"""Agent worker querying deterministic policies (Track 1) or real open-weights SLM (Track 2) for MN-024."""

from __future__ import annotations

import http.client
import json
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class AgentWorker:
    """Manages agent turn execution via mock deterministic policies or HTTP llama-server calls."""

    def __init__(
        self,
        agent_id: str,
        assigned_goal: str,
        is_mock: bool = True,
        server_port: int = 18502,
        model_name: str = "Qwen3.5-2B-Q4_K_M",
    ) -> None:
        self.agent_id = agent_id
        self.assigned_goal = assigned_goal
        self.is_mock = is_mock
        self.server_port = server_port
        self.model_name = model_name
        self._conn: Optional[http.client.HTTPConnection] = None

    def _get_conn(self) -> http.client.HTTPConnection:
        if self._conn is None:
            self._conn = http.client.HTTPConnection("127.0.0.1", self.server_port, timeout=20)
        return self._conn

    def query(
        self,
        prompt: str,
        valid_affordances: List[str],
        arm: str,
        held_leases: Set[str],
        known_secret: Optional[str] = None,
        target_resource: Optional[str] = None,
    ) -> Tuple[str, float, int]:
        """Queries policy or SLM endpoint.

        Returns:
            Tuple[action_text, latency_ms, token_count]
        """
        if self.is_mock:
            return self._query_mock(valid_affordances, arm, held_leases, known_secret, target_resource)
        return self._query_slm(prompt, valid_affordances)

    def _query_mock(
        self,
        valid_affordances: List[str],
        arm: str,
        held_leases: Set[str],
        known_secret: Optional[str],
        target_resource: Optional[str],
    ) -> Tuple[str, float, int]:
        """Deterministic policy simulation for Track 1."""
        latency_ms = 1.2
        est_tokens = max(20, len(valid_affordances) * 8)

        if not valid_affordances:
            return "ACTION: WAIT", latency_ms, est_tokens

        if arm == "arm1":
            # Naive uncoordinated, immediately acts on target
            act_affs = [a for a in valid_affordances if "ACT" in a or "ENGAGE" in a]
            if act_affs:
                return act_affs[0], latency_ms, est_tokens
            return valid_affordances[0], latency_ms, est_tokens

        if arm == "arm2":
            # Unpruned control, leases greedily
            if target_resource and target_resource not in held_leases:
                lease_affs = [a for a in valid_affordances if a == f"ACTION: LEASE {target_resource}"]
                if lease_affs:
                    return lease_affs[0], latency_ms, est_tokens
            act_affs = [a for a in valid_affordances if "ACT" in a or "ENGAGE" in a]
            if act_affs:
                return act_affs[0], latency_ms, est_tokens
            return valid_affordances[0], latency_ms, est_tokens

        # Arm 3: Coordinated epistemic policy
        if target_resource and target_resource not in held_leases:
            lease_affs = [a for a in valid_affordances if a == f"ACTION: LEASE {target_resource}"]
            if lease_affs:
                return lease_affs[0], latency_ms, est_tokens

        if target_resource and target_resource in held_leases:
            if known_secret:
                secret_affs = [a for a in valid_affordances if known_secret in a]
                if secret_affs:
                    return secret_affs[0], latency_ms, est_tokens
            act_affs = [a for a in valid_affordances if "ACT" in a or "ENGAGE" in a or "MAINTAIN" in a]
            if act_affs:
                return act_affs[0], latency_ms, est_tokens

        return valid_affordances[0], latency_ms, est_tokens

    def _query_slm(self, prompt: str, valid_affordances: List[str]) -> Tuple[str, float, int]:
        """Real inference call to local llama-server using ChatML formatting."""
        formatted_prompt = (
            f"<|im_start|>system\n"
            f"You are {self.agent_id}. Goal: {self.assigned_goal}\n"
            f"Select exactly ONE action from the valid affordances below.\n"
            f"Respond ONLY with ACTION: <verb> <args>. No explanations.\n"
            f"<|im_end|>\n"
            f"<|im_start|>user\n"
            f"{prompt}\n"
            f"Valid Affordances:\n"
            + "\n".join([f"- {a}" for a in valid_affordances]) + "\n"
            f"<|im_end|>\n"
            f"<|im_start|>assistant\nACTION:"
        )

        start_t = time.perf_counter()
        payload = {
            "prompt": formatted_prompt,
            "temperature": 0.0,
            "n_predict": 16,
            "stop": ["\n", "<|im_end|>", "User:", "Tick:"],
        }

        try:
            conn = self._get_conn()
            conn.request("POST", "/completion", json.dumps(payload), {"Content-Type": "application/json"})
            res = conn.getresponse()
            data = json.loads(res.read().decode("utf-8"))
            lat_ms = (time.perf_counter() - start_t) * 1000.0
            raw_text = "ACTION: " + data.get("content", "").strip()
            tokens_eval = data.get("tokens_evaluated", len(formatted_prompt.split()) + 10)

            # Match valid affordances
            chosen_action = "ACTION: WAIT"
            for aff in valid_affordances:
                if aff.lower() in raw_text.lower():
                    chosen_action = aff
                    break

            if chosen_action == "ACTION: WAIT" and valid_affordances:
                for aff in valid_affordances:
                    parts = raw_text.split()
                    if len(parts) > 1 and any(p.lower() in aff.lower() for p in parts[1:]):
                        chosen_action = aff
                        break

            return chosen_action, lat_ms, tokens_eval

        except Exception:
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None
            lat_ms = (time.perf_counter() - start_t) * 1000.0
            fallback = valid_affordances[0] if valid_affordances else "ACTION: WAIT"
            return fallback, lat_ms, len(formatted_prompt.split()) + 10
