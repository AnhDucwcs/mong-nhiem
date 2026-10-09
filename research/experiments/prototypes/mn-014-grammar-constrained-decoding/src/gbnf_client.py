"""Client wrapper for llama-server supporting GBNF grammar-constrained decoding."""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


class LlamaServerClient:
    """HTTP client interface to llama-server with native GBNF grammar parameter support."""

    def __init__(self, host: str = "127.0.0.1", port: int = 18504, grammar_path: Optional[Path] = None):
        self.host = host
        self.port = port
        self.grammar_content: Optional[str] = None
        if grammar_path and grammar_path.exists():
            with open(grammar_path, "r", encoding="utf-8") as f:
                self.grammar_content = f.read().strip()

    def check_health(self) -> bool:
        url = f"http://{self.host}:{self.port}/health"
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def complete(
        self,
        prompt: str,
        max_tokens: int = 64,
        use_grammar: bool = True,
        stop_sequences: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Execute completion request with optional GBNF grammar constraint."""
        if stop_sequences is not None:
            stops = stop_sequences
        elif use_grammar:
            stops = ["\n", "\n\n", "User:", "Task:", "Directive:"]
        else:
            stops = ["\n\n", "User:", "Task:", "Directive:"]

        payload_dict: Dict[str, Any] = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": 0.0,
            "stop": stops,
        }

        if use_grammar and self.grammar_content:
            payload_dict["grammar"] = self.grammar_content

        payload_bytes = json.dumps(payload_dict).encode("utf-8")
        req = urllib.request.Request(url, data=payload_bytes, headers={"Content-Type": "application/json"})

        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        content = data.get("content", "").strip()
        tokens_predicted = data.get("tokens_predicted", 0)

        return {
            "content": content,
            "tokens_predicted": tokens_predicted,
            "tokens_evaluated": data.get("tokens_evaluated", 0),
            "latency_ms": elapsed_ms,
            "used_grammar": bool(use_grammar and self.grammar_content),
        }
