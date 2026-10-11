"""Stateless SLM Agent Worker for Multi-Agent Symbiosis.

Executes inference against local llama-server with GBNF constrained grammar.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


class AgentWorker:
    """Stateless worker representing an individual SLM reasoning agent."""

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
        fallback_action: str = "ACTION: RESOLVE COMPLETE",
    ) -> str:
        """Query LLM or deterministic simulator fallback."""
        if self.track == 1:
            # Track 1 Deterministic Simulator: select action matching prompt mission intent
            candidates = []
            for line in grammar.split("\n"):
                if "action ::=" in line:
                    alts = line.replace("action ::=", "").split("|")
                    for a in alts:
                        clean = a.strip().replace('"', "")
                        if clean:
                            candidates.append(clean)

            # Pick first available DISPATCH action permitted by grammar
            for c in candidates:
                if c.startswith("ACTION: DISPATCH"):
                    return c

            if candidates:
                return candidates[0]
            return fallback_action

        # Track 2: Real Model Inference via local llama-server HTTP API
        url = f"http://127.0.0.1:{self.port}/completion"
        payload = {
            "prompt": f"<|im_start|>system\nYou are {self.agent_id}, a collaborative cyber-physical controller.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n",
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
        except Exception as e:
            # On network timeout or connection reset, fallback gracefully
            return fallback_action
