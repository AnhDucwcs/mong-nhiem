"""Deterministic MN-007 calibration measurement-authority model and serialization."""
from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import mn007_materialization as materialization

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_FILE = EXPERIMENT_ROOT / "measurement-authority.json"

AUTHORITY_ID = "mn007-calibration-measurement-authority-v1"
AUTHORITY_VERSION = "1.0.0"

EXPECTED_MODEL_FILE = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
EXPECTED_MODEL_PATH = (
    r"D:\Code\mong-nhiem\artifacts\models\mn-002\Llama-3.2-3B-Instruct-Q4_K_M.gguf"
)
EXPECTED_MODEL_SHA256 = (
    "6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff"
)
EXPECTED_MODEL_SIZE = 2019377696
EXPECTED_MODEL_SUBJECT = "llama-3.2-3b"

EXPECTED_EXECUTABLE_PATH = (
    r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe"
)
EXPECTED_EXECUTABLE_SHA256 = (
    "28d861538ffdf4e811e2febb0c5f06063792d184b66a2758f103c165629bc08"
)
EXPECTED_RUNTIME_VERSION = "0.2.0-dev"
EXPECTED_RUNTIME_BUILD = "10566"
EXPECTED_RUNTIME_COMMIT = "bb4caa754"
EXPECTED_RUNTIME_COMPILER = "MSVC 19.44.35217.0 for x64"

REQUEST_ORDER_CONTRACT = "mn007-interleaved-cell-round-robin-v1"
EXPECTED_REQUEST_ORDER_SHA256 = (
    "93d578e5a24903e826f2ad0481a420d219e53be30e2e4a822d9c3fdc0a96b474"
)
EXPECTED_GRAMMAR_SHA256 = hashlib.sha256(
    materialization.GRAMMAR.encode("utf-8")
).hexdigest()


class AuthorityValidationError(ValueError):
    """Raised when measurement authority invariants are violated."""


def build_request_order() -> list[str]:
    return [
        f"{cell.cell_id}-c{k:02d}"
        for k in range(1, 19)
        for cell in materialization.CELLS
    ]


def build_authority_core() -> dict[str, Any]:
    """Construct canonical authority mapping excluding its self-referential hash."""
    order = build_request_order()
    order_text = "\n".join(order) + "\n"
    order_sha256 = hashlib.sha256(order_text.encode("utf-8")).hexdigest()

    return {
        "authority_id": AUTHORITY_ID,
        "authority_version": AUTHORITY_VERSION,
        "corpus": {
            "calibration_namespace": materialization.CALIBRATION_NAMESPACE,
            "contract_document_sha256": "8fad7292d18b56c89ae15d4a7b87a3260008316cc1975348995c8dd9c18c9a61",
            "contract_namespace": materialization.CONTRACT_NAMESPACE,
            "evaluator_corpus_sha256": "c88d0ed7d5ded70987e3468917df7e658a40d31b34ad5c4eac6fc10ec69392fa",
            "manifest_core_sha256": "380da885870e234ba6c9935622096d054e0b9e78ed7755d9add6c660fd974194",
            "manifest_physical_sha256": "98f30163d72696fac1b14d849fbcdcf9c93c03f5f292d0dfb4c8d50997bfae49",
            "materializer_source_sha256": "10e9c39be234ae320e74a70f251206b11246b95555f71b9f0602abf88b1a25ac",
            "public_prompt_corpus_sha256": "e3f6ec3881a5d2d98dc702adf1b9085536bca02f4413142cb0e8e7a221541353",
            "record_count": 108,
            "root_seed_sha256": "d97d50f4f1b396d13203e91241979945c2787e07a8adeffa5eb13ccc7361a31b",
            "semantic_corpus_sha256": "61ca3269dd948846345831aaa054385d2e2dca03e8a601df3226c0b5dde3f941",
        },
        "evaluator": {
            "corpus_sha256": "c88d0ed7d5ded70987e3468917df7e658a40d31b34ad5c4eac6fc10ec69392fa",
            "grammar": materialization.GRAMMAR,
            "grammar_id": materialization.GRAMMAR_ID,
            "grammar_sha256": EXPECTED_GRAMMAR_SHA256,
            "parser_rule": "strict_ascii_whitespace_trimmed_two_token_vector",
            "schema": materialization.EVALUATOR_SCHEMA,
            "scoring_rule": "exact_vector_match_binary_1_or_0",
        },
        "execution_limits": {
            "health_deadline_seconds": 180,
            "request_timeout_seconds": 120,
            "retry_policy": "prohibited_strictly_once_per_case",
            "timeout_retry_allowed": False,
        },
        "failure_semantics": {
            "health_deadline_seconds": 180,
            "interruption_policy": "abort_run_no_retry_fail_closed",
            "malformed_output_scoring": "score_zero_point_zero_persisted_as_is",
            "persistence_failure_policy": "abort_run_do_not_evaluate_fail_closed",
            "request_timeout_seconds": 120,
            "retry_policy": "prohibited_strictly_once_per_case",
            "sent_unconfirmed_status": "measurement_or_design_blocked",
            "state_taxonomy": [
                "not_started",
                "sent_unconfirmed",
                "response_received",
                "persisted",
                "evaluated",
                "invalid_ambiguous",
            ],
            "timeout_failure_policy": "abort_run_no_retry_fail_closed",
        },
        "model": {
            "exact_path": EXPECTED_MODEL_PATH,
            "file": EXPECTED_MODEL_FILE,
            "name": "Meta Llama 3.2 3B Instruct",
            "provenance": "Meta official weights converted to GGUF, qualified under MN-002 (MCB v0.3.0)",
            "quantization": "Q4_K_M",
            "sha256": EXPECTED_MODEL_SHA256,
            "size_bytes": EXPECTED_MODEL_SIZE,
            "subject": EXPECTED_MODEL_SUBJECT,
        },
        "preflight": {
            "clean_environment_required": True,
            "forbidden_env_vars_must_be_unset": True,
            "gpu_memory_used_max_mib": 0,
            "gpu_utilization_max_percent": 0,
            "no_compute_processes": True,
            "no_stale_llama_processes": True,
            "verify_corpus_manifest": True,
            "verify_executable_sha256": True,
            "verify_model_sha256": True,
        },
        "request_order": {
            "case_count": 108,
            "contract": REQUEST_ORDER_CONTRACT,
            "formula": "wave = (ordinal // 6) + 1; cell = CELLS[ordinal % 6]; case_id = f'{cell.cell_id}-c{wave:02d}'",
            "sha256": order_sha256,
            "strata_wave_count": 18,
        },
        "runtime": {
            "backend": "llama.cpp",
            "batch_size": 2048,
            "build": EXPECTED_RUNTIME_BUILD,
            "chat_template_flag": "--jinja",
            "chat_template_kwargs_arg": "{}",
            "commit": EXPECTED_RUNTIME_COMMIT,
            "compiler": EXPECTED_RUNTIME_COMPILER,
            "configured_context_size": 16896,
            "exact_executable_path": EXPECTED_EXECUTABLE_PATH,
            "executable_sha256": EXPECTED_EXECUTABLE_SHA256,
            "flash_attention": "on",
            "gpu": {
                "device_selection": [],
                "fit_params": True,
                "fit_params_min_ctx": 4096,
                "fit_params_target_mib": 1024,
                "kv_offload": True,
                "load_mode": "auto",
                "main_gpu": 0,
                "n_gpu_layers": -1,
                "n_gpu_layers_mode": "auto",
                "op_offload": True,
                "split_mode": "layer",
                "tensor_split": None,
                "verified_device_name": "NVIDIA GeForce RTX 3050 Laptop GPU",
                "verified_evidence_retained_vram_mib": 2267,
            },
            "gpu_offload_flag": "-ngl auto (runtime auto layer fitting into VRAM; verified from retained MN-006 evidence 2267-2289 MiB)",
            "health_deadline_seconds": 180,
            "hermetic_environment": {
                "cli_overrides_env_proven": True,
                "env_precedence_semantics": "config_file_then_env_then_cli",
                "forbidden_env_prefixes": ["LLAMA_ARG_", "LLAMA_"],
                "forbidden_env_vars": sorted([
                    "LLAMA_API_KEY",
                    "LLAMA_ARG_AGENT",
                    "LLAMA_ARG_ALIAS",
                    "LLAMA_ARG_API_KEY_FILE",
                    "LLAMA_ARG_API_PREFIX",
                    "LLAMA_ARG_BACKEND_SAMPLING",
                    "LLAMA_ARG_BATCH",
                    "LLAMA_ARG_CACHE_IDLE_SLOTS",
                    "LLAMA_ARG_CACHE_PROMPT",
                    "LLAMA_ARG_CACHE_RAM",
                    "LLAMA_ARG_CACHE_REUSE",
                    "LLAMA_ARG_CACHE_TYPE_K",
                    "LLAMA_ARG_CACHE_TYPE_V",
                    "LLAMA_ARG_CHAT_TEMPLATE",
                    "LLAMA_ARG_CHAT_TEMPLATE_FILE",
                    "LLAMA_ARG_CHAT_TEMPLATE_KWARGS",
                    "LLAMA_ARG_CHECKPOINT_MIN_SPACING_NT",
                    "LLAMA_ARG_CONTEXT_SHIFT",
                    "LLAMA_ARG_CONT_BATCHING",
                    "LLAMA_ARG_CORS_CREDENTIALS",
                    "LLAMA_ARG_CORS_HEADERS",
                    "LLAMA_ARG_CORS_METHODS",
                    "LLAMA_ARG_CORS_ORIGINS",
                    "LLAMA_ARG_CPU_MOE",
                    "LLAMA_ARG_CTX_CHECKPOINTS",
                    "LLAMA_ARG_CTX_SIZE",
                    "LLAMA_ARG_DEFRAG_THOLD",
                    "LLAMA_ARG_DEVICE",
                    "LLAMA_ARG_DIO",
                    "LLAMA_ARG_DOCKER_REPO",
                    "LLAMA_ARG_DRAFT_MAX",
                    "LLAMA_ARG_DRAFT_MIN",
                    "LLAMA_ARG_EMBEDDINGS",
                    "LLAMA_ARG_ENDPOINT_METRICS",
                    "LLAMA_ARG_ENDPOINT_PROPS",
                    "LLAMA_ARG_ENDPOINT_SLOTS",
                    "LLAMA_ARG_FIT",
                    "LLAMA_ARG_FIT_CTX",
                    "LLAMA_ARG_FIT_ESTIMATE",
                    "LLAMA_ARG_FIT_TARGET",
                    "LLAMA_ARG_FLASH_ATTN",
                    "LLAMA_ARG_GRP_ATTN_N",
                    "LLAMA_ARG_GRP_ATTN_W",
                    "LLAMA_ARG_HF_FILE",
                    "LLAMA_ARG_HF_REPO",
                    "LLAMA_ARG_HOST",
                    "LLAMA_ARG_IMAGE_MAX_TOKENS",
                    "LLAMA_ARG_IMAGE_MIN_TOKENS",
                    "LLAMA_ARG_JINJA",
                    "LLAMA_ARG_KV_OFFLOAD",
                    "LLAMA_ARG_KV_UNIFIED",
                    "LLAMA_ARG_LOAD_MODE",
                    "LLAMA_ARG_LOG_COLORS",
                    "LLAMA_ARG_LOG_FILE",
                    "LLAMA_ARG_LOG_PREFIX",
                    "LLAMA_ARG_LOG_TIMESTAMPS",
                    "LLAMA_ARG_LOG_VERBOSITY",
                    "LLAMA_ARG_MAIN_GPU",
                    "LLAMA_ARG_MCP_SERVERS_CONFIG",
                    "LLAMA_ARG_MCP_SERVERS_JSON",
                    "LLAMA_ARG_MIN_P",
                    "LLAMA_ARG_MLOCK",
                    "LLAMA_ARG_MMAP",
                    "LLAMA_ARG_MMPROJ",
                    "LLAMA_ARG_MMPROJ_AUTO",
                    "LLAMA_ARG_MMPROJ_OFFLOAD",
                    "LLAMA_ARG_MMPROJ_URL",
                    "LLAMA_ARG_MODEL",
                    "LLAMA_ARG_MODELS_AUTOLOAD",
                    "LLAMA_ARG_MODELS_DIR",
                    "LLAMA_ARG_MODELS_MAX",
                    "LLAMA_ARG_MODELS_PRESET",
                    "LLAMA_ARG_MODEL_URL",
                    "LLAMA_ARG_MTMD_BATCH_MAX_TOKENS",
                    "LLAMA_ARG_NO_CACHE_PROMPT",
                    "LLAMA_ARG_NO_HOST",
                    "LLAMA_ARG_NUMA",
                    "LLAMA_ARG_N_CPU_MOE",
                    "LLAMA_ARG_N_GPU_LAYERS",
                    "LLAMA_ARG_N_GPU_LAYERS_DRAFT",
                    "LLAMA_ARG_N_PARALLEL",
                    "LLAMA_ARG_N_PREDICT",
                    "LLAMA_ARG_OFFLINE",
                    "LLAMA_ARG_OP_OFFLOAD",
                    "LLAMA_ARG_OVERRIDE_TENSOR",
                    "LLAMA_ARG_PERF",
                    "LLAMA_ARG_POOLING",
                    "LLAMA_ARG_PORT",
                    "LLAMA_ARG_PREFILL_ASSISTANT",
                    "LLAMA_ARG_REASONING",
                    "LLAMA_ARG_REASONING_EFFORT",
                    "LLAMA_ARG_REASONING_PRESERVE",
                    "LLAMA_ARG_REPACK",
                    "LLAMA_ARG_RERANKING",
                    "LLAMA_ARG_REUSE_PORT",
                    "LLAMA_ARG_ROPE_FREQ_BASE",
                    "LLAMA_ARG_ROPE_FREQ_SCALE",
                    "LLAMA_ARG_ROPE_SCALE",
                    "LLAMA_ARG_ROPE_SCALING_TYPE",
                    "LLAMA_ARG_RPC",
                    "LLAMA_ARG_SEED",
                    "LLAMA_ARG_SHOW_TIMINGS",
                    "LLAMA_ARG_SKIP_CHAT_PARSING",
                    "LLAMA_ARG_SPEC_DRAFT_BACKEND_SAMPLING",
                    "LLAMA_ARG_SPEC_DRAFT_CACHE_TYPE_K",
                    "LLAMA_ARG_SPEC_DRAFT_CACHE_TYPE_V",
                    "LLAMA_ARG_SPEC_DRAFT_CPU_MOE",
                    "LLAMA_ARG_SPEC_DRAFT_HF_REPO",
                    "LLAMA_ARG_SPEC_DRAFT_MODEL",
                    "LLAMA_ARG_SPEC_DRAFT_N_CPU_MOE",
                    "LLAMA_ARG_SPEC_DRAFT_N_MAX",
                    "LLAMA_ARG_SPEC_DRAFT_N_MIN",
                    "LLAMA_ARG_SPEC_DRAFT_P_MIN",
                    "LLAMA_ARG_SPEC_DRAFT_P_SPLIT",
                    "LLAMA_ARG_SPEC_TYPE",
                    "LLAMA_ARG_SPLIT_MODE",
                    "LLAMA_ARG_SSE_PING_INTERVAL",
                    "LLAMA_ARG_SSL_CERT_FILE",
                    "LLAMA_ARG_SSL_KEY_FILE",
                    "LLAMA_ARG_STATIC_PATH",
                    "LLAMA_ARG_SWA_FULL",
                    "LLAMA_ARG_TAGS",
                    "LLAMA_ARG_TEMP",
                    "LLAMA_ARG_TENSOR_SPLIT",
                    "LLAMA_ARG_THINK",
                    "LLAMA_ARG_THINK_BUDGET",
                    "LLAMA_ARG_THINK_BUDGET_MESSAGE",
                    "LLAMA_ARG_THREADS",
                    "LLAMA_ARG_THREADS_HTTP",
                    "LLAMA_ARG_TIMEOUT",
                    "LLAMA_ARG_TOOLS",
                    "LLAMA_ARG_TOOLS_RUNTIME",
                    "LLAMA_ARG_TOP_K",
                    "LLAMA_ARG_TOP_P",
                    "LLAMA_ARG_UBATCH",
                    "LLAMA_ARG_UI",
                    "LLAMA_ARG_UI_CONFIG",
                    "LLAMA_ARG_UI_CONFIG_FILE",
                    "LLAMA_ARG_UI_MCP_PROXY",
                    "LLAMA_ARG_YARN_ATTN_FACTOR",
                    "LLAMA_ARG_YARN_BETA_FAST",
                    "LLAMA_ARG_YARN_BETA_SLOW",
                    "LLAMA_ARG_YARN_EXT_FACTOR",
                    "LLAMA_ARG_YARN_ORIG_CTX",
                ]),
                "required_env_clean_state": "all_forbidden_vars_unset",
            },
            "host": "127.0.0.1",
            "metrics": True,
            "parallel_slots": 1,
            "port": 18501,
            "prompt_cache": False,
            "request_timeout_seconds": 120,
            "server_command": [
                EXPECTED_EXECUTABLE_PATH,
                "-m",
                EXPECTED_MODEL_PATH,
                "--host",
                "127.0.0.1",
                "--port",
                "18501",
                "-c",
                "16896",
                "-t",
                "12",
                "-b",
                "2048",
                "-ub",
                "512",
                "-np",
                "1",
                "-fa",
                "on",
                "-ngl",
                "auto",
                "-sm",
                "layer",
                "-mg",
                "0",
                "--fit",
                "on",
                "--fit-target",
                "1024",
                "--fit-ctx",
                "4096",
                "--kv-offload",
                "--op-offload",
                "--load-mode",
                "auto",
                "--temp",
                "0",
                "--seed",
                "42",
                "--jinja",
                "--no-webui",
                "--no-cache-prompt",
                "--metrics",
                "--chat-template-kwargs",
                "{}",
            ],
            "threads": 12,
            "ubatch_size": 512,
            "version": EXPECTED_RUNTIME_VERSION,
            "webui": False,
        },
        "sampling": {
            "classification": {
                "chat_template_kwargs": "explicit_request_and_runtime_arg",
                "frequency_penalty": "not_applicable_inactive_under_greedy",
                "grammar": "explicit_request_payload",
                "max_tokens": "explicit_request_payload",
                "messages": "explicit_request_payload",
                "min_p": "not_applicable_inactive_under_greedy",
                "mirostat": "not_applicable_inactive_under_greedy",
                "presence_penalty": "not_applicable_inactive_under_greedy",
                "repetition_penalty": "not_applicable_inactive_under_greedy",
                "seed": "explicit_request_and_runtime_arg",
                "stop": "deterministic_runtime_default_via_grammar_and_gguf_eos",
                "stream": "explicit_request_payload",
                "temperature": "explicit_request_and_runtime_arg",
                "top_k": "runtime_default",
                "top_p": "not_applicable_inactive_under_greedy",
                "typical_p": "not_applicable_inactive_under_greedy",
            },
            "effective_sampling": {
                "behavior": "greedy_argmax_due_to_temperature_zero",
                "candidate_set_size": 1,
                "runtime_top_k_parameter": 40,
                "sampler_chain_order": [
                    "penalties",
                    "dry",
                    "top_n_sigma",
                    "top_k",
                    "typical_p",
                    "top_p",
                    "min_p",
                    "xtc",
                    "temperature",
                ],
            },
            "request_payload_schema": {
                "chat_template_kwargs": {},
                "grammar": materialization.GRAMMAR,
                "max_tokens": 16,
                "messages": [
                    {
                        "content": "<canonical_public_prompt_text>",
                        "role": "user",
                    }
                ],
                "seed": 42,
                "stream": False,
                "temperature": 0.0,
            },
        },
    }


def build_authority() -> dict[str, Any]:
    core = build_authority_core()
    core_bytes = materialization.canonical_json_bytes(core)
    core_sha256 = materialization.sha256_bytes(core_bytes)
    return {
        **core,
        "authority_core_sha256": core_sha256,
    }


def authority_bytes() -> bytes:
    authority = build_authority()
    return materialization.canonical_json_bytes(authority)


def write_authority_artifact(target: Path = AUTHORITY_FILE) -> dict[str, Any]:
    payload = authority_bytes()
    target.write_bytes(payload)
    return validate_authority_artifact(target)


def validate_authority_artifact(target: Path = AUTHORITY_FILE) -> dict[str, Any]:
    if not target.is_file():
        raise AuthorityValidationError(f"Authority artifact missing: {target}")
    content = target.read_bytes()
    expected = authority_bytes()
    if content != expected:
        raise AuthorityValidationError(
            f"Authority physical bytes differ from canonical build: {target}"
        )
    loaded = json.loads(content.decode("utf-8"))
    core = {k: v for k, v in loaded.items() if k != "authority_core_sha256"}
    expected_core_sha256 = materialization.sha256_bytes(
        materialization.canonical_json_bytes(core)
    )
    if loaded.get("authority_core_sha256") != expected_core_sha256:
        raise AuthorityValidationError("authority_core_sha256 mismatch")
    return loaded


def main() -> int:
    write_authority_artifact(AUTHORITY_FILE)
    loaded = validate_authority_artifact(AUTHORITY_FILE)
    print("Authority validated:")
    print("  authority_id:", loaded["authority_id"])
    print("  authority_version:", loaded["authority_version"])
    print("  authority_core_sha256:", loaded["authority_core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
