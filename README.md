# Mộng Nhiễm

[English](README.md) | [Tiếng Việt](README_vi.md)

**Authoritative cognitive governance and deterministic state-tracking kernel for small language models in dynamic environments.**

---

## 1. Architectural Foundations

Mộng Nhiễm provides a formal cognitive governance substrate for small open-weights language models (< 4B parameters) operating in real-time dynamic environments and cyber-physical systems.

### 1.1 The Host-Arbiter Invariant (Raison d'Être)
Traditional agentic frameworks grant generative language models unconstrained write authority over memory, simulation state, and tool invocation. Under small open-weights models (< 4B parameters), this paradigm experiences frequent state drift, horizon jumping, and syntactic collapse.

Mộng Nhiễm establishes a clear architectural separation:
1. **The Reasoning Engine (LLM) is an isolated black-box computation unit.** It receives bounded context ($\le 512$ tokens) and emits candidate acts. Model weights remain unaltered (zero fine-tuning, no weight modification).
2. **The Host Kernel acts as the authoritative state arbiter.** The Host governs continuous state evolution, physical conservation laws, time progression ($\Delta t$), deterministic state checkpointing (Mementos), and emergency preemption.

### 1.2 Core Architectural Invariants
- **Bimodal Emission Invariant:** Every generative forward pass produces a simultaneous dual-channel emission (`ACTION: <verb> [params]` and `COMMUNICATE [<CLASS>]: "<message>"`). Grammatical structure is constrained at the logit level via GBNF context-free grammars, eliminating parse failures.
- **Continuous State & Invariant Reflex Breakers:** Continuous physical and cognitive traits (battery, hunger, temperature, pressure) decay deterministically according to differential rate equations. When traits breach safety bounds, the Host reflex breaker immediately intercepts and executes failsafe actions without model latency.
- **Human Supervisory Preemption:** Deterministic preemption bridges allow external human supervisors to enforce immediate standby, pause, or state override conditions mid-cycle.
- **Zero-Conflict Ephemeral Port Hunting:** Autonomous subprocess management inspects system sockets and dynamically binds free ports, preventing network collisions with concurrent services.
- **Dual Packaging Strategy:** 
  - Pure Python distribution (100% Python Standard Library, zero external runtime dependencies).
  - High-performance native Rust core exporting a standardized C-ABI (`mong_nhiem.dll` / `libmong_nhiem.so`) for multi-language systems (C#, C++, Rust) and embedded daemons.

---

## 2. Installation & Distribution

### 2.1 Python Distribution (AI Agents & Systems Automation)

Requires Python 3.11+. Developers have two options:

#### Option 1: Direct Network Installation (Recommended - Zero Manual Downloads)
Pip autonomously clones and installs the package directly from GitHub:
```powershell
pip install git+https://github.com/AnhDucwcs/mong-nhiem.git
```

#### Option 2: Pre-built Wheel Archive Installation
1. Navigate to **[GitHub Releases](https://github.com/AnhDucwcs/mong-nhiem/releases)** and download `mong_nhiem-0.2.0-py3-none-any.whl`.
2. Open a terminal in the download folder and execute:
   ```powershell
   pip install mong_nhiem-0.2.0-py3-none-any.whl
   ```

Verify installation:
```bash
python -c "import mong_nhiem; print(mong_nhiem.__name__, mong_nhiem.__version__)"
```

---

### 2.2 Native Rust & C-ABI Distribution (Native Runtimes: C#, C++, Rust)

#### Option 1: Pre-compiled Shared Libraries (Zero Rust Toolchain Setup)
1. Navigate to **[GitHub Releases](https://github.com/AnhDucwcs/mong-nhiem/releases)** and download:
   - `mong_nhiem.dll` (Windows) or `libmong_nhiem.so` (Linux)
   - `mong_nhiem.h` (C-ABI header definitions)
2. Copy artifacts directly into your native project structure:
   - **C# / .NET:** Place `mong_nhiem.dll` in your binary output folder and load via `[DllImport]`.
   - **C / C++:** Include `mong_nhiem.h` and link against `mong_nhiem.dll`.

#### Option 2: Source Compilation
If customizing or targeting specialized hardware architectures:
```powershell
git clone https://github.com/AnhDucwcs/mong-nhiem.git
cd mong-nhiem
cargo build --release
```
Compiled artifacts are emitted to:
- `target/release/mong_nhiem.dll` (or `.so`)
- `crates/mong_nhiem_core/include/mong_nhiem.h`
- Rust Crate workspace reference:
  ```toml
  [dependencies]
  mong-nhiem-core = { path = "crates/mong_nhiem_core" }
  ```

---

## 3. Step-by-Step Practical Implementation

### 3.1 Autonomous State-Decaying Entity (Cyber-Pet / Robotic Controller)

Demonstrates real-time state decay and automatic reflex breaker interception when physical limits are breached.

```python
from mong_nhiem import MockBackend, MongNhiemKernel

# Step 1: Define continuous variables and safety invariants
schema = {
    "schema_name": "autonomous_entity",
    "continuous_traits": [
        {"name": "hunger", "initial_value": 30.0, "rate_per_sec": 2.0, "is_decay": False},
        {"name": "energy", "initial_value": 100.0, "rate_per_sec": 1.5, "is_decay": True},
    ],
    "invariants": [
        {"id": "inv_starvation", "condition": "hunger >= 80.0", "trigger_action": "FORCE_FEED"}
    ],
}

# Step 2: Initialize kernel within standard context manager
with MongNhiemKernel(schema=schema, backend=MockBackend()) as kernel:
    # Nominal tick: dt = 10s (hunger: 30 -> 50)
    step_1 = kernel.tick(stimulus="Stimulus arrival", delta_time=10.0)
    print(f"Tick 1 Action: {step_1.action_verb} | State: {step_1.state_snapshot}")

    # Breach tick: dt = 20s (hunger: 50 -> 90 >= 80.0 -> Invariant Triggered)
    step_2 = kernel.tick(stimulus="Nominal operation", delta_time=20.0)
    print(f"Tick 2 Intercepted Action: {step_2.action_verb} | Invariant: {step_2.fired_invariants}")
```

### 3.2 Human Supervisory Preemption & Dynamic Port Allocation

Demonstrates autonomous backend launching with automatic port hunting and human-in-the-loop supervisory preemption.

```python
from mong_nhiem import MongNhiemKernel, SubprocessLlamaBackend

# Step 1: Initialize local inference backend with port=0 for automatic port hunting
backend = SubprocessLlamaBackend(
    weights_path="./models/qwen2.5-3b-instruct.gguf",
    port=0,  # OS dynamically allocates an unused ephemeral port
)

kernel = MongNhiemKernel(
    schema="configs/assistant_schema.yaml",
    backend=backend,
)

# Step 2: External human supervisor signals an emergency standby
kernel.human_bridge.enter_standby(reason="Human supervisor paused execution")

# Step 3: Kernel tick aborts model forward pass, remaining in safe standby
result = kernel.tick(stimulus="Execute privileged operation", delta_time=1.0)
assert result.in_standby is True
assert result.action_verb == "STANDBY"

kernel.close()
```

### 3.3 Native Multi-Language Embedding (C# via C-ABI)

Demonstrates direct integration of `mong_nhiem.dll` into host application loops (such as C#, C++, or simulation runtimes).

```csharp
using System;
using System.Runtime.InteropServices;

public class NpcCognitiveController : IDisposable
{
    [StructLayout(LayoutKind.Sequential)]
    public struct FfiStepResult
    {
        public IntPtr ActionVerb;
        public IntPtr CommClass;
        public IntPtr CommMessage;
        public ulong Tick;
        public double DeltaTime;
        public IntPtr StateJson;
        public int HasFiredInvariants;
    }

    [DllImport("mong_nhiem.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern IntPtr mong_nhiem_kernel_new();

    [DllImport("mong_nhiem.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern void mong_nhiem_kernel_free(IntPtr kernel);

    [DllImport("mong_nhiem.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern int mong_nhiem_register_variable(
        IntPtr kernel, string name, double initial, double min, double max, double rate, int isDecay);

    [DllImport("mong_nhiem.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern int mong_nhiem_tick(
        IntPtr kernel, string stimulus, double deltaTime, ref FfiStepResult outResult);

    [DllImport("mong_nhiem.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern void mong_nhiem_free_step_result(ref FfiStepResult result);

    private IntPtr _kernel;

    public NpcCognitiveController()
    {
        _kernel = mong_nhiem_kernel_new();
        // Register mana decaying at 2.5 units per second
        mong_nhiem_register_variable(_kernel, "mana", 100.0, 0.0, 100.0, 2.5, 1);
    }

    public void UpdateNpc(float delta)
    {
        FfiStepResult res = new FfiStepResult();
        mong_nhiem_tick(_kernel, "ACTION: PATROL\nCOMMUNICATE [INFORM]: \"Patrolling\"", delta, ref res);

        string action = Marshal.PtrToStringAnsi(res.ActionVerb);
        string message = Marshal.PtrToStringAnsi(res.CommMessage);

        // Execute application logic based on authoritative kernel decisions
        Console.WriteLine($"[Tick {res.Tick}] Action: {action} | Message: {message}");

        mong_nhiem_free_step_result(ref res);
    }

    public void Dispose()
    {
        if (_kernel != IntPtr.Zero)
        {
            mong_nhiem_kernel_free(_kernel);
            _kernel = IntPtr.Zero;
        }
    }
}
```

---

## 4. Subsystem Topology

```
mong-nhiem/
├── src/mong_nhiem/              # Production Python Kernel (100% Python Standard Library)
│   ├── kernel.py                # MongNhiemKernel: Unified facade coordinating all subsystems
│   ├── state/continuous.py      # ContinuousStateEngine: Differential state decay & threshold triggers
│   ├── bimodal/                 # Bimodal emission parser and dynamic GBNF grammar compiler
│   ├── temporal/bridge.py       # TemporalBridge: Real-time and discrete simulated clock arbitration
│   ├── runtime/slot_cache.py    # SlotCacheManager: KV prefix cache optimization and slot isolation
│   ├── runtime/backends.py      # Inference backends (llama-server, Ollama, Mock, auto-port hunting)
│   ├── preemption/supervisory.py# HumanSupervisoryBridge: Supervisory intervention and standby gates
│   ├── orchestration/           # Resource arbiters, Memento snapshot rollback, reflex circuit breakers
│   ├── context/                 # Context Packer and AST Codebase Slicer bounded to <= 512 tokens
│   └── knowledge/               # Causal Event DAG and Dynamic Schema Registry
│
├── crates/mong_nhiem_core/      # Production Native Rust Kernel & C-ABI
│   ├── src/lib.rs               # Rust public API and automated test harnesses
│   ├── src/ffi.rs               # C-ABI export symbols for Godot, Unity, and C++ runtimes
│   ├── src/state.rs             # Native differential state engine
│   ├── src/bimodal.rs           # Native bimodal grammar parser
│   ├── src/kernel.rs            # Native cognitive tick coordination loop
│   └── include/mong_nhiem.h     # Standard C header file
│
└── research/                    # Formal Research Knowledge Base (Obsidian Vault)
    ├── 00-mong-nhiem.md         # Master knowledge base entrypoint
    ├── roadmap.md               # Empirical progression ledger across research milestones
    ├── current-state.md         # Authoritative evaluation contract dispositions
    └── decisions/decisions.md   # Architectural Decision Records (ADRs)
```

---

## 5. Verification & Quality Assurance

Mộng Nhiễm maintains zero tolerance for unverified regression.

```powershell
# 1. Execute full Python unit and integration test suite
python -m pytest tests/unit/ -v

# 2. Execute native Rust core test harness
cargo test

# 3. Verify PEP 8 / Ruff compliance
ruff check src/ tests/
```

---

## 6. License

This project is licensed under the dual **MIT License** and **Apache License 2.0**.
