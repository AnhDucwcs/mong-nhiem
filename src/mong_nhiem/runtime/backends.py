"""Pluggable Inference Backends for Mộng Nhiễm.

Completely decouples the Host Cognitive Kernel from specific model architectures or execution providers.
Supports:
- MockBackend: Offline rule-based testing & Track 1 simulation (0 dependencies, 0ms latency).
- LlamaServerBackend: Remote/local llama-server.exe over HTTP with GBNF & Slot Cache affinity.
- SubprocessLlamaBackend: Autonomous managed lifecycle; automatically spawns & terminates llama-server.exe from a .gguf file.
- OpenAICompatBackend: Standard OpenAI/Ollama/vLLM HTTP endpoint (/v1/chat/completions).

100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from collections.abc import Callable

from mong_nhiem.runtime.slot_cache import SlotCacheManager, SlotExecutionMode


def find_free_port() -> int:
    """Asks the operating system for an available ephemeral port to prevent collisions."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return int(s.getsockname()[1])


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Checks if a network port is currently occupied by another process."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex((host, port)) == 0


class BaseInferenceBackend(ABC):
    """Abstract contract for all reasoning engine backends."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        grammar: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 64,
        stop: list[str] | None = None,
        session_id: str | None = None,
    ) -> str:
        """Emits raw text completion for a given prompt and optional grammar."""

    def flush(self, session_id: str | None = None) -> None:
        """Flushes KV cache or state for a session if supported."""

    def close(self) -> None:
        """Releases any active background processes or network connections."""


class MockBackend(BaseInferenceBackend):
    """Deterministic, zero-latency in-memory backend for offline testing and CI/CD."""

    def __init__(
        self,
        default_response: str = 'ACTION: NOMINAL_STEP\nCOMMUNICATE [INFORM]: "System operating normally."',
        response_map: dict[str, str] | None = None,
        response_fn: Callable[[str], str] | None = None,
    ) -> None:
        self.default_response = default_response
        self.response_map = dict(response_map or {})
        self.response_fn = response_fn
        self.call_history: list[str] = []

    def generate(
        self,
        prompt: str,
        grammar: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 64,
        stop: list[str] | None = None,
        session_id: str | None = None,
    ) -> str:
        self.call_history.append(prompt)
        if self.response_fn is not None:
            return self.response_fn(prompt)

        for trigger, resp in self.response_map.items():
            if trigger in prompt:
                return resp

        return self.default_response


class LlamaServerBackend(BaseInferenceBackend):
    """Connects to a running llama-server.exe instance with Slot Cache governance."""

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:8080",
        slot_id: int = 0,
        cache_prompt: bool = True,
        timeout_seconds: float = 15.0,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.slot_id = slot_id
        self.cache_prompt = cache_prompt
        self.timeout = timeout_seconds

        mode = SlotExecutionMode.AFFINITY if cache_prompt else SlotExecutionMode.ISOLATION
        self.slot_mgr = SlotCacheManager(
            base_url=self.endpoint,
            total_slots=max(1, slot_id + 1),
            mode=mode,
            timeout_seconds=timeout_seconds,
        )

    def generate(
        self,
        prompt: str,
        grammar: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 64,
        stop: list[str] | None = None,
        session_id: str | None = None,
    ) -> str:
        s_id = session_id or "default_session"
        url = f"{self.endpoint}/completion"

        payload = self.slot_mgr.build_request_payload(
            session_id=s_id,
            static_prefix="",  # Will use full prompt
            dynamic_suffix=prompt,
            grammar=grammar,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
        payload["id_slot"] = self.slot_id
        payload["cache_prompt"] = self.cache_prompt

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            return str(resp_data.get("content", ""))

    def flush(self, session_id: str | None = None) -> None:
        self.slot_mgr.flush_slot(self.slot_id)


class SubprocessLlamaBackend(LlamaServerBackend):
    """Manages an autonomous local llama-server.exe child process from a .gguf file.

    Starts llama-server on an available port, waits for /health, and terminates cleanly on close.
    """

    def __init__(
        self,
        weights_path: str,
        server_binary: str = "llama-server.exe",
        port: int = 18505,
        n_gpu_layers: int = 99,
        ctx_size: int = 2048,
        threads: int = 4,
        cache_prompt: bool = True,
        startup_timeout: float = 30.0,
    ) -> None:
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Model weights file not found: {weights_path}")

        self.weights_path = os.path.abspath(weights_path)
        self.server_binary = server_binary

        # Auto-Port Hunting: if port=0 or port is currently occupied by DB/server, auto-bind free port
        if port == 0 or is_port_in_use(port):
            allocated_port = find_free_port()
        else:
            allocated_port = port

        self.port = allocated_port
        self.process: subprocess.Popen | None = None

        endpoint = f"http://127.0.0.1:{allocated_port}"
        self._spawn_process(n_gpu_layers, ctx_size, threads, startup_timeout)

        super().__init__(
            endpoint=endpoint,
            slot_id=0,
            cache_prompt=cache_prompt,
            timeout_seconds=15.0,
        )

    def _spawn_process(
        self,
        n_gpu_layers: int,
        ctx_size: int,
        threads: int,
        timeout: float,
    ) -> None:
        """Spawns the llama-server background process and polls health."""
        cmd = [
            self.server_binary,
            "-m", self.weights_path,
            "--port", str(self.port),
            "-ngl", str(n_gpu_layers),
            "-c", str(ctx_size),
            "-t", str(threads),
            "--host", "127.0.0.1",
        ]

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        health_url = f"http://127.0.0.1:{self.port}/health"
        deadline = time.time() + timeout
        ready = False

        while time.time() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(
                    f"llama-server exited prematurely with code {self.process.returncode}"
                )
            try:
                req = urllib.request.Request(health_url)
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status == 200:
                        ready = True
                        break
            except (urllib.error.URLError, OSError, TimeoutError):
                time.sleep(0.5)

        if not ready:
            self.close()
            raise TimeoutError(f"llama-server failed to respond within {timeout}s")

    def close(self) -> None:
        """Terminates the spawned llama-server process cleanly."""
        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=3.0)
            except (subprocess.TimeoutExpired, OSError):
                self.process.kill()
            finally:
                self.process = None


class OpenAICompatBackend(BaseInferenceBackend):
    """Generic backend for Ollama, vLLM, LM Studio, or OpenAI-compatible endpoints."""

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:11434/v1",
        model_name: str = "default",
        api_key: str | None = None,
        timeout_seconds: float = 15.0,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key
        self.timeout = timeout_seconds

    def generate(
        self,
        prompt: str,
        grammar: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 64,
        stop: list[str] | None = None,
        session_id: str | None = None,
    ) -> str:
        url = f"{self.endpoint}/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": stop or [],
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                return str(choices[0].get("message", {}).get("content", ""))
            return ""
