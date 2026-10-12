import http.client
import json
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class AgentWorker:
    """Manages agent turn execution via mock policies or HTTP llama-server calls."""

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
            self._conn = http.client.HTTPConnection("127.0.0.1", self.server_port, timeout=15)
        return self._conn

    def query(
        self,
        prompt: str,
        valid_affordances: List[str],
        arm: str,
        held_leases: Set[str],
        target_resource: Optional[str] = None,
    ) -> Tuple[str, float, int]:
        """Queries the agent policy or SLM endpoint.
        
        Returns:
            Tuple[action_text, latency_ms, token_count]
        """
        if self.is_mock:
            return self._query_mock(valid_affordances, arm, held_leases, target_resource)
        return self._query_slm(prompt, valid_affordances)

    def _query_mock(
        self,
        valid_affordances: List[str],
        arm: str,
        held_leases: Set[str],
        target_resource: Optional[str] = None,
    ) -> Tuple[str, float, int]:
        """Deterministic policy simulation for Track 1."""
        latency_ms = 1.5
        token_count = max(10, len(valid_affordances) * 8)

        if arm == "arm1":
            # Arm 1: Naive uncoordinated policy, acts directly without lease
            act_affs = [a for a in valid_affordances if target_resource and f"ACT {target_resource}" in a]
            if not act_affs:
                act_affs = [a for a in valid_affordances if "ACT" in a]
            chosen = act_affs[0] if act_affs else valid_affordances[0]
            return chosen, latency_ms, token_count

        if arm == "arm2":
            # Arm 2: Unpruned gossip control, acquires leases greedily but gets stuck in contention
            lease_affs = [a for a in valid_affordances if "LEASE" in a]
            if lease_affs and not held_leases:
                return lease_affs[0], latency_ms, token_count
            act_affs = [a for a in valid_affordances if "ACT" in a]
            if act_affs and held_leases:
                return act_affs[0], latency_ms, token_count
            return "ACTION: WAIT", latency_ms, token_count

        # Arm 3: Consensus Hub Policy
        # 1. If holding target resource, perform ACT, then RELEASE
        if target_resource and target_resource in held_leases:
            act_for_target = [a for a in valid_affordances if f"ACT {target_resource}" in a]
            if act_for_target:
                return act_for_target[0], latency_ms, token_count
            rel_for_target = [a for a in valid_affordances if f"RELEASE {target_resource}" in a]
            if rel_for_target:
                return rel_for_target[0], latency_ms, token_count

        # 2. If target resource available to LEASE, acquire it
        if target_resource:
            lease_target = f"ACTION: LEASE {target_resource}"
            if lease_target in valid_affordances:
                return lease_target, latency_ms, token_count

        # 3. Otherwise, pick any valid work or WAIT
        for aff in valid_affordances:
            if "ACT" in aff:
                return aff, latency_ms, token_count
        return "ACTION: WAIT", latency_ms, token_count

    def _query_slm(self, prompt: str, valid_affordances: List[str]) -> Tuple[str, float, int]:
        """Queries local llama-server instance via persistent HTTP connection."""
        # Apply model-specific template formatting
        is_llama = "llama" in self.model_name.lower()
        if is_llama:
            formatted_prompt = (
                f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
                f"Respond ONLY with the single action line starting with ACTION:. No thoughts, no explanations.<|eot_id|>"
                f"<|start_header_id|>user<|end_header_id|>\n\n"
                f"{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\nACTION:"
            )
            stop_tokens = ["<|eot_id|>", "\n", "User:"]
        else:
            # Qwen / ChatML format
            formatted_prompt = (
                f"<|im_start|>system\nRespond ONLY with the single action line starting with ACTION:. No thoughts, no explanations.<|im_end|>\n"
                f"<|im_start|>user\n{prompt}\n<|im_end|>\n<|im_start|>assistant\nACTION:"
            )
            stop_tokens = ["<|im_end|>", "\n", "User:"]

        payload = {
            "prompt": formatted_prompt,
            "temperature": 0.0,
            "n_predict": 16,
            "stop": stop_tokens,
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")

        t0 = time.perf_counter()
        try:
            conn = self._get_conn()
            conn.request("POST", "/completion", data, {"Content-Type": "application/json"})
            resp = conn.getresponse()
            result = json.loads(resp.read().decode("utf-8"))
            latency_ms = (time.perf_counter() - t0) * 1000.0
            content = "ACTION:" + result.get("content", "").strip()
            tokens_eval = result.get("tokens_evaluated", len(prompt.split()))

            # Extract ACTION: ...
            match = re.search(
                r"ACTION:\s*([A-Za-z0-9_\-\.]+)(?:\s+([A-Za-z0-9_\-\.]+))?(?:\s+([A-Za-z0-9_\-\.]+))?",
                content,
            )
            if match:
                action_text = match.group(0).strip()
            else:
                action_text = "ACTION: WAIT"

            # If action not in valid affordances, fall back to best match
            if action_text not in valid_affordances:
                matching = [a for a in valid_affordances if action_text.split()[-1] in a]
                if matching:
                    action_text = matching[0]

            return action_text, latency_ms, tokens_eval

        except Exception as e:
            # Fallback if server call fails or times out
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None
            latency_ms = (time.perf_counter() - t0) * 1000.0
            fallback = valid_affordances[0] if valid_affordances else "ACTION: WAIT"
            return fallback, latency_ms, len(prompt.split())
