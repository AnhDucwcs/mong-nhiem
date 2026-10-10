# Gate B Evaluation Contract: Milestone MN-018
## Stateful Simulated Microworld Evolution

### 1. Evaluation Arms & Comparative Configuration

| Parameter | Arm 1: Raw Unassisted Agent | Arm 2: Naive Tool Agent | Arm 3: Full Mộng Nhiễm Cognitive Host Stack |
|---|---|---|---|
| **Context Assembly** | Sliding FIFO token window | Raw prompt + unpruned tool returns | Scoped Context Packing + Scaffolding ($\le 512$ tok) |
| **Decoding Steering** | Free-form unconstrained generation | Basic JSON/regex tool format | Native GBNF Dynamic Phase-Gate logit masking |
| **Mission Planning** | Flat natural language instruction | Static step checklist | Topological Mission DAG with Host symbolic gates |
| **State Authority** | Model self-declares world state | Client executes without version check | Host Concurrency Guard + Delta Notices ($v_{\text{agent}} == v_{\text{world}}$) |
| **Physical Invariants** | Unenforced (hallucinates values) | Unenforced (accepts invalid states) | Host Conservation Guard (mass/energy balance checks) |
| **Memory Archiving** | None (FIFO context truncation) | None (FIFO context truncation) | Host Episodic Log + AutoDream Consolidation |
| **Fault Recovery** | None (fatal exception or loops) | Naive fixed retry loop | Host Memento Rollback + Negative Action Directives |

### 2. Quantitative Acceptance Thresholds

To achieve formal Gate B pass, Arm 3 must satisfy all of the following empirical criteria across the frozen 30-case benchmark:

| Metric ID | Metric Description | Mathematical Formulation | Acceptance Threshold | Evaluation Track |
|---|---|---|:---:|:---:|
| **M1** | Task Completion Rate | $\text{Accuracy}(\text{Arm 3}) = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{TaskSuccess}_i)$ | $\ge 90.0\%$ ($27/30$) | Track 1 & Track 2 |
| **M2** | Comparative Efficacy Margin | $\Delta \text{Accuracy} = \text{Accuracy}(\text{Arm 3}) - \text{Accuracy}(\text{Arm 1})$ | $\ge +50.0\%$ | Track 1 & Track 2 |
| **M3** | Conservation Law Violations | $\text{BreachRate} = \frac{\text{Committed Breaches}}{\text{Total Action Attempts}}$ | $= 0.0\%$ | Track 1 & Track 2 |
| **M4** | Stale Version Commit Rate | $\text{StaleCommitRate} = \frac{\text{Committed Stale Overwrites}}{\text{Total Action Attempts}}$ | $= 0.0\%$ | Track 1 & Track 2 |
| **M5** | AutoDream Consolidation Ratio | $\text{CompRatio} = 1.0 - \frac{\text{Tokens}(\text{Consolidated Memory})}{\text{Tokens}(\text{Raw Episodic Events})}$ | $\ge 70.0\%$ | Track 1 & Track 2 |
| **M6** | Memory Contradiction Rate | $\text{ContradictionRate} = \frac{\text{Contradictory Fact Assertions}}{\text{Total Fact Assertions}}$ | $= 0.0\%$ | Track 1 & Track 2 |
| **M7** | Prompt Token Ceiling Bound | $\max_t(\text{PromptTokens}_t)$ | $\le 512\text{ tokens}$ | Track 2 |
| **M8** | Mean Prompt Token Budget | $\mathbb{E}[\text{PromptTokens}]$ | $\le 384\text{ tokens}$ | Track 2 |
| **M9** | Turn Latency SLA | $\mathbb{E}[\text{TurnLatency}]$ | $< 1000\text{ ms}$ | Track 2 |
| **M10** | Host Processing Overhead | $\max(\text{HostOverhead})$ | $< 10.0\text{ ms}$ | Track 1 & Track 2 |
| **M11** | Peak GPU VRAM Footprint | $\max(\text{VRAM}_{\text{GPU}})$ | $\le 3072\text{ MiB}$ ($3.0\text{ GB}$) | Track 2 |

### 3. Falsification & Termination Protocol

Evaluation will immediately trigger failure if any of the following occur:
1. **Physical Invariant Breach**: Any illegal state transition (e.g. negative energy, duplicated cargo item, destroyed mass) is successfully committed to the Host world state by Arm 3.
2. **Context Window Saturation**: Any Arm 3 forward pass exceeds 512 tokens.
3. **State Desynchronization**: The host permits an action planned against an obsolete entity version ($v_{\text{agent}} < v_{\text{world}}$) without interception.
4. **Catastrophic Latency Degeneracy**: Mean forward-pass turn latency exceeds 1000 ms on the primary evaluation hardware.

### 4. Hardware Environment & Runtime Specification

- **Primary Subject**: `Qwen3.5-2B-Q4_K_M.gguf` (MD5 / SHA-256 registered in `definition/pre-run-freeze-manifest.json`).
- **Secondary Reference Subjects**: `Llama-3.2-3B-Instruct-Q4_K_M.gguf` and `Qwen3-4B-Q4_K_M.gguf`.
- **Inference Server**: Local `llama-server.exe` (Release build, Vulkan/CPU acceleration, $T=0.0$, context size 2048).
- **Execution Tracks**:
  - **Track 1**: Deterministic Symbolic State Simulation across 30 cases.
  - **Track 2**: Real-Time Local LLM Inference across 30 cases.
