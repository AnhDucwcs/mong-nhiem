"""Static contract tests for MN-007 measurement authority and request order."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

MN007_DIR = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-007-state-recovery-operating-region"
)
MN007_SCRIPTS = MN007_DIR / "scripts"
if str(MN007_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MN007_SCRIPTS))

import mn007_materialization as materialization
import mn007_measurement_authority as authority

FROZEN_REQUEST_ORDER_SHA256 = (
    "93d578e5a24903e826f2ad0481a420d219e53be30e2e4a822d9c3fdc0a96b474"
)
FROZEN_AUTHORITY_CORE_SHA256 = (
    "2d5d82c1a342c34dfb0b3d35d0b6f0cef4dba835d8ebcc75e15398a2beab2633"
)
FROZEN_AUTHORITY_FILE_SHA256 = (
    "213e2c355cf3ee7b59f81bf67ab6538608ec92ce90cc00179597f34efeadf5b8"
)


def request_order() -> list[str]:
    return authority.build_request_order()


def test_request_order_length_and_coverage() -> None:
    order = request_order()
    assert len(order) == 108
    assert len(set(order)) == 108
    by_cell = Counter(case_id.rsplit("-c", 1)[0] for case_id in order)
    assert by_cell == {cell.cell_id: 18 for cell in materialization.CELLS}


def test_request_order_strata_balance() -> None:
    order = request_order()
    for wave_idx in range(18):
        wave = order[wave_idx * 6 : (wave_idx + 1) * 6]
        wave_cells = [case_id.rsplit("-c", 1)[0] for case_id in wave]
        assert wave_cells == [cell.cell_id for cell in materialization.CELLS]
        wave_ordinals = [case_id.rsplit("-c", 1)[1] for case_id in wave]
        assert len(set(wave_ordinals)) == 1
        assert wave_ordinals[0] == f"{wave_idx + 1:02d}"


def test_request_order_fingerprint() -> None:
    order = request_order()
    text = "\n".join(order) + "\n"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert digest == FROZEN_REQUEST_ORDER_SHA256


def test_request_order_joins_materialized_public_prompts() -> None:
    prompts_path = (
        MN007_DIR / "definition" / "calibration-corpus-v1" / "public-prompts.jsonl"
    )
    lines = prompts_path.read_text(encoding="utf-8").strip().split("\n")
    corpus_ids = {json.loads(line)["case_id"] for line in lines}
    assert set(request_order()) == corpus_ids


def test_authority_file_validates_and_is_canonical() -> None:
    loaded = authority.validate_authority_artifact(authority.AUTHORITY_FILE)
    assert loaded["authority_id"] == authority.AUTHORITY_ID
    assert loaded["authority_version"] == authority.AUTHORITY_VERSION
    assert loaded["authority_core_sha256"] == FROZEN_AUTHORITY_CORE_SHA256
    file_bytes = authority.AUTHORITY_FILE.read_bytes()
    assert hashlib.sha256(file_bytes).hexdigest() == FROZEN_AUTHORITY_FILE_SHA256
    assert not file_bytes.startswith(b"\xef\xbb\xbf")
    assert b"\r\n" not in file_bytes
    assert file_bytes.endswith(b"\n")


def test_authority_self_reference_prohibition() -> None:
    core = authority.build_authority_core()
    assert "authority_core_sha256" not in core
    full = authority.build_authority()
    assert "authority_core_sha256" in full
    assert full["authority_core_sha256"] == FROZEN_AUTHORITY_CORE_SHA256


def test_authority_hash_determinism_and_mutation_sensitivity() -> None:
    core = authority.build_authority_core()
    base_hash = materialization.sha256_bytes(materialization.canonical_json_bytes(core))
    assert base_hash == FROZEN_AUTHORITY_CORE_SHA256

    mutated = copy.deepcopy(core)
    mutated["sampling"]["request_payload_schema"]["temperature"] = 0.1
    mut_hash = materialization.sha256_bytes(
        materialization.canonical_json_bytes(mutated)
    )
    assert mut_hash != base_hash

    mutated_runtime = copy.deepcopy(core)
    mutated_runtime["runtime"]["configured_context_size"] = 4096
    mut_runtime_hash = materialization.sha256_bytes(
        materialization.canonical_json_bytes(mutated_runtime)
    )
    assert mut_runtime_hash != base_hash

    # Proves composite hash changes when GPU configuration changes
    mutated_gpu = copy.deepcopy(core)
    mutated_gpu["runtime"]["gpu"]["n_gpu_layers"] = 0
    mut_gpu_hash = materialization.sha256_bytes(
        materialization.canonical_json_bytes(mutated_gpu)
    )
    assert mut_gpu_hash != base_hash

    # Proves composite hash changes when timeout changes
    mutated_timeout = copy.deepcopy(core)
    mutated_timeout["runtime"]["request_timeout_seconds"] = 60
    mut_timeout_hash = materialization.sha256_bytes(
        materialization.canonical_json_bytes(mutated_timeout)
    )
    assert mut_timeout_hash != base_hash

    # Proves composite hash changes when sampling classification changes
    mutated_sampling = copy.deepcopy(core)
    mutated_sampling["sampling"]["classification"]["top_k"] = "explicit_request_payload"
    mut_sampling_hash = materialization.sha256_bytes(
        materialization.canonical_json_bytes(mutated_sampling)
    )
    assert mut_sampling_hash != base_hash

    # Proves composite hash changes when hermetic environment contract changes
    mutated_env = copy.deepcopy(core)
    mutated_env["runtime"]["hermetic_environment"]["forbidden_env_prefixes"].pop()
    mut_env_hash = materialization.sha256_bytes(
        materialization.canonical_json_bytes(mutated_env)
    )
    assert mut_env_hash != base_hash
    # Proves composite hash changes when case_insensitive changes
    mutated_case = copy.deepcopy(core)
    mutated_case["runtime"]["hermetic_environment"]["env_matching_semantics"] = "case_sensitive"
    mut_case_hash = materialization.sha256_bytes(materialization.canonical_json_bytes(mutated_case))
    assert mut_case_hash != base_hash

    # Proves composite hash changes when PROGRAMDATA policy changes
    mutated_prog = copy.deepcopy(core)
    mutated_prog["runtime"]["hermetic_environment"]["execution_relevant_env_vars"]["PROGRAMDATA"] = "allow"
    mut_prog_hash = materialization.sha256_bytes(materialization.canonical_json_bytes(mutated_prog))
    assert mut_prog_hash != base_hash
    
    # Proves composite hash changes when config resolution strategy changes
    mutated_res = copy.deepcopy(core)
    mutated_res["runtime"]["configuration_file_policy"]["resolution_strategy"] = "ignore"
    mut_res_hash = materialization.sha256_bytes(materialization.canonical_json_bytes(mutated_res))
    assert mut_res_hash != base_hash



def test_exact_model_and_executable_fingerprints() -> None:
    core = authority.build_authority_core()
    assert core["model"]["sha256"] == authority.EXPECTED_MODEL_SHA256
    assert core["runtime"]["executable_sha256"] == authority.EXPECTED_EXECUTABLE_SHA256
    assert core["model"]["file"] == "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    assert core["runtime"]["build"] == "10566"
    assert core["runtime"]["commit"] == "bb4caa754"
    assert core["runtime"]["compiler"] == "MSVC 19.44.35217.0 for x64"


def test_server_command_and_offload_authority() -> None:
    core = authority.build_authority_core()
    cmd = core["runtime"]["server_command"]
    assert "-ngl" in cmd and cmd[cmd.index("-ngl") + 1] == "auto"
    assert "-sm" in cmd and cmd[cmd.index("-sm") + 1] == "layer"
    assert "-mg" in cmd and cmd[cmd.index("-mg") + 1] == "0"
    assert "--fit" in cmd and cmd[cmd.index("--fit") + 1] == "on"
    assert "--fit-target" in cmd and cmd[cmd.index("--fit-target") + 1] == "1024"
    assert "--fit-ctx" in cmd and cmd[cmd.index("--fit-ctx") + 1] == "4096"
    assert "--kv-offload" in cmd
    assert "--op-offload" in cmd
    assert "--load-mode" in cmd and cmd[cmd.index("--load-mode") + 1] == "auto"
    assert "-ub" in cmd and cmd[cmd.index("-ub") + 1] == "512"
    assert "-fa" in cmd and cmd[cmd.index("-fa") + 1] == "on"
    assert "-c" in cmd and cmd[cmd.index("-c") + 1] == "16896"
    assert "-t" in cmd and cmd[cmd.index("-t") + 1] == "12"
    assert "-b" in cmd and cmd[cmd.index("-b") + 1] == "2048"
    assert "-np" in cmd and cmd[cmd.index("-np") + 1] == "1"
    assert "--temp" in cmd and cmd[cmd.index("--temp") + 1] == "0"
    assert "--seed" in cmd and cmd[cmd.index("--seed") + 1] == "42"
    assert "--no-cache-prompt" in cmd
    assert "--no-webui" in cmd
    assert "--metrics" in cmd

    # GPU authority is NOT CPU-only
    gpu_flag = core["runtime"]["gpu_offload_flag"]
    assert "cpu threadpool execution" not in gpu_flag.lower()
    assert "auto" in gpu_flag.lower()

    # n_gpu_layers authority is the frozen auto configuration
    gpu_conf = core["runtime"]["gpu"]
    assert gpu_conf["n_gpu_layers_mode"] == "auto"
    assert gpu_conf["n_gpu_layers"] == -1

    # Runtime GPU defaults are internally consistent
    assert gpu_conf["device_selection"] == []
    assert gpu_conf["verified_device_name"] == "NVIDIA GeForce RTX 3050 Laptop GPU"
    assert gpu_conf["verified_evidence_retained_vram_mib"] == 2267
    assert gpu_conf["split_mode"] == "layer"
    assert gpu_conf["main_gpu"] == 0
    assert gpu_conf["tensor_split"] is None
    assert gpu_conf["kv_offload"] is True
    assert gpu_conf["fit_params"] is True
    assert gpu_conf["fit_params_target_mib"] == 1024
    assert gpu_conf["fit_params_min_ctx"] == 4096
    assert gpu_conf["load_mode"] == "auto"
    assert gpu_conf["op_offload"] is True


def test_sampling_classification_and_top_k_semantics() -> None:
    core = authority.build_authority_core()
    classification = core["sampling"]["classification"]
    expected_params = {
        "temperature",
        "seed",
        "max_tokens",
        "grammar",
        "messages",
        "chat_template_kwargs",
        "stream",
        "top_k",
        "top_p",
        "min_p",
        "typical_p",
        "repetition_penalty",
        "presence_penalty",
        "frequency_penalty",
        "mirostat",
        "stop",
    }
    assert set(classification) == expected_params
    assert classification["temperature"] == "explicit_request_and_runtime_arg"
    assert classification["seed"] == "explicit_request_and_runtime_arg"
    assert classification["max_tokens"] == "explicit_request_payload"
    assert classification["grammar"] == "explicit_request_payload"
    assert classification["stream"] == "explicit_request_payload"

    # top_k is NOT incorrectly represented as 1
    assert classification["top_k"] == "runtime_default"

    # Temperature-zero greedy behavior is represented separately from top-k
    effective = core["sampling"]["effective_sampling"]
    assert effective["runtime_top_k_parameter"] == 40
    assert effective["candidate_set_size"] == 1
    assert effective["behavior"] == "greedy_argmax_due_to_temperature_zero"

    # stream=false is frozen in request payload schema
    payload_schema = core["sampling"]["request_payload_schema"]
    assert payload_schema["stream"] is False


def test_execution_limits_and_timeouts() -> None:
    core = authority.build_authority_core()
    limits = core["execution_limits"]
    assert limits["request_timeout_seconds"] == 120
    assert limits["health_deadline_seconds"] == 180
    assert limits["retry_policy"] == "prohibited_strictly_once_per_case"
    assert limits["timeout_retry_allowed"] is False

    assert core["runtime"]["request_timeout_seconds"] == 120
    assert core["runtime"]["health_deadline_seconds"] == 180

    failure = core["failure_semantics"]
    assert failure["request_timeout_seconds"] == 120
    assert failure["health_deadline_seconds"] == 180
    assert failure["timeout_failure_policy"] == "abort_run_no_retry_fail_closed"


def test_failure_taxonomy_and_no_retry_policy() -> None:
    core = authority.build_authority_core()
    failure = core["failure_semantics"]
    assert failure["state_taxonomy"] == [
        "not_started",
        "sent_unconfirmed",
        "response_received",
        "persisted",
        "evaluated",
        "invalid_ambiguous",
    ]
    assert failure["retry_policy"] == "prohibited_strictly_once_per_case"
    assert (
        failure["sent_unconfirmed_status"] == "measurement_or_design_blocked"
    )
    assert failure["interruption_policy"] == "abort_run_no_retry_fail_closed"
    assert (
        failure["persistence_failure_policy"]
        == "abort_run_do_not_evaluate_fail_closed"
    )
    assert (
        failure["malformed_output_scoring"]
        == "score_zero_point_zero_persisted_as_is"
    )


def test_hermetic_env_vars_comprehensive_coverage() -> None:
    core = authority.build_authority_core()
    env_policy = core["runtime"]["hermetic_environment"]
    
    assert "LLAMA_" in env_policy["forbidden_env_prefixes"]
    
    execution_relevant = env_policy["execution_relevant_env_vars"]
    assert execution_relevant["CUDA_VISIBLE_DEVICES"] == "forbidden_unset_verify_before_launch"
    assert execution_relevant["GGML_CUDA_NO_PINNED"] == "forbidden_unset"
    assert execution_relevant["LLAMA_APP_CMD"] == "forbidden_unset"
    assert execution_relevant["LLAMA_SERVER_ROUTER_PORT"] == "forbidden_unset_router_only"

    config_policy = core["runtime"]["configuration_file_policy"]
    assert config_policy["required_config_files_absent"] is True
    assert config_policy["resolution_strategy"] == "read_host_env_resolve_paths_verify_absent_and_freeze_env_to_child"
    assert "PROGRAMDATA" in config_policy["windows_paths_resolved_from"]
    assert "APPDATA" in config_policy["windows_paths_resolved_from"]
    
    executor_contract = core["runtime"]["executor_contract"]
    assert executor_contract["must_use_argv_no_shell"] is True
    assert executor_contract["child_process_environment_policy"] == "freeze_exact_preflight_values_no_inheritance"

    assert core["preflight"]["forbidden_env_vars_must_be_unset"] is True


def test_no_silent_gpu_placement_override() -> None:
    core = authority.build_authority_core()
    cmd = core["runtime"]["server_command"]
    prefixes = core["runtime"]["hermetic_environment"]["forbidden_env_prefixes"]
    is_forbidden = lambda v: any(v.startswith(p) for p in prefixes)
    # Explicit CLI arguments present
    assert "-ngl" in cmd and cmd[cmd.index("-ngl") + 1] == "auto"
    assert "-sm" in cmd and cmd[cmd.index("-sm") + 1] == "layer"
    assert "-mg" in cmd and cmd[cmd.index("-mg") + 1] == "0"
    assert "--kv-offload" in cmd
    assert "--op-offload" in cmd
    # Env vars forbidden
    assert is_forbidden("LLAMA_ARG_DEVICE")
    assert is_forbidden("LLAMA_ARG_N_GPU_LAYERS")
    assert is_forbidden("LLAMA_ARG_SPLIT_MODE")
    assert is_forbidden("LLAMA_ARG_TENSOR_SPLIT")
    assert is_forbidden("LLAMA_ARG_MAIN_GPU")
    assert is_forbidden("LLAMA_ARG_KV_OFFLOAD")
    assert is_forbidden("LLAMA_ARG_OP_OFFLOAD")


def test_no_silent_fit_behavior_override() -> None:
    core = authority.build_authority_core()
    cmd = core["runtime"]["server_command"]
    prefixes = core["runtime"]["hermetic_environment"]["forbidden_env_prefixes"]
    is_forbidden = lambda v: any(v.startswith(p) for p in prefixes)
    assert "--fit" in cmd and cmd[cmd.index("--fit") + 1] == "on"
    assert "--fit-target" in cmd and cmd[cmd.index("--fit-target") + 1] == "1024"
    assert "--fit-ctx" in cmd and cmd[cmd.index("--fit-ctx") + 1] == "4096"
    assert "--load-mode" in cmd and cmd[cmd.index("--load-mode") + 1] == "auto"
    assert is_forbidden("LLAMA_ARG_FIT")
    assert is_forbidden("LLAMA_ARG_FIT_TARGET")
    assert is_forbidden("LLAMA_ARG_FIT_CTX")
    assert is_forbidden("LLAMA_ARG_LOAD_MODE")


def test_no_silent_context_batch_parallelism_override() -> None:
    core = authority.build_authority_core()
    cmd = core["runtime"]["server_command"]
    prefixes = core["runtime"]["hermetic_environment"]["forbidden_env_prefixes"]
    is_forbidden = lambda v: any(v.startswith(p) for p in prefixes)
    assert "-c" in cmd and cmd[cmd.index("-c") + 1] == "16896"
    assert "-t" in cmd and cmd[cmd.index("-t") + 1] == "12"
    assert "-b" in cmd and cmd[cmd.index("-b") + 1] == "2048"
    assert "-ub" in cmd and cmd[cmd.index("-ub") + 1] == "512"
    assert "-np" in cmd and cmd[cmd.index("-np") + 1] == "1"
    assert "-fa" in cmd and cmd[cmd.index("-fa") + 1] == "on"
    assert is_forbidden("LLAMA_ARG_CTX_SIZE")
    assert is_forbidden("LLAMA_ARG_THREADS")
    assert is_forbidden("LLAMA_ARG_BATCH")
    assert is_forbidden("LLAMA_ARG_UBATCH")
    assert is_forbidden("LLAMA_ARG_N_PARALLEL")
    assert is_forbidden("LLAMA_ARG_FLASH_ATTN")


def test_no_silent_sampling_override() -> None:
    core = authority.build_authority_core()
    cmd = core["runtime"]["server_command"]
    prefixes = core["runtime"]["hermetic_environment"]["forbidden_env_prefixes"]
    is_forbidden = lambda v: any(v.startswith(p) for p in prefixes)
    assert "--temp" in cmd and cmd[cmd.index("--temp") + 1] == "0"
    assert "--seed" in cmd and cmd[cmd.index("--seed") + 1] == "42"
    assert is_forbidden("LLAMA_ARG_TOP_K")
    assert is_forbidden("LLAMA_ARG_TEMP")
    assert is_forbidden("LLAMA_ARG_SEED")
    assert is_forbidden("LLAMA_ARG_TOP_P")
    assert is_forbidden("LLAMA_ARG_MIN_P")


def test_no_silent_prompt_caching_override() -> None:
    core = authority.build_authority_core()
    cmd = core["runtime"]["server_command"]
    prefixes = core["runtime"]["hermetic_environment"]["forbidden_env_prefixes"]
    is_forbidden = lambda v: any(v.startswith(p) for p in prefixes)
    assert "--no-cache-prompt" in cmd
    assert is_forbidden("LLAMA_ARG_CACHE_PROMPT")

def test_case_insensitive_matching_and_config_paths() -> None:
    core = authority.build_authority_core()
    
    assert core["runtime"]["hermetic_environment"]["env_matching_semantics"] == "case_insensitive_windows_crt"
    
    prefixes = core["runtime"]["hermetic_environment"]["forbidden_env_prefixes"]
    is_forbidden = lambda v: any(v.upper().startswith(p.upper()) for p in prefixes)
    
    # Test case insensitivity for prefixes
    assert is_forbidden("LLAMA_ARG_TEMP")
    assert is_forbidden("llama_arg_temp")
    assert is_forbidden("LlAmA_ArG_TeMp")
    assert is_forbidden("LLAMA_SERVER_DEBUG_FAKE_TIMING")
    
    exec_vars = core["runtime"]["hermetic_environment"]["execution_relevant_env_vars"]
    # Check named variables with uppercase normalized lookup
    assert exec_vars["PROGRAMDATA".upper()] == "frozen_config_path_input"
    assert exec_vars["APPDATA".upper()] == "frozen_config_path_input"
    assert exec_vars["CUDA_VISIBLE_DEVICES".upper()] == "forbidden_unset_verify_before_launch"
    assert exec_vars["GGML_CUDA_NO_PINNED".upper()] == "forbidden_unset"
    assert exec_vars["LOCALAPPDATA".upper()] == "irrelevant_due_to_explicit_local_model_path_but_forbidden_unset"
    
    config_policy = core["runtime"]["configuration_file_policy"]
    assert config_policy["resolution_strategy"] == "read_host_env_resolve_paths_verify_absent_and_freeze_env_to_child"
    assert "PROGRAMDATA" in config_policy["windows_paths_resolved_from"]
    assert "APPDATA" in config_policy["windows_paths_resolved_from"]
    
    executor = core["runtime"]["executor_contract"]
    assert executor["child_process_environment_policy"] == "freeze_exact_preflight_values_no_inheritance"
