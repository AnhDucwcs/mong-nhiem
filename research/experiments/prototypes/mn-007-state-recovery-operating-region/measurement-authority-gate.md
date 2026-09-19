# MN-007 — Static Executor and Measurement-Authority Gate

## Status and authorization boundary

**`mn007_static_measurement_authority_frozen`**

This is a pre-measurement authority gate. It freezes the exact model, runtime, sampling,
grammar, evaluator, corpus binding, deterministic request order, raw-response persistence,
interruption/failure semantics, and clean-environment preflight for MN-007.

**No model is loaded. No llama.cpp server is spawned. No inference loop is run. No
calibration request is sent. No measured calibration evidence exists. No cell is scored
or classified. Status remains strictly pre-measurement.**

All previous milestone evidence (MN-003, MN-004, MN-005, MN-006) remains immutable.
MN-006 remains closed at `measurement_interface_blocked`. Locality remains unmeasured.
This gate does not authorize a locality comparison, intervention, or model search.

---

## 1. Exact model authority

Future calibration is bound to the qualified small-model capability baseline from MN-002
and MN-006:

| Field | Authority value | Provenance / Verification |
| --- | --- | --- |
| Model subject | `llama-3.2-3b` | Qualified baseline in MN-002 (MCB v0.3.0, overall 0.89 PASS). |
| Model name / family | Meta Llama 3.2 3B Instruct | Meta official architecture and weights. |
| Model file name | `Llama-3.2-3B-Instruct-Q4_K_M.gguf` | Canonical local GGUF candidate filename. |
| Model path | `artifacts/models/mn-002/Llama-3.2-3B-Instruct-Q4_K_M.gguf` | Committed artifact repository location. |
| File size | `2,019,377,696` bytes | Exact physical byte length. |
| Exact GGUF SHA-256 | `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff` | Verified on physical file. |
| Quantization | `Q4_K_M` | k-quant medium quantization format. |

No model replacement, weight modification, or alternate quantization is permitted. If the
physical file hash differs from the frozen SHA-256 above, execution is blocked.

---

## 2. Exact llama.cpp / runtime authority

Future calibration is bound to the qualified llama.cpp runtime identity from MN-006:

| Parameter | Authority value | Rationale |
| --- | --- | --- |
| Backend | `llama.cpp` (`llama-server`) | Local deterministic C++ inference runtime. |
| Executable path | `D:\Materials\llama.cpp\build\bin\Release\llama-server.exe` | Qualified binary location. |
| Executable SHA-256 | `28d861538ffdf4e811e2febb0c5f06063792d184b66a2758f103c165629bc08` | Physical binary fingerprint. |
| Version | `0.2.0-dev` | Qualified version string. |
| Build | `10566` | Compiler build number. |
| Commit | `bb4caa754` | Exact Git commit hash of llama.cpp. |
| Compiler | `MSVC 19.44.35217.0 for x64` | Native MSVC build environment. |
| Context size (`-c`) | `16896` | Frozen runtime context parity with MN-006 direct-state-vector qualification. |
| CPU threads (`-t`) | `12` | Deterministic CPU worker allocation. |
| Batch size (`-b`) | `2048` | Prompt evaluation batch size. |
| Parallel slots (`-np`) | `1` | Strict single-tenant slot, avoiding multi-tenant interference. |
| Flash Attention (`-fa`) | `on` | Enabled, identical to MN-006 runtime authority. |
| Prompt cache | `disabled` (`--no-cache-prompt`) | Eliminates cross-request KV-cache leakage or carryover. |
| Chat template | `--jinja` | Native GGUF embedded Jinja chat template rendering. |
| Web UI | `disabled` (`--no-webui`) | Prevents unnecessary HTTP endpoints and background threads. |
| Metrics | `enabled` (`--metrics`) | Enables observability of server timings and prompt/predicted tokens. |
| GPU offload | Full offload to NVIDIA GeForce RTX 3050 Laptop GPU (driver `595.95`, 4096 MiB VRAM) | Parity with MN-006 execution environment. |

Server invocation command:

```powershell
D:\Materials\llama.cpp\build\bin\Release\llama-server.exe `
  -m D:\Code\mong-nhiem\artifacts\models\mn-002\Llama-3.2-3B-Instruct-Q4_K_M.gguf `
  --host 127.0.0.1 `
  --port 18501 `
  -c 16896 `
  -t 12 `
  -b 2048 `
  -np 1 `
  -fa on `
  --temp 0 `
  --seed 42 `
  --jinja `
  --no-webui `
  --no-cache-prompt `
  --metrics `
  --chat-template-kwargs "{}"
```

---

## 3. Frozen generation and sampling parameters

All generation parameters are frozen before calibration. No executor may adjust or tune
these values:

| Parameter | Frozen value | Rule / Constraint |
| --- | --- | --- |
| `temperature` | `0.0` | Deterministic greedy decoding (argmax). |
| `seed` | `42` | Frozen RNG seed. |
| `top_k` | `1` | Argmax selection (or inactive under `temperature=0.0`). |
| `top_p` | `1.0` | Unrestricted cumulative probability. |
| `min_p` | `0.0` | Disabled. |
| `typical_p` | `1.0` | Disabled. |
| `repetition_penalty` | `1.0` | Disabled (1.0 = no penalty). |
| `frequency_penalty` | `0.0` | Disabled. |
| `presence_penalty` | `0.0` | Disabled. |
| `mirostat` | `0` | Disabled. |
| `max_tokens` | `16` | Maximum output tokens (answer is a 5-character string, e.g. `S1,S2`). |
| `stop` | `["\n", "<|eot_id|>", "<|end_of_text|>"]` | Strict termination at newline or end-of-turn. |
| `chat_template_kwargs` | `{}` | No injected system instructions or template flags. |

---

## 4. Evaluator authority

Evaluation is strictly deterministic and bound to the frozen materialization contract:

| Component | Identifier / Value | Specification |
| --- | --- | --- |
| Grammar ID | `mn007-bare-ordered-two-state-vector-v1` | Bare ordered two-state vector grammar. |
| Grammar definition | `root ::= state "," state\nstate ::= "S0" | "S1" | "S2"\n` | Single LF terminal. |
| Strict parser | Trims leading/trailing ASCII whitespace; requires exactly one comma and two tokens from `("S0", "S1", "S2")`. | Returns `tuple[str, str]` or `None`. |
| Evaluator schema | `mn007-evaluator-oracle-v1` | Minimal oracle record schema. |
| Scoring rule | Exact ordered vector match `parsed == expected` -> `score = 1.0`, else `0.0`. | No partial credit, synonym, keyed form, or LLM judge. |
| Evaluator corpus SHA-256 | `c88d0ed7d5ded70987e3468917df7e658a40d31b34ad5c4eac6fc10ec69392fa` | Frozen physical file hash. |

Model-visible prompt text contains only the public prompt lines. Expected vectors, case IDs,
cell IDs, seeds, and oracle metadata remain evaluator-side only.

---

## 5. Corpus authority

Future calibration binds directly to the canonical materialized corpus:

- Contract document: `8fad7292d18b56c89ae15d4a7b87a3260008316cc1975348995c8dd9c18c9a61`
- Root-seed text: `d97d50f4f1b396d13203e91241979945c2787e07a8adeffa5eb13ccc7361a31b`
- Materializer source: `10e9c39be234ae320e74a70f251206b11246b95555f71b9f0602abf88b1a25ac`
- Semantic corpus (`semantic-cases.jsonl`): `61ca3269dd948846345831aaa054385d2e2dca03e8a601df3226c0b5dde3f941`
- Public prompt corpus (`public-prompts.jsonl`): `e3f6ec3881a5d2d98dc702adf1b9085536bca02f4413142cb0e8e7a221541353`
- Evaluator corpus (`evaluator-records.jsonl`): `c88d0ed7d5ded70987e3468917df7e658a40d31b34ad5c4eac6fc10ec69392fa`
- Manifest physical bytes (`manifest.json`): `98f30163d72696fac1b14d849fbcdcf9c93c03f5f292d0dfb4c8d50997bfae49`
- Manifest core: `380da885870e234ba6c9935622096d054e0b9e78ed7755d9add6c660fd974194`

No corpus regeneration is permitted.

---

## 6. Deterministic request-order authority

### Contract: `mn007-interleaved-cell-round-robin-v1`

Executing all 18 cases of one cell consecutively introduces temporal, thermal, and process
drift confounds across entity-load profiles. Calibration requests must be balanced across
the six cells throughout the entire run.

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

### Properties:
1. **Deterministic:** Pure arithmetic index mapping, independent of filesystem, discovery, or OS time.
2. **Strata Balance:** At any multiple of 6 completed requests, all 6 cells have identical sample sizes.
3. **Difficulty Balance:** In wave `k`, all six cells share the identical vector slot `(k-1) % 9`.
4. **Orientation Balance:** Waves 1–9 are all `source_order`; waves 10–18 are all `reverse_source_order`.
5. **Frozen Fingerprint:** The UTF-8 newline-separated list of 108 case IDs has SHA-256:
   `93d578e5a24903e826f2ad0481a420d219e53be30e2e4a822d9c3fdc0a96b474`

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

## 8. Interruption and failure semantics

### Request state taxonomy

Every request transitions through strictly bounded states:
- `not_started`: Request socket has not been opened.
- `sent_unconfirmed`: Request was dispatched over the socket, but connection closed, timed out,
  or interrupted before full response body was buffered.
  **CRITICAL RULE: Rerun is strictly prohibited.** If any request enters `sent_unconfirmed`,
  the entire calibration run aborts immediately as `measurement/design blocked`.
- `response_received`: Complete HTTP response body buffered in memory.
- `persisted`: Record written and confirmed on disk via `os.fsync()`.
- `evaluated`: Strict parser and expected-vector oracle executed.
- `invalid_ambiguous`: Socket or JSON corruption detected.

### Failure handling:
- **Server crash / process exit:** Calibration aborts immediately. Status: `measurement/design blocked`.
- **Timeout / network drop:** Calibration aborts immediately. Status: `measurement/design blocked`.
- **GPU error / OOM:** Calibration aborts immediately. Status: `measurement/design blocked`.
- **Malformed model output:** Measured score `0.0`. It is a valid capability measurement result,
  NOT an infrastructure failure, and MUST NOT trigger a retry.
- **Selective retries prohibited:** No selective retry of difficult, incorrect, timed-out,
  or malformed cases. Exactly-once execution is strictly enforced.

---

## 9. Clean-environment precondition (preflight)

Before executing calibration, the host environment must pass strict preflight checks:

1. Exact model file exists and SHA-256 equals `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`.
2. Exact runtime binary exists and SHA-256 equals `28d861538ffdf4e811e2febb0c5f06063792d184b66a2758f103c165629bc08`.
3. Working tree is clean on branch `codex/mn-007-state-recovery-operating-region`.
4. Corpus artifacts validate against all frozen manifest SHA-256 fingerprints.
5. GPU state: NVIDIA GeForce RTX 3050 Laptop GPU, memory used = `0 MiB`, GPU utilization = `0%`, no compute processes.
6. Process state: No existing `llama-server.exe`, `llama-bench.exe`, or rogue inference processes.
7. Workload state: All games, heavy GPU applications, and compute-heavy background tasks must be terminated.

---

## 10. Authority identity and version

Single composite authority identifier:
`mn007-calibration-measurement-authority-v1`

Binding tuple:
```text
(
  model: "llama-3.2-3b",
  model_file_sha256: "6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff",
  runtime_build: "10566",
  runtime_commit: "bb4caa754",
  runtime_binary_sha256: "28d861538ffdf4e811e2febb0c5f06063792d184b66a2758f103c165629bc08",
  runtime_flags: "-c 16896 -t 12 -b 2048 -np 1 -fa on --temp 0 --seed 42 --jinja --no-webui --no-cache-prompt --metrics",
  sampling: "temp=0.0,seed=42,max_tokens=16",
  grammar_id: "mn007-bare-ordered-two-state-vector-v1",
  evaluator_schema: "mn007-evaluator-oracle-v1",
  evaluator_corpus_sha256: "c88d0ed7d5ded70987e3468917df7e658a40d31b34ad5c4eac6fc10ec69392fa",
  manifest_core_sha256: "380da885870e234ba6c9935622096d054e0b9e78ed7755d9add6c660fd974194",
  request_order_contract: "mn007-interleaved-cell-round-robin-v1",
  request_order_sha256: "93d578e5a24903e826f2ad0481a420d219e53be30e2e4a822d9c3fdc0a96b474"
)
```

If any element changes, the authority version must change. Calibration under a modified
tuple represents a distinct authority.

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

## 12. Executor boundary and next authorization

This task freezes the measurement authority only. It creates no executor, runs no server,
and collects no responses.

The execution boundary is:
```text
frozen authority -> clean-environment preflight -> executor -> raw persistence -> evaluator
```

The future executor will be authorized under a separate task. Its responsibility will be
limited to executing the 108 requests in frozen order and persisting raw responses before
evaluation.
