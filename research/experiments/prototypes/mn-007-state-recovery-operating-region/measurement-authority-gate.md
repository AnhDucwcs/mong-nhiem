# MN-007 — Static Executor and Measurement-Authority Gate

## Status and authorization boundary

**`mn007_static_measurement_authority_frozen`**

This is a pre-measurement static authority gate. It freezes the exact model, runtime,
sampling, grammar, evaluator, corpus binding, deterministic request order, raw-response
persistence, interruption/failure semantics, composite machine-readable authority, and
clean-environment preflight for MN-007.

**No model is loaded. No llama.cpp server is spawned. No inference loop is run. No
calibration request is sent. No measured calibration evidence exists. No cell is scored
or classified. Status remains strictly pre-measurement.**

All previous milestone evidence (MN-003, MN-004, MN-005, MN-006) remains immutable.
MN-006 remains closed at `measurement_interface_blocked`. Locality remains unmeasured.
This gate does not authorize a locality comparison, intervention, or model search.

---

## 0. Evidence classification taxonomy

To ensure absolute auditability, every field in this gate is classified into one of five
evidence tiers:

1. **`[VERIFIED FROM RETAINED EVIDENCE]`**: Directly proven by committed historical
   artifacts in MN-002, MN-006, or MN-007 materialization.
2. **`[VERIFIED FROM EXACT RUNTIME SOURCE]`**: Directly verified from source code and header
   definitions of the qualified llama.cpp binary at commit `bb4caa754` (`common/common.h`, `common/arg.cpp`, `tools/server/server.cpp`).
3. **`[VERIFIED DIRECTLY FROM CURRENT STATIC FILESYSTEM]`**: Physically hashed and
   verified directly from local binary/source bytes during this static gate without runtime execution.
4. **`[FROZEN DERIVATION]`**: Pure deterministic derivation from verified evidence,
   guaranteed by frozen algorithms and unit tests.
5. **`[FROZEN EXECUTION CONTRACT]`**: Explicit invariant and preflight constraint contractually
   bound for execution integrity (e.g. forbidden environment clean state, zero retries).
6. **`[NOT PROVEN / BLOCKED]`**: Any unverified assumption or missing critical authority.
   *(There are zero critical authority fields in this tier; all requirements are fully proven).*

---

## 1. Exact model authority

Future calibration is bound to the qualified small-model capability baseline from MN-002
and MN-006:

| Field | Authority value | Evidence tier | Provenance / Verification |
| --- | --- | --- | --- |
| Model subject | `llama-3.2-3b` | `VERIFIED FROM RETAINED EVIDENCE` | Qualified baseline in MN-002 (MCB v0.3.0, overall 0.89 PASS). |
| Model name / family | Meta Llama 3.2 3B Instruct | `VERIFIED FROM RETAINED EVIDENCE` | Meta official architecture and weights. |
| Model file name | `Llama-3.2-3B-Instruct-Q4_K_M.gguf` | `VERIFIED FROM RETAINED EVIDENCE` | Canonical local GGUF candidate filename in MN-002 / MN-006. |
| Model path | `artifacts/models/mn-002/Llama-3.2-3B-Instruct-Q4_K_M.gguf` | `VERIFIED FROM RETAINED EVIDENCE` | Committed artifact repository location. |
| File size | `2,019,377,696` bytes | `VERIFIED DIRECTLY FROM CURRENT STATIC FILESYSTEM` | Exact physical byte length verified on disk. |
| Exact GGUF SHA-256 | `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff` | `VERIFIED DIRECTLY FROM CURRENT STATIC FILESYSTEM` | Physically computed via SHA-256 from file bytes. |
| Quantization | `Q4_K_M` | `VERIFIED FROM RETAINED EVIDENCE` | k-quant medium quantization format. |

No model replacement, weight modification, or alternate quantization is permitted. If the
physical file hash differs from the frozen SHA-256 above, execution is blocked.

---

## 2. Exact llama.cpp / runtime authority

Future calibration is bound to the qualified llama.cpp runtime identity from MN-006:

| Parameter | Authority value | Evidence tier | Provenance / Verification |
| --- | --- | --- | --- |
| Backend | `llama.cpp` (`llama-server`) | `VERIFIED FROM RETAINED EVIDENCE` | Local deterministic C++ inference runtime. |
| Executable path | `D:\Materials\llama.cpp\build\bin\Release\llama-server.exe` | `VERIFIED FROM RETAINED EVIDENCE` | Qualified binary location in MN-006. |
| Executable SHA-256 | `28d861538ffdf4e811e2febb0c5f06063792d184b66a2758f103c165629bc08` | `VERIFIED DIRECTLY FROM CURRENT STATIC FILESYSTEM` | Physically computed from executable bytes (10,752 bytes). |
| Version | `0.2.0-dev` | `VERIFIED FROM RETAINED EVIDENCE` | Qualified version string recorded in MN-006 metadata. |
| Build | `10566` | `VERIFIED FROM RETAINED EVIDENCE` | Build number in MN-006 metadata. |
| Commit | `bb4caa754` | `VERIFIED FROM RETAINED EVIDENCE` | Git commit hash in MN-006 metadata. |
| Compiler | `MSVC 19.44.35217.0 for x64` | `VERIFIED FROM RETAINED EVIDENCE` | Native MSVC build environment from MN-006 version output. |
| Context size (`-c`) | `16896` | `VERIFIED FROM RETAINED EVIDENCE` | Frozen runtime context parity with MN-006 direct-state-vector qualification. |
| CPU threads (`-t`) | `12` | `VERIFIED FROM RETAINED EVIDENCE` | Deterministic CPU worker allocation (`n_threads = 12`). |
| Batch size (`-b`) | `2048` | `VERIFIED FROM RETAINED EVIDENCE` | Prompt evaluation batch size in MN-006. |
| Parallel slots (`-np`) | `1` | `VERIFIED FROM RETAINED EVIDENCE` | Single slot (`n_slots = 1`), avoiding multi-tenant interference. |
| Flash Attention (`-fa`) | `on` | `VERIFIED FROM RETAINED EVIDENCE` | Identical to MN-006 runtime authority. |
| Prompt cache | `disabled` (`--no-cache-prompt`) | `VERIFIED FROM RETAINED EVIDENCE` | Eliminates cross-request KV-cache leakage or carryover. |
| Chat template | `--jinja` | `VERIFIED FROM RETAINED EVIDENCE` | Native GGUF embedded Jinja chat template rendering. |
| Web UI | `disabled` (`--no-webui`) | `VERIFIED FROM RETAINED EVIDENCE` | Prevents UI background polling or threads. |
| Metrics | `enabled` (`--metrics`) | `VERIFIED FROM RETAINED EVIDENCE` | Server timing and token metric logging. |
| GPU offload flag | `-ngl auto` | `VERIFIED FROM RETAINED EVIDENCE` | In retained MN-006 `server-lifecycle.json`, `environment_at_ready` recorded `llama-server.exe` as GPU compute process using `2267 MiB` VRAM, and `environment_before_cleanup` recorded `2289 MiB` and `14%` GPU utilization. In `bb4caa754` source (`common.h:465`, `arg.cpp:2765-2768`), `n_gpu_layers = -1` defaults to `'auto'` offload via `fit.cpp`. Absence of `-ngl` executes auto layer offload, NOT CPU-only execution. Explicit `-ngl auto` binds identical C++ `-1` parameter. |
| GPU device audit | NVIDIA GeForce RTX 3050 Laptop GPU (driver `595.95`, 4096 MiB VRAM) | `VERIFIED FROM RETAINED EVIDENCE` | Qualified GPU device in MN-006. Preflight requires 0 MiB used and 0% utilization prior to server launch. |

### Execution-relevant GPU defaults (`bb4caa754` source verification)

| Parameter | Authority value | Evidence tier | Provenance / Verification |
| --- | --- | --- | --- |
| GPU layer mode (`n_gpu_layers`) | `-1` (`"auto"`) | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:465`, `arg.cpp:2765`. Fits layers into VRAM with target margin. |
| Device selection (`devices`) | `[]` (auto / default discrete GPU) | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:463`, `arg.cpp:2719`. Binds to device index 0 (`RTX 3050 Laptop GPU`). |
| Split mode (`split_mode`) | `layer` (`LLAMA_SPLIT_MODE_LAYER`) | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:475`, `arg.cpp:2785`. Standard pipelined layer split across GPUs. |
| Main GPU (`main_gpu`) | `0` | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:466`, `arg.cpp:2834`. Primary GPU device index. |
| Tensor split (`tensor_split`) | `null` (default `{0}`) | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:467`, `arg.cpp:2824`. No manual tensor proportion partitioning. |
| KV offload (`no_kv_offload` / `offload_kqv`) | `enabled` (`offload_kqv = true`) | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:568`, `common.cpp:1721`, `arg.cpp:2406`. KV cache offloading enabled. |
| Parameter fitting (`fit_params`) | `true` (`on`) | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:468`, `arg.cpp:2844`. Automatic adjustment of unset parameters. |
| Fit target margin (`fit_params_target`) | `1024 MiB` | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:473`, `arg.cpp:2873`. Memory headroom margin per device. |
| Fit minimum context (`fit_params_min_ctx`) | `4096` | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:470`, `arg.cpp:2897`. Lower bound context for fitting. |
| Load mode (`load_mode`) | `auto` (`LLAMA_LOAD_MODE_AUTO`) | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:476`, `arg.cpp:2687`. Memory map with device fallback. |
| Op offload (`no_op_offload`) | `enabled` (`no_op_offload = false`) | `VERIFIED FROM EXACT RUNTIME SOURCE` | `common.h:569`, `arg.cpp:2924`. Host tensor operations offloaded to device. |

Server invocation command:

```powershell
D:\Materials\llama.cpp\build\bin\Release\llama-server.exe `
  -m D:\Code\mong-nhiem\artifacts\models\mn-002\Llama-3.2-3B-Instruct-Q4_K_M.gguf `
  --host 127.0.0.1 `
  --port 18501 `
  -c 16896 `
  -t 12 `
  -b 2048 `
  -ub 512 `
  -np 1 `
  -fa on `
  -ngl auto `
  -sm layer `
  -mg 0 `
  --fit on `
  --fit-target 1024 `
  --fit-ctx 4096 `
  --kv-offload `
  --op-offload `
  --load-mode auto `
  --temp 0 `
  --seed 42 `
  --jinja `
  --no-webui `
  --no-cache-prompt `
  --metrics `
  --chat-template-kwargs "{}"
```

### 2.1 Runtime environment precedence and hermetic isolation contract

In `llama.cpp` commit `bb4caa754` (`common/arg.cpp:763-830`), option resolution inside
`common_params_parse_ex()` follows strict three-stage precedence:

1. **System configuration file**: `common_params_apply_system_config(ctx_arg, params)`
2. **Environment variables**: `get_value_from_env(ctx_arg.options)`
3. **Command-line arguments**: `parse_cli_args(ctx_arg, params, argc, argv)`

**Precedence rule**: CLI arguments execute last and overwrite any values set by environment
variables or configuration files. Explicitly passing CLI arguments (`-ngl auto`, `-sm layer`,
`-mg 0`, `--fit on`, etc.) guarantees override against matching ambient `LLAMA_ARG_*` variables.

**Hermetic defense-in-depth contract**:
While explicit CLI flags override their specific counterparts, unpassed flags could still be
silently mutated by ambient environment variables (e.g. speculative decoding, drafting, context
shifting, caching). To enforce absolute hermetic isolation, MN-007 freezes:

- **`forbidden_env_vars_must_be_unset: true`** `[FROZEN EXECUTION CONTRACT]`
- Any environment variable starting with the prefix `LLAMA_` (including negative aliases derived as `LLAMA_ARG_NO_*`) is strictly forbidden.
- Execution-relevant variables including `CUDA_VISIBLE_DEVICES`, `GGML_CUDA_NO_PINNED`, `LLAMA_APP_CMD`, etc. must be explicitly unset or strictly evaluated before launch.
- **Configuration files forbidden**: `llama.cpp` parses configuration from `%PROGRAMDATA%\llama.cpp\config.ini` and `%APPDATA%\llama.cpp\config.ini`. The executor must resolve these paths and assert both are absent, failing closed if either exists (`required_config_files_absent: true`).
- **Executor contract**: The future executor must use an explicit array for `argv` (prohibiting shell tokenization and environment mutation).
---

## 3. Frozen sampling authority and parameter classification

Every sampling parameter is classified to distinguish actual runtime parameters from derived/effective sampler behaviors:

| Parameter | Frozen value | Classification | Evidence / Rationale |
| --- | --- | --- | --- |
| `temperature` | `0.0` | `explicit request and runtime arg` | Sent in request payload and passed via `--temp 0` to llama-server. Engages greedy argmax decoding via `llama_sampler_temp_impl`. |
| `seed` | `42` | `explicit request and runtime arg` | Sent in request payload and passed via `--seed 42` to llama-server. |
| `max_tokens` | `16` | `explicit request payload` | Sent in request payload (MN-006 `results.jsonl`). |
| `grammar` | `root ::= state "," state\nstate ::= "S0" \| "S1" \| "S2"\n` | `explicit request payload` | Sent in request payload (`mn007-bare-ordered-two-state-vector-v1`). |
| `messages` | `[{"role": "user", "content": "<prompt>"}]` | `explicit request payload` | Standard user chat completion turn. |
| `chat_template_kwargs` | `{}` | `explicit request and runtime arg` | Passed in request payload and `--chat-template-kwargs "{}"`. |
| `stream` | `false` | `explicit request payload` | Complete single HTTP response body expected; streaming disabled. |
| `top_k` | `40` | `runtime default` | In build 10566 (`common.h:229`), runtime default is `top_k = 40`. `temperature = 0.0` engages greedy argmax, pruning the candidate set to 1 token, but the underlying parameter value is 40. |
| `top_p` | `0.95` | `not applicable / inactive` | Inactive under greedy decoding. |
| `min_p` | `0.05` | `not applicable / inactive` | Inactive under greedy decoding. |
| `typical_p` | `1.0` | `not applicable / inactive` | Inactive under greedy decoding. |
| `repetition_penalty` | `1.0` | `not applicable / inactive` | Disabled / inactive under greedy decoding. |
| `frequency_penalty` | `0.0` | `not applicable / inactive` | Disabled / inactive under greedy decoding. |
| `presence_penalty` | `0.0` | `not applicable / inactive` | Disabled / inactive under greedy decoding. |
| `mirostat` | `0` | `not applicable / inactive` | Disabled. |
| `stop` | `grammar EOS + GGUF EOS` | `deterministic runtime default` | Managed by grammar completion and GGUF EOS tokens (`<|eot_id|>`, `<|end_of_text|>`). |

### Effective sampling behavior

- **Effective sampler mechanism:** `greedy_argmax_due_to_temperature_zero`
- **Candidate set size:** Exactly 1 token
- **Sampler chain execution:** `penalties -> dry -> top_n_sigma -> top_k(40) -> typical_p -> top_p -> min_p -> xtc -> temp(0.0)`. At `temp <= 0.0`, `llama_sampler_temp_impl` selects the maximum logit token and assigns $-\infty$ to all remaining candidate logits.

---

## 4. Evaluator authority

Evaluation is strictly deterministic and bound to the frozen materialization contract:

| Component | Identifier / Value | Evidence tier |
| --- | --- | --- |
| Grammar ID | `mn007-bare-ordered-two-state-vector-v1` | `VERIFIED FROM RETAINED EVIDENCE` |
| Grammar definition | `root ::= state "," state\nstate ::= "S0" \| "S1" \| "S2"\n` | `VERIFIED FROM RETAINED EVIDENCE` |
| Grammar SHA-256 | `717e29f7e3081b13a47b402ad8a007d3b5e03c626da05e2cca7d6c3d84a46ceb` | `VERIFIED DIRECTLY FROM CURRENT STATIC FILESYSTEM` |
| Strict parser | Trims leading/trailing ASCII whitespace; requires exactly one comma and two tokens from `("S0", "S1", "S2")`. Returns `tuple[str, str]` or `None`. | `VERIFIED FROM RETAINED EVIDENCE` |
| Evaluator schema | `mn007-evaluator-oracle-v1` | `VERIFIED FROM RETAINED EVIDENCE` |
| Scoring rule | Exact ordered vector match `parsed == expected` -> `score = 1.0`, else `0.0`. | `VERIFIED FROM RETAINED EVIDENCE` |
| Evaluator corpus SHA-256 | `c88d0ed7d5ded70987e3468917df7e658a40d31b34ad5c4eac6fc10ec69392fa` | `VERIFIED FROM RETAINED EVIDENCE` |

---

## 5. Corpus authority

Future calibration binds directly to the canonical materialized corpus:

- Contract document: `8fad7292d18b56c89ae15d4a7b87a3260008316cc1975348995c8dd9c18c9a61` `[VERIFIED FROM RETAINED EVIDENCE]`
- Root-seed text: `d97d50f4f1b396d13203e91241979945c2787e07a8adeffa5eb13ccc7361a31b` `[VERIFIED FROM RETAINED EVIDENCE]`
- Materializer source: `10e9c39be234ae320e74a70f251206b11246b95555f71b9f0602abf88b1a25ac` `[VERIFIED FROM RETAINED EVIDENCE]`
- Semantic corpus (`semantic-cases.jsonl`): `61ca3269dd948846345831aaa054385d2e2dca03e8a601df3226c0b5dde3f941` `[VERIFIED FROM RETAINED EVIDENCE]`
- Public prompt corpus (`public-prompts.jsonl`): `e3f6ec3881a5d2d98dc702adf1b9085536bca02f4413142cb0e8e7a221541353` `[VERIFIED FROM RETAINED EVIDENCE]`
- Evaluator corpus (`evaluator-records.jsonl`): `c88d0ed7d5ded70987e3468917df7e658a40d31b34ad5c4eac6fc10ec69392fa` `[VERIFIED FROM RETAINED EVIDENCE]`
- Manifest physical bytes (`manifest.json`): `98f30163d72696fac1b14d849fbcdcf9c93c03f5f292d0dfb4c8d50997bfae49` `[VERIFIED FROM RETAINED EVIDENCE]`
- Manifest core: `380da885870e234ba6c9935622096d054e0b9e78ed7755d9add6c660fd974194` `[VERIFIED FROM RETAINED EVIDENCE]`

No corpus regeneration is permitted.

---

## 6. Deterministic request-order authority

### Contract: `mn007-interleaved-cell-round-robin-v1` `[FROZEN DERIVATION]`

The 108 requests are partitioned into exactly 18 strata (waves) of 6 requests each. In wave
`k ∈ [1..18]`, one case of ordinal `k` is requested from each cell in the fixed canonical
cell order:

```text
for k = 1 .. 18:
    mn007-calibration-v1-e3-terminal-c{k:02d}
    mn007-calibration-v1-e3-leading-c{k:02d}
    mn007-calibration-v1-e5-terminal-c{k:02d}
    mn007-calibration-v1-e5-leading-c{k:02d}
    mn007-calibration-v1-e7-terminal-c{k:02d}
    mn007-calibration-v1-e7-leading-c{k:02d}
```

For request ordinal `r ∈ [0..107]`:
- `wave = (r // 6) + 1` (1 to 18)
- `cell_idx = r % 6` (0 to 5)
- `cell = CELLS[cell_idx]`
- `case_id = f"{cell.cell_id}-c{wave:02d}"`

**Frozen Request-Order Sequence SHA-256**:
`93d578e5a24903e826f2ad0481a420d219e53be30e2e4a822d9c3fdc0a96b474` `[FROZEN DERIVATION]`

---

## 7. Raw-response persistence authority

### Principle: `persist-before-evaluate`

Raw model outputs must be committed to durable storage before passing to the parser/evaluator.
The evaluator must never be the sole store of raw output.

1. Upon receiving an HTTP 200 response payload from `llama-server`:
   Create record containing:
   - `record_id`: case ID string
   - `request_ordinal`: 1-based integer `1..108`
   - `case_id`: canonical case ID
   - `public_prompt_sha256`: SHA-256 of public prompt text
   - `raw_request_payload`: JSON object sent to `/v1/chat/completions`
   - `raw_response_payload_utf8`: raw text returned by the server
   - `raw_output`: `choices[0].message.content`
   - `model`: model metadata and SHA-256
   - `runtime`: runtime metadata and SHA-256
   - `timing`: request latency in milliseconds
   - `usage`: token counts
   - `persistence_status`: `"persisted_unverified_evaluation"`
2. Write record to `raw-responses.jsonl`, invoke `flush()` and `os.fsync()`.
3. Only after `os.fsync()` succeeds, invoke the strict vector parser.
4. If output is malformed or invalid, the raw response is safely persisted; the evaluator
   records `{"malformed": true, "correct": false, "score": 0.0}`. It is never discarded.

---

## 8. Complete interruption and failure semantics

### Request state taxonomy and terminal behaviors

| State | Condition | Terminal behavior |
| --- | --- | --- |
| `not_started` | Socket connection not initiated. | May proceed to dispatch if no preceding ambiguity exists. |
| `sent_unconfirmed` | Socket dispatched, but connection dropped, timed out, or interrupted before full response buffered. | **RUN FAILS CLOSED IMMEDIATELY.** Status: `measurement/design blocked`. **Rerun/retry is strictly prohibited.** |
| `response_received` | Full HTTP 200 response body buffered in memory. | Must immediately proceed to persistence before evaluation. |
| `persisted` | Bytes written to `raw-responses.jsonl` and confirmed via `os.fsync()`. | Eligible for strict evaluation. |
| `evaluated` | Parsed and scored against expected vector oracle. | Measured case result recorded. |
| `invalid_ambiguous` | JSON parse error of HTTP body, protocol framing error, or schema mismatch. | **RUN FAILS CLOSED IMMEDIATELY.** Status: `measurement/design blocked`. |

### Execution limits and timeout policy

| Limit | Frozen value | Evidence tier | Provenance / Verification |
| --- | --- | --- | --- |
| Request timeout | `120` seconds | `VERIFIED FROM RETAINED EVIDENCE` | MN-006 `run_mn006_baseline.py:54` (`request_timeout_seconds: 120`). |
| Health / startup deadline | `180` seconds | `VERIFIED FROM RETAINED EVIDENCE` | MN-006 `run_mn006_baseline.py:55` (`health_deadline_seconds: 180`). |
| Timeout retry policy | `prohibited` | `FROZEN DERIVATION` | Zero retries. Timeout terminates run as `measurement/design blocked`. |
| Execution cardinality | `strictly exactly-once` | `FROZEN DERIVATION` | 1 request per case. Never retried. |

### Specific failure policies:
- **Persistence failure (`os.fsync` fails / disk error):** Calibration aborts immediately as `measurement/design blocked`. No evaluation is permitted. No retry.
- **Evaluator failure:** If raw response was persisted but evaluator raises an unhandled exception: calibration aborts as `measurement/design blocked`. Do not rerun request.
- **Malformed model output:** Persisted intact, scored as `0.0`. It is a valid capability measurement result, NOT an infrastructure failure, and MUST NOT trigger a retry.
- **Strictly Exactly-Once:** Every calibration request is sent at most once. No automatic retry, timeout retry, per-cell retry, or selective rerun is permitted under any circumstance.

---

## 9. Clean-environment preflight

### Distinction between Specification and Execution:
- **This static gate** freezes the preflight checklist specification.
- **Actual preflight validation** is executed at the start of the future calibration execution task.

Preflight checklist requirements:
1. Exact model file exists and SHA-256 equals `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`.
2. Exact runtime binary exists and SHA-256 equals `28d861538ffdf4e811e2febb0c5f06063792d184b66a2758f103c165629bc08`.
3. Working tree is clean on branch `codex/mn-007-state-recovery-operating-region`.
4. Corpus artifacts validate against all frozen manifest SHA-256 fingerprints.
5. GPU state: NVIDIA GeForce RTX 3050 Laptop GPU, memory used = `0 MiB`, GPU utilization = `0%`, no compute processes (must be verified prior to server launch).
6. Process state: No existing `llama-server.exe`, `llama-bench.exe`, or rogue inference processes.
7. Workload state: All games, heavy GPU applications, and compute-heavy background tasks must be terminated.
8. Environment state: All `LLAMA_*` environment variables, and exact execution-relevant variables (e.g. `CUDA_VISIBLE_DEVICES`, `GGML_CUDA_NO_PINNED`), must be unset (`forbidden_env_vars_must_be_unset = true`).
9. Configuration state: `%PROGRAMDATA%\llama.cpp\config.ini` and `%APPDATA%\llama.cpp\config.ini` must be absent.

---

## 10. Composite authority identity and machine-readable artifact

### Machine-readable artifact: `measurement-authority.json`

The authority is materialized as canonical JSON in `measurement-authority.json` at the
experiment root.

### Self-reference prohibition rule:
The composite fingerprint is computed from canonical bytes of `authority_core` (all fields
excluding `authority_core_sha256`).

- **Authority ID**: `mn007-calibration-measurement-authority-v1`
- **Authority Version**: `1.0.0`
- **Composite Core SHA-256**: `3995bafded4d01539c493d71c217ba97a5a1b8a0b99a5bf50f1a239b8a54146d` `[FROZEN DERIVATION]`
- **Physical File SHA-256**: `2694d45d2b7116e1abc6fc6b4bfcfa4a3db36ca2a001b188d8e484d537273b7e` `[FROZEN DERIVATION]`

Canonical serialization rules:
- UTF-8 without BOM.
- NFC normalized.
- Recursively Unicode-code-point-sorted JSON object keys.
- Compact separators (`","`, `":"`).
- Preserved integer, string, boolean types.
- Exactly one terminal LF (`\n`).
- Lowercase hexadecimal SHA-256.

---

## 11. Explicit prohibition of adaptive behavior

The following behaviors are strictly prohibited during calibration:
- Tuning sampling or decoding parameters after observing any output.
- Adjusting context window or batch size based on observed latency or accuracy.
- Modifying prompts, instructions, or grammar between runs.
- Skipping cases, reordering requests, or selecting subsets.
- Retrying failed, timed-out, or malformed cases.
- Regenerating or substituting corpus items.
- Modifying evaluator or oracle logic post hoc.
- Switching models, GGUF files, or llama.cpp versions.
- Adjusting thresholds or cell boundaries after observing scores.

Calibration is a fixed prospective protocol executed exactly once.

---

## 12. Future executor boundary and next authorization

This task freezes the measurement authority only. It creates no executor, runs no server,
and collects no responses.

The execution boundary is:
```text
frozen authority -> clean-environment preflight -> executor -> raw persistence -> evaluator
```

The future executor will be authorized under a separate task. Its responsibility will be
limited to executing the 108 requests in frozen order and persisting raw responses before
evaluation.
