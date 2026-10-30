"""Cognitive Bridge Server for Mộng Nhiễm Living World.

Zero external dependencies. 100% Python Standard Library.
Embeds MongNhiemKernel to arbitrate state invariants, SLM reasoning,
spatial trajectory lookahead, and human supervisory preemption.
Serves static Canvas dashboard and REST API endpoints on port 8765.
"""

from __future__ import annotations

import http.server
import json
import math
import os
import socketserver
import sys
import webbrowser
from pathlib import Path
from typing import Any

# Ensure src/ is on sys.path for direct module import
DEMO_DIR = Path(__file__).resolve().parent
ROOT_DIR = DEMO_DIR.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mong_nhiem.kernel import MongNhiemKernel, StepResult
from mong_nhiem.runtime.backends import MockBackend


PORT = int(os.environ.get("DEMO_PORT", "8765"))
STATIC_DIR = DEMO_DIR / "static"
SCHEMA_PATH = DEMO_DIR / "schema" / "living_world.json"

_KERNEL_INSTANCE: MongNhiemKernel | None = None


def living_world_slm_reasoning_fn(prompt: str) -> str:
    """Domain-grounded SLM reasoning engine for Mộng Nhiễm Living World.

    Emits formal bimodal outputs conformant with living_world.json action verbs.
    """
    stimulus = ""
    for line in prompt.splitlines():
        if line.startswith("Stimulus:"):
            stimulus = line.replace("Stimulus:", "").strip()
            break
    s_lower = stimulus.lower()

    # 1. Epistemic Surprise Spike (Belief 80u != GT 0u)
    if "surprise spike" in s_lower or "bất đối xứng" in s_lower or "delta" in s_lower:
        return (
            'ACTION: MOVE_TO target=bush_west x=260 y=230\n'
            'COMMUNICATE [INFORM]: "Bất đối xứng nhận thức: Bụi Bắc đã cạn (0u). Chuyển hướng toàn bầy sang Bụi Tây [260, 230]."'
        )

    # 2. Succession (New Alpha Scout assumption)
    if "succession" in s_lower or "kế thừa" in s_lower:
        return (
            'ACTION: MOVE_TO target=burrow x=320 y=520\n'
            'COMMUNICATE [INFORM]: "Tân Alpha Scout tiếp quản quyền điều hướng. Tái tập hợp bầy đàn quanh Hang Trú Ẩn."'
        )

    # 3. Total Famine (All food depleted)
    if "total famine" in s_lower or "all food depleted" in s_lower or "nạn đói" in s_lower:
        return (
            'ACTION: SHELTER_BURROW target=burrow x=320 y=520\n'
            'COMMUNICATE [INFORM]: "Nạn đói diện rộng: Tất cả nguồn lương thực đã cạn. Toàn bầy vào hang ngủ đông tiết kiệm năng lượng."'
        )

    # 4. Predator proximity / ambush
    if "predator ambush" in s_lower or "sói phục kích" in s_lower or "sói vồ" in s_lower:
        return (
            'ACTION: EMERGENCY_BURROW_EVAC target=burrow x=320 y=520\n'
            'COMMUNICATE [INFORM:ALERT]: "Phát hiện thú săn trong cự ly nguy hiểm. Toàn bầy rút lui khẩn cấp vào Hang Trú Ẩn."'
        )

    # 5. Starvation Alert / Critical Hunger
    if "starvation" in s_lower or "hunger" in s_lower or "đói" in s_lower:
        if "bush_north_amount: 0" in prompt.lower() or "cạn" in s_lower or "depleted" in s_lower:
            return (
                'ACTION: FORAGE_BERRY target=bush_west x=260 y=230\n'
                'COMMUNICATE [INFORM]: "Báo động đói: Bụi Bắc đã cạn. Chỉ thị bầy đàn di chuyển sang Bụi Tây [260, 230] kiếm ăn khẩn cấp."'
            )
        return (
            'ACTION: FORAGE_BERRY target=bush_north x=580 y=140\n'
            'COMMUNICATE [INFORM]: "Báo động đói: Bầy đàn di chuyển đến Bụi Dâu Bắc [580, 140] bổ sung calo."'
        )

    # 6. Default Periodic Strategic Routine / Nominal
    return (
        'ACTION: REST_COLONY target=burrow x=320 y=520\n'
        'COMMUNICATE [INFORM]: "Chỉ thị danh định: Bầy đàn duy trì trật tự và tuần tra an toàn."'
    )


def _setup_kernel_instance(kernel: MongNhiemKernel) -> MongNhiemKernel:
    """Configures contextual domain reasoning for MockBackend in Living World demo."""
    if isinstance(kernel.backend, MockBackend):
        kernel.backend.response_fn = living_world_slm_reasoning_fn
    return kernel


def get_kernel() -> MongNhiemKernel:
    """Returns or lazily initializes the singleton MongNhiemKernel instance."""
    global _KERNEL_INSTANCE
    if _KERNEL_INSTANCE is None:
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Living World Schema not found at {SCHEMA_PATH}")
        _KERNEL_INSTANCE = MongNhiemKernel.from_schema(str(SCHEMA_PATH))
        _setup_kernel_instance(_KERNEL_INSTANCE)
    return _KERNEL_INSTANCE


def reset_kernel() -> MongNhiemKernel:
    """Re-initializes kernel from schema, resetting all runtime state."""
    global _KERNEL_INSTANCE
    _KERNEL_INSTANCE = MongNhiemKernel.from_schema(str(SCHEMA_PATH))
    _setup_kernel_instance(_KERNEL_INSTANCE)
    return _KERNEL_INSTANCE


def evaluate_spatial_lookahead(
    waypoints: list[list[float]],
    wolf_pos: list[float],
    wolf_vel: list[float] | None = None,
    scout_start: list[float] | None = None,
    safety_dist: float = 35.0,
    samples_per_step: int = 10,
) -> dict[str, Any]:
    """Evaluates 4-step spatial trajectory lookahead horizon (4.0s).

    Calculates minimum Euclidean distance between projected Scout polyline path
    and Wolf dynamic position over tau in [0.0s, 4.0s].
    """
    if not waypoints:
        return {
            "approved": True,
            "min_distance": 999.0,
            "safety_dist": safety_dist,
            "reason": "APPROVED: No waypoints submitted.",
        }

    p0 = scout_start if scout_start and len(scout_start) >= 2 else waypoints[0]
    path_points = [p0] + waypoints
    num_segments = len(path_points) - 1

    wx, wy = float(wolf_pos[0]), float(wolf_pos[1])
    vx = float(wolf_vel[0]) if wolf_vel and len(wolf_vel) >= 1 else 0.0
    vy = float(wolf_vel[1]) if wolf_vel and len(wolf_vel) >= 2 else 0.0

    min_dist = float("inf")
    closest_t = 0.0
    closest_scout = [0.0, 0.0]
    closest_wolf = [0.0, 0.0]

    total_time = float(num_segments) * 1.0  # 1.0s per step

    for seg_idx in range(num_segments):
        start_pt = path_points[seg_idx]
        end_pt = path_points[seg_idx + 1]

        for s in range(samples_per_step):
            frac = s / float(samples_per_step)
            t_curr = seg_idx * 1.0 + frac * 1.0

            # Interpolate Scout position along polyline segment
            sx = start_pt[0] + (end_pt[0] - start_pt[0]) * frac
            sy = start_pt[1] + (end_pt[1] - start_pt[1]) * frac

            # Extrapolate Wolf position based on constant velocity projection
            w_curr_x = wx + vx * t_curr
            w_curr_y = wy + vy * t_curr

            dist = math.hypot(sx - w_curr_x, sy - w_curr_y)
            if dist < min_dist:
                min_dist = dist
                closest_t = t_curr
                closest_scout = [sx, sy]
                closest_wolf = [w_curr_x, w_curr_y]

    approved = min_dist >= safety_dist
    if approved:
        reason = (
            f"APPROVED: Trajectory lookahead clear "
            f"(measured d_min = {min_dist:.1f}px >= {safety_dist:.1f}px at t={closest_t:.2f}s)"
        )
    else:
        reason = (
            f"REJECT: Path breaches predator safety margin "
            f"(measured d_min = {min_dist:.1f}px < {safety_dist:.1f}px at t={closest_t:.2f}s)"
        )

    return {
        "approved": approved,
        "min_distance": round(min_dist, 2),
        "closest_time": round(closest_t, 2),
        "closest_scout_pos": [round(c, 1) for c in closest_scout],
        "closest_wolf_pos": [round(c, 1) for c in closest_wolf],
        "safety_dist": safety_dist,
        "reason": reason,
    }


class LivingWorldBridgeHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler serving static web files and MongNhiem REST API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        # Keep stdout clean; log only unexpected errors
        if "404" in format % args or "500" in format % args:
            sys.stderr.write(f"[Bridge Warning] {format % args}\n")

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json_response(self, data: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        """Handles preflight CORS requests."""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        """Routes API status or serves static Canvas dashboard assets."""
        if self.path == "/api/status" or self.path.startswith("/api/status?"):
            kernel = get_kernel()
            snapshot = {name: kernel.state_engine.get_variable(name) for name in kernel.state_engine.variables}
            self._send_json_response({
                "status": "ONLINE",
                "schema_name": kernel.schema.schema_name,
                "simulated_tick": kernel.temporal_bridge.simulated_tick,
                "in_standby": kernel.human_bridge.in_standby,
                "standby_reason": kernel.human_bridge.standby_reason,
                "state_snapshot": snapshot,
                "active_fact_cards": [
                    {
                        "entity": c.entity,
                        "value": c.value,
                        "priority": c.priority,
                        "version": c.version,
                    }
                    for c in kernel.active_fact_cards
                ],
            })
            return

        super().do_GET()

    def do_POST(self) -> None:
        """Processes cognitive ticks, lookahead verifications, and supervisory commands."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            payload = json.loads(raw_body) if raw_body else {}
        except Exception as e:
            self._send_json_response({"success": False, "error": f"Malformed JSON: {e}"}, status=400)
            return

        endpoint = self.path.split("?")[0]

        if endpoint == "/api/step":
            # 1. Authoritative Cognitive Step Execution
            kernel = get_kernel()

            # Synchronize state variables if provided from simulation
            state_updates = payload.get("state_updates", {})
            for var_name, var_val in state_updates.items():
                if var_name in kernel.state_engine.variables and var_val is not None:
                    kernel.state_engine.set_variable(var_name, float(var_val))

            stimulus = payload.get("stimulus", "")
            user_input = payload.get("user_input")
            delta_time = float(payload.get("delta_time", 0.05))

            result: StepResult = kernel.tick(
                stimulus=stimulus,
                user_input=user_input,
                delta_time=delta_time,
            )

            self._send_json_response({
                "success": True,
                "tick": result.tick,
                "action_verb": result.action_verb,
                "action_params": result.action_params,
                "comm_class": result.comm_class.value,
                "comm_message": result.comm_message,
                "raw_output": result.raw_output,
                "in_standby": result.in_standby,
                "preempted": result.preempted,
                "state_snapshot": result.state_snapshot,
                "fired_invariants": result.fired_invariants,
                "fact_cards": [
                    {
                        "entity": c.entity,
                        "value": c.value,
                        "priority": c.priority,
                        "version": c.version,
                    }
                    for c in result.fact_cards
                ],
            })

        elif endpoint == "/api/verify_lookahead":
            # 2. 4-Step Spatial Trajectory Lookahead Verification
            waypoints = payload.get("waypoints", [])
            wolf_pos = payload.get("wolf_pos", [0.0, 0.0])
            wolf_vel = payload.get("wolf_vel", [0.0, 0.0])
            scout_start = payload.get("scout_start")
            safety_dist = float(payload.get("safety_dist", 35.0))

            verification = evaluate_spatial_lookahead(
                waypoints=waypoints,
                wolf_pos=wolf_pos,
                wolf_vel=wolf_vel,
                scout_start=scout_start,
                safety_dist=safety_dist,
            )
            self._send_json_response(verification)

        elif endpoint == "/api/operator_action":
            # 3. Human Supervisory Command Preemption
            kernel = get_kernel()
            cmd = payload.get("command", "")
            standby = payload.get("standby")

            if cmd:
                kernel.human_bridge.inject_human_command(cmd)

            if standby is not None:
                if standby:
                    kernel.human_bridge.enter_standby(payload.get("reason", "Operator Standby Engaged"))
                else:
                    kernel.human_bridge.in_standby = False
                    kernel.human_bridge.standby_reason = None

            self._send_json_response({
                "success": True,
                "command_injected": cmd,
                "in_standby": kernel.human_bridge.in_standby,
                "standby_reason": kernel.human_bridge.standby_reason,
            })

        elif endpoint == "/api/reset":
            # 4. Clean State Reset
            reset_kernel()
            self._send_json_response({"success": True, "message": "Kernel reset to initial schema baseline."})

        else:
            self._send_json_response({"success": False, "error": f"Unknown endpoint: {endpoint}"}, status=404)


def run_server() -> None:
    """Launches the cognitive bridge server and prints operational endpoints."""
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), LivingWorldBridgeHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print(f"\n========================================================")
        print(f" Mong Nhiem Cognitive Bridge Server Running on Port {PORT}")
        print(f" Dashboard URL:  {url}")
        print(f" Status API:     http://localhost:{PORT}/api/status")
        print(f" Step API:       http://localhost:{PORT}/api/step")
        print(f" Lookahead API:  http://localhost:{PORT}/api/verify_lookahead")
        print(f" Zero external dependencies. 100% Python Standard Library.")
        print(f" Press Ctrl+C to terminate.")
        print(f"========================================================\n")

        if "--no-browser" not in sys.argv:
            try:
                webbrowser.open(url)
            except Exception:
                pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down cognitive bridge server.")
            httpd.server_close()


if __name__ == "__main__":
    run_server()
