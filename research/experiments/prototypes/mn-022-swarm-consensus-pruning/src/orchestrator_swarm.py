"""Swarm Orchestrator coordinating M = 5 agents, async transport, leases, and consensus pruning."""
from __future__ import annotations

import copy
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from .agent_worker import AgentWorker
from .async_world_engine import AsyncWorldEngine, SwarmScenario
from .autodream_swarm import AutoDreamSwarm
from .byzantine_filter import ByzantineFilter
from .consensus_pruner import ConsensusPruner
from .network_transport import NetworkTransport
from .swarm_concurrency_arbiter import SwarmConcurrencyArbiter


class SwarmOrchestrator:
    """Coordinates multi-agent swarm microworld episodes under Arms 1, 2, and 3."""

    def __init__(
        self,
        scenario: SwarmScenario,
        arm: str,  # "arm1", "arm2", "arm3"
        min_latency: int = 0,
        max_latency: int = 5,
        workers: Optional[Dict[str, AgentWorker]] = None,
        seed: int = 42,
    ) -> None:
        self.scenario = scenario
        self.arm = arm
        self.agent_ids = [f"agent_{i+1}" for i in range(scenario.num_agents)]
        self.engine = AsyncWorldEngine(scenario)
        self.transport = NetworkTransport(
            min_latency=min_latency,
            max_latency=max_latency,
            out_of_order_prob=0.1,
            seed=seed,
        )
        self.arbiter = SwarmConcurrencyArbiter(default_ttl=4)
        for res in scenario.resources:
            self.arbiter.register_resource(res)

        self.pruner = ConsensusPruner(self.agent_ids, frontier_window=4)
        self.byzantine_filter = ByzantineFilter(set(scenario.resources))
        self.autodream = AutoDreamSwarm(token_ceiling=512)
        self.workers = workers or {
            aid: AgentWorker(aid, scenario.agent_goals.get(aid, ""), is_mock=True)
            for aid in self.agent_ids
        }
        self.raw_gossip_history: List[Dict[str, Any]] = []
        self.race_collisions: int = 0

    def run_episode(self) -> Dict[str, Any]:
        """Executes full multi-agent simulation episode."""
        max_ticks = self.scenario.max_ticks
        tick_latencies: List[float] = []
        tick_tokens: List[int] = []
        episode_success = False

        for t in range(max_ticks):
            # 1. Host cleanup of expired leases
            if self.arm in ("arm2", "arm3"):
                self.arbiter.tick_cleanup(t)

            # 2. Agent Turn Loop: each agent polls state, builds prompt, decides action
            agent_actions: Dict[str, str] = {}
            prepared_queries: List[Tuple] = []
            for aid in self.agent_ids:
                held_leases = {
                    res for res, l in self.arbiter.leases.items()
                    if l.holder_id == aid and l.state == "HELD"
                }
                valid_affordances = self.engine.get_valid_affordances(
                    aid,
                    held_leases,
                    allow_unleased_act=(self.arm == "arm1"),
                )
                resource_states = self.engine.get_resource_states(self.arbiter.get_lease_summary())

                # Frontier selection
                if self.arm == "arm2":
                    prompt, est_tok = self.autodream.build_prompt(
                        domain_name=self.scenario.domain,
                        current_tick=t,
                        agent_id=aid,
                        assigned_goal=self.scenario.agent_goals.get(aid, ""),
                        resource_states=resource_states,
                        frontier_nodes=[],
                        held_leases=held_leases,
                        valid_affordances=valid_affordances,
                        unpruned_gossip=self.raw_gossip_history,
                    )
                elif self.arm == "arm3":
                    active_frontier = self.pruner.prune_frontier(t)
                    prompt, est_tok = self.autodream.build_prompt(
                        domain_name=self.scenario.domain,
                        current_tick=t,
                        agent_id=aid,
                        assigned_goal=self.scenario.agent_goals.get(aid, ""),
                        resource_states=resource_states,
                        frontier_nodes=active_frontier,
                        held_leases=held_leases,
                        valid_affordances=valid_affordances,
                        unpruned_gossip=None,
                    )
                else:
                    # Arm 1: Flat baseline, no frontier or leases
                    prompt, est_tok = self.autodream.build_prompt(
                        domain_name=self.scenario.domain,
                        current_tick=t,
                        agent_id=aid,
                        assigned_goal=self.scenario.agent_goals.get(aid, ""),
                        resource_states=resource_states,
                        frontier_nodes=[],
                        held_leases=set(),
                        valid_affordances=valid_affordances,
                        unpruned_gossip=None,
                    )

                target_res = self.scenario.resources[self.agent_ids.index(aid) % len(self.scenario.resources)]
                prepared_queries.append((aid, self.workers[aid], prompt, valid_affordances, held_leases, target_res, est_tok))

            # Query all swarm agents concurrently across available slots
            from concurrent.futures import ThreadPoolExecutor

            def _execute_worker_query(item):
                aid, worker, prompt, valid_affs, held_l, tgt_r, est_t = item
                raw_act, lat_ms, tok_c = worker.query(
                    prompt=prompt,
                    valid_affordances=valid_affs,
                    arm=self.arm,
                    held_leases=held_l,
                    target_resource=tgt_r,
                )
                return aid, raw_act, lat_ms, max(est_t, tok_c), tgt_r

            with ThreadPoolExecutor(max_workers=min(5, len(self.agent_ids))) as executor:
                query_results = list(executor.map(_execute_worker_query, prepared_queries))

            for aid, raw_act, lat_ms, tok_count, target_res in query_results:
                tick_latencies.append(lat_ms)
                tick_tokens.append(tok_count)

                # Send action packet across async network transport
                self.transport.send(
                    sender_id=aid,
                    recipient_id="HOST",
                    payload={"action": raw_act, "target_res": target_res},
                    current_tick=t,
                )

            # 3. Host receives delivered packets for this tick
            delivered_pkts = self.transport.poll(t, recipient_id="HOST")
            active_actors_on_resource: Dict[str, List[str]] = {}

            for pkt in delivered_pkts:
                aid = pkt.sender_id
                raw_act = pkt.payload.get("action", "ACTION: WAIT")
                held_leases = {
                    res for res, l in self.arbiter.leases.items()
                    if l.holder_id == aid and l.state == "HELD"
                }

                # Admission filtering
                require_lease = (self.arm != "arm1")
                f_res = self.byzantine_filter.validate_action(raw_act, aid, held_leases, require_lease=require_lease)
                if not f_res.is_valid:
                    continue

                act_type = f_res.action_type
                target = f_res.target

                if self.arm == "arm1":
                    # Arm 1: No arbiter! Direct uncoordinated concurrent mutations cause race collisions
                    if act_type == "ACT" and target:
                        active_actors_on_resource.setdefault(target, []).append(aid)
                        if len(active_actors_on_resource[target]) > 1:
                            self.race_collisions += 1  # Race collision detected!
                        self.engine.step_action(aid, act_type, target, f_res.param)

                elif self.arm == "arm2":
                    # Arm 2: Unpruned gossip, acquires leases greedily
                    if act_type == "LEASE" and target:
                        ok, status = self.arbiter.acquire(target, aid, t)
                        self.raw_gossip_history.append({"tick": t, "agent_id": aid, "action": f"LEASE {target} ({status})"})
                    elif act_type == "ACT" and target:
                        self.engine.step_action(aid, act_type, target, f_res.param)
                        self.raw_gossip_history.append({"tick": t, "agent_id": aid, "action": f"ACT {target}"})
                    elif act_type == "RELEASE" and target:
                        self.arbiter.release(target, aid)
                        self.raw_gossip_history.append({"tick": t, "agent_id": aid, "action": f"RELEASE {target}"})

                elif self.arm == "arm3":
                    # Arm 3: Consensus Hub & Pruned DAG
                    if act_type == "LEASE" and target:
                        ok, status = self.arbiter.acquire(target, aid, t)
                        self.pruner.record_event(
                            event_id=f"evt-{t}-{aid}-lease",
                            tick=t,
                            agent_id=aid,
                            action_type="LEASE",
                            target=target,
                            payload={"status": status},
                            status="COMMITTED" if ok else "REJECTED_CONFLICT",
                        )
                    elif act_type == "ACT" and target:
                        self.engine.step_action(aid, act_type, target, f_res.param)
                        self.pruner.record_event(
                            event_id=f"evt-{t}-{aid}-act",
                            tick=t,
                            agent_id=aid,
                            action_type="ACT",
                            target=target,
                            payload={"result": "OK"},
                            status="COMMITTED",
                        )
                    elif act_type == "RELEASE" and target:
                        self.arbiter.release(target, aid)
                        self.pruner.record_event(
                            event_id=f"evt-{t}-{aid}-release",
                            tick=t,
                            agent_id=aid,
                            action_type="RELEASE",
                            target=target,
                            payload={},
                            status="COMMITTED",
                        )

            # 4. Check early resolution
            if self.engine.is_resolved():
                episode_success = True
                break

            self.engine.advance_tick()

        # Final check if resolved at max ticks
        if not episode_success and self.engine.is_resolved():
            episode_success = True

        comp_metrics = self.pruner.get_compaction_metrics()
        compaction = comp_metrics["compaction_ratio"] if self.arm == "arm3" else 0.0

        return {
            "scenario_id": self.scenario.scenario_id,
            "domain": self.scenario.domain,
            "arm": self.arm,
            "success": episode_success,
            "ticks_used": min(max_ticks, self.engine.current_tick + 1),
            "physical_breaches": self.engine.physical_breaches,
            "race_collisions": self.race_collisions,
            "max_tokens": max(tick_tokens) if tick_tokens else 0,
            "mean_tokens": round(sum(tick_tokens) / len(tick_tokens), 2) if tick_tokens else 0,
            "mean_latency_ms": round(sum(tick_latencies) / len(tick_latencies), 2) if tick_latencies else 0,
            "compaction_ratio": compaction,
        }
