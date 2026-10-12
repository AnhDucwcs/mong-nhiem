"""Stateless SLM Agent Worker for Federated Causal Graph Synthesis (MN-021).

Executes inference against local llama-server with GBNF constrained grammar or deterministic simulator.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


class AgentWorker:
    """Stateless worker representing an individual SLM reasoning agent in MN-021."""

    def __init__(
        self,
        agent_id: str,
        port: int = 18502,
        model_id: str = "Qwen3.5-2B-Q4_K_M",
        track: int = 1,
    ):
        self.agent_id = agent_id
        self.port = port
        self.model_id = model_id
        self.track = track

    def query_action(
        self,
        prompt: str,
        grammar: str,
        preferred_target: Optional[str] = None,
        fallback_action: str = "ACTION: RESOLVE",
    ) -> str:
        """Query LLM (Track 2) or deterministic simulator fallback (Track 1)."""
        if self.track == 1:
            return self._simulate_action(grammar, preferred_target, fallback_action)

        # Track 2: Real Model Inference via local llama-server HTTP API
        url = f"http://127.0.0.1:{self.port}/completion"
        payload = {
            "prompt": f"<|im_start|>system\nYou are {self.agent_id}, an autonomous cyber-physical agent in a federated environment.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n",
            "temperature": 0.0,
            "grammar": grammar,
            "n_predict": 32,
            "stop": ["\n", "<|im_end|>"],
            "cache_prompt": True,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data.get("content", "").strip()
                if content.startswith("ACTION:"):
                    return content
                return f"ACTION: {content}"
        except Exception:
            # Network timeout, offline server, or connection reset fallback
            return self._simulate_action(grammar, preferred_target, fallback_action)

    def _simulate_action(
        self,
        grammar: str,
        preferred_target: Optional[str],
        fallback_action: str,
    ) -> str:
        """Extract valid actions from grammar and select the optimal deterministic action."""
        candidates: List[str] = []
        for line in grammar.split("\n"):
            line = line.strip()
            if "::=" in line and "action-" in line:
                # e.g. action-dispatch ::= "ACTION: DISPATCH " ("e1" | "e2") "\n"
                # or action-resolve ::= "ACTION: RESOLVE\n"
                prefix_part = ""
                if '"ACTION: ' in line:
                    start_idx = line.find('"ACTION: ') + 1
                    end_idx = line.find('"', start_idx)
                    prefix_part = line[start_idx:end_idx]

                if "(" in line and ")" in line:
                    targets_part = line[line.find("(") + 1 : line.find(")")]
                    for t in targets_part.split("|"):
                        target_clean = t.strip().replace('"', "")
                        if target_clean:
                            candidates.append(f"{prefix_part}{target_clean}".strip())
                elif prefix_part:
                    clean_prefix = prefix_part.replace("\\n", "").strip()
                    candidates.append(clean_prefix)

        if not candidates:
            return fallback_action

        # Priority 1: CROSS_INSPECT (resolving contested epistemic discrepancies)
        for c in candidates:
            if c.startswith("ACTION: CROSS_INSPECT"):
                if preferred_target and preferred_target in c:
                    return c
                return c

        # Priority 2: Preferred action / target match
        if preferred_target:
            for c in candidates:
                if c == preferred_target:
                    return c
            for c in candidates:
                if preferred_target in c:
                    return c

        # Priority 3: Any DISPATCH
        for c in candidates:
            if c.startswith("ACTION: DISPATCH"):
                return c

        # Priority 4: Any PROBE
        for c in candidates:
            if c.startswith("ACTION: PROBE"):
                return c

        # Priority 5: RESOLVE
        for c in candidates:
            if c == "ACTION: RESOLVE":
                return c

        return candidates[0]
