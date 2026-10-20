# Mộng Nhiễm

[English](README.md) | [Tiếng Việt](README_vi.md)

**Hạt nhân Điều phối Nhận thức Tối thượng cho Tương tác Vật lý - Không gian mạng và Thực thể Game Tự chủ.**

---

## 1. Nền tảng Kiến trúc (Architectural Foundations)

Mộng Nhiễm cung cấp một hạ tầng điều phối nhận thức hình thức (formal cognitive governance substrate) cho các tác nhân tương tác thời gian thực, thực thể game (NPC), và hệ thống điều khiển vật lý-không gian mạng (cyber-physical systems).

### 1.1 Nguyên lý Bất biến Host-Arbiter (Raison d'Être)
Các kiến trúc tác tử AI truyền thống thường trao cho mô hình ngôn ngữ lớn quyền ghi trực tiếp và tùy tiện vào bộ nhớ, trạng thái mô phỏng thế giới, cũng như quyền gọi công cụ. Đối với các mô hình trọng số mở cỡ nhỏ ($< 4\text{B}$ tham số), cách tiếp cận này thường xuyên dẫn đến hiện tượng trôi dạt trạng thái (state drift), nhảy cóc mục tiêu (horizon jumping), và sụp đổ cú pháp.

Mộng Nhiễm thiết lập một ranh giới kiến trúc phân tách tuyệt đối:
1. **Mô hình suy luận (LLM) là một khối tính toán hộp đen biệt lập, không đáng tin cậy.** Mô hình chỉ tiếp nhận ngữ cảnh bị chặn biên giới hạn ($\le 512$ tokens) và phát ra các đề xuất hành động. Trọng số mô hình được giữ nguyên vẹn tuyệt đối (zero fine-tuning, không can thiệp trọng số).
2. **Hạt nhân Host nắm quyền phán quyết trạng thái tối thượng (Host-Authoritative State Arbiter).** Host kiểm soát toàn bộ tiến trình biến đổi trạng thái vật lý, các định luật bảo toàn, dòng chảy thời gian ($\Delta t$), cơ chế quay lui trạng thái tất định (Mementos), và cơ chế ngắt mạch can thiệp khẩn cấp.

### 1.2 Các Nguyên lý Kiến trúc Cốt lõi
- **Phát xạ Nhị thức Bất biến (Bimodal Emission Invariant):** Mỗi lượt suy luận của mô hình bắt buộc phải đồng thời phát sinh hai kênh song song (`ACTION: <verb> [params]` và `COMMUNICATE [<CLASS>]: "<message>"`). Cấu trúc ngữ pháp được ràng buộc trực tiếp ở cấp độ logits thông qua văn phạm phi ngữ cảnh GBNF, loại bỏ 100% lỗi cú pháp và ảo giác.
- **Trạng thái Liên tục & Rào chắn Ngắt mạch Phản xạ (Continuous State & Reflex Breakers):** Các chỉ số thực thể liên tục (pin, độ đói, nhiệt độ, năng lượng) tự động suy hao theo các phương trình vi phân biến thiên theo thời gian thực ($\Delta t$). Khi một chỉ số vi phạm ngưỡng an toàn, cơ chế ngắt mạch phản xạ của Host lập tức can thiệp và thực thi hành động phòng hộ khẩn cấp mà không cần chờ độ trễ phản hồi của LLM.
- **Quyền Can thiệp Giám sát của Con người (Human Supervisory Preemption):** Cầu nối giám sát tất định cho phép người vận hành can thiệp ngay lập tức (Standby, Pause, Override) giữa chu kỳ hoạt động.
- **Dò tìm Cổng Mạng Ngẫu nhiên Khả dụng (Zero-Conflict Ephemeral Port Hunting):** Cơ chế quản lý tiến trình con tự động kiểm tra socket hệ điều hành và cấp phát cổng trống ngẫu nhiên, triệt tiêu nguy cơ xung đột mạng với các dịch vụ khác (Database, Web server).
- **Chiến lược Đóng gói Kép:** 
  - Bản phân phối Python thuần chuẩn (100% Python Standard Library, không phụ thuộc bất kỳ thư viện ngoài nào).
  - Bản phân phối Native Rust hiệu năng cao xuất chuẩn C-ABI (`mong_nhiem.dll` / `libmong_nhiem.so`) cho các Game Engine (Godot, Unity, Unreal) và hệ thống nhúng.

---

## 2. Cài đặt & Phân phối (Installation & Distribution)

### 2.1 Bản phân phối Python (Dành cho AI Agents & Hệ thống Tự động hóa)

Bản Python yêu cầu môi trường Python 3.11+ và chỉ sử dụng thư viện chuẩn của hệ điều hành:

```powershell
# Cài đặt trực tiếp từ file wheel đã đóng gói (zero external dependencies)
pip install dist/mong_nhiem-0.2.0-py3-none-any.whl

# Hoặc cài đặt ở chế độ editable phục vụ phát triển
pip install -e ".[dev]"
```

Kiểm tra cài đặt:
```bash
python -c "import mong_nhiem; print(mong_nhiem.__name__, mong_nhiem.__version__)"
```

### 2.2 Bản phân phối Native Rust & C-ABI (Dành cho Game Engines & Runtimes Nhúng)

Mã nguồn Rust nằm tại `crates/mong_nhiem_core/`, biên dịch trực tiếp ra thư viện động C-ABI (`.dll`, `.so`, `.dylib`) và file header C để nhúng đa ngôn ngữ:

```powershell
# Biên dịch thư viện tối ưu hóa release và các artifact C-ABI
cargo build --release
```

Các artifact được sinh ra:
- **Thư viện liên kết động:** `target/release/mong_nhiem.dll` (Windows) hoặc `target/release/libmong_nhiem.so` (Linux).
- **File C Header:** `crates/mong_nhiem_core/include/mong_nhiem.h`.
- **Rust Crate:** Có thể đưa trực tiếp vào không gian làm việc Cargo:
  ```toml
  [dependencies]
  mong-nhiem-core = { path = "crates/mong_nhiem_core" }
  ```

---

## 3. Hướng dẫn Tích hợp Thực tế Từng bước (Step-by-Step Implementation)

### 3.1 Thực thể Tự chủ có Suy hao Trạng thái (Thú cưng Ảo / Bộ điều khiển Thiết bị)

Mô phỏng sự suy hao trạng thái vật lý theo thời gian thực và sự can thiệp ngắt mạch tự động khi chạm ngưỡng an toàn.

```python
from mong_nhiem import MockBackend, MongNhiemKernel

# Bước 1: Khai báo biến trạng thái liên tục và rào chắn an toàn
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

# Bước 2: Khởi tạo hạt nhân trong khối ngữ cảnh chuẩn (Context Manager)
with MongNhiemKernel(schema=schema, backend=MockBackend()) as kernel:
    # Chu kỳ định chuẩn: dt = 10s (hunger: 30 -> 50)
    step_1 = kernel.tick(stimulus="Kích thích đầu vào", delta_time=10.0)
    print(f"Tick 1 Action: {step_1.action_verb} | State: {step_1.state_snapshot}")

    # Chu kỳ vi phạm: dt = 20s (hunger: 50 -> 90 >= 80.0 -> Kích hoạt ngắt mạch Invariant)
    step_2 = kernel.tick(stimulus="Hoạt động thường", delta_time=20.0)
    print(f"Tick 2 Hành động ngắt mạch: {step_2.action_verb} | Invariant vi phạm: {step_2.fired_invariants}")
```

### 3.2 Quyền Can thiệp Giám sát của Con người & Dò Cổng Ngẫu nhiên

Mô phỏng việc tự động quản lý tiến trình con của backend suy luận, tự động cấp phát cổng tránh xung đột, và xử lý lệnh dừng khẩn cấp từ người giám sát.

```python
from mong_nhiem import MongNhiemKernel, SubprocessLlamaBackend

# Bước 1: Khởi tạo backend nội bộ với port=0 để tự động dò cổng trống
backend = SubprocessLlamaBackend(
    weights_path="./models/qwen2.5-3b-instruct.gguf",
    port=0,  # Hệ điều hành tự động cấp phát một cổng ngẫu nhiên khả dụng
)

kernel = MongNhiemKernel(
    schema="configs/assistant_schema.yaml",
    backend=backend,
)

# Bước 2: Người giám sát phát tín hiệu tạm dừng khẩn cấp
kernel.human_bridge.enter_standby(reason="Người giám sát yêu cầu tạm dừng chu trình")

# Bước 3: Chu kỳ tick lập tức hủy yêu cầu gửi đến mô hình, duy trì chế độ an toàn
result = kernel.tick(stimulus="Yêu cầu thực thi lệnh", delta_time=1.0)
assert result.in_standby is True
assert result.action_verb == "STANDBY"

kernel.close()
```

### 3.3 Nhúng vào Game Engine qua C# / C-ABI (Unity & Godot)

Tích hợp trực tiếp file native `mong_nhiem.dll` vào vòng lặp của Game Engine (`Update` trong Unity hoặc `_Process` trong Godot).

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
        // Đăng ký chỉ số mana suy hao 2.5 đơn vị mỗi giây
        mong_nhiem_register_variable(_kernel, "mana", 100.0, 0.0, 100.0, 2.5, 1);
    }

    public void UpdateNpc(float delta)
    {
        FfiStepResult res = new FfiStepResult();
        mong_nhiem_tick(_kernel, "ACTION: PATROL\nCOMMUNICATE [INFORM]: \"Đang tuần tra.\"", delta, ref res);

        string action = Marshal.PtrToStringAnsi(res.ActionVerb);
        string message = Marshal.PtrToStringAnsi(res.CommMessage);

        // Điều khiển chuyển động và hoạt cảnh trong game dựa trên quyết định từ kernel
        Console.WriteLine($"[Tick {res.Tick}] Hành động: {action} | Lời thoại: {message}");

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

## 4. Cấu trúc Các Phân hệ Thư viện (Subsystem Topology)

```
mong-nhiem/
├── src/mong_nhiem/              # Lõi sản xuất Python (100% Python Standard Library)
│   ├── kernel.py                # MongNhiemKernel: Façade hợp nhất điều phối toàn bộ phân hệ
│   ├── state/continuous.py      # ContinuousStateEngine: Suy hao vi phân & Ngắt mạch ngưỡng
│   ├── bimodal/                 # Bimodal parser & Trình biên dịch ngữ pháp động GBNF
│   ├── temporal/bridge.py       # TemporalBridge: Trọng tài đồng hồ thời gian thực và mô phỏng
│   ├── runtime/slot_cache.py    # SlotCacheManager: Tối ưu tiền tố bộ nhớ đệm KV và cách ly slot
│   ├── runtime/backends.py      # Các backend suy luận (llama-server, Ollama, Mock, auto-port)
│   ├── preemption/supervisory.py# HumanSupervisoryBridge: Can thiệp giám sát và cổng dừng khẩn cấp
│   ├── orchestration/           # Trọng tài tài nguyên, quay lui Memento, ngắt mạch phản xạ
│   ├── context/                 # Đóng gói ngữ cảnh & Phân tách AST mã nguồn giới hạn <= 512 tokens
│   └── knowledge/               # Đồ thị quan hệ nhân quả (DAG) & Đăng ký lược đồ động
│
├── crates/mong_nhiem_core/      # Lõi sản xuất Native Rust & Giao diện C-ABI
│   ├── src/lib.rs               # API công khai của Rust & Hệ thống kiểm thử tự động
│   ├── src/ffi.rs               # Các ký hiệu xuất C-ABI cho Godot, Unity, và môi trường C++
│   ├── src/state.rs             # Động cơ trạng thái vi phân native
│   ├── src/bimodal.rs           # Trình phân tích ngữ pháp nhị thức native
│   ├── src/kernel.rs            # Vòng lặp điều phối chu kỳ nhận thức native
│   └── include/mong_nhiem.h     # File C header tiêu chuẩn
│
└── research/                    # Kho tri thức Nghiên cứu Hình thức (Obsidian Vault)
    ├── 00-mong-nhiem.md         # Điểm truy cập trung tâm của kho tri thức
    ├── roadmap.md               # Sổ cái tiến trình thực nghiệm qua 27 mốc nghiên cứu
    ├── current-state.md         # Báo cáo hợp đồng đánh giá và phán quyết Gate B
    └── decisions/decisions.md   # Danh mục Quyết định Kiến trúc (ADRs)
```

---

## 5. Kiểm thử & Đảm bảo Chất lượng (Verification & Quality Assurance)

Mộng Nhiễm tuân thủ nguyên tắc không chấp nhận hồi quy (zero tolerance for unverified regression).

```powershell
# 1. Chạy toàn bộ bộ kiểm thử đơn vị và tích hợp của Python
python -m pytest tests/unit/ -v

# 2. Chạy bộ kiểm thử tự động của lõi native Rust
cargo test

# 3. Kiểm tra tính tuân thủ quy chuẩn mã nguồn PEP 8 / Ruff
ruff check src/ tests/
```

---

## 6. Giấy phép (License)

Dự án được phân phối dưới hình thức giấy phép kép: **Giấy phép MIT** và **Giấy phép Apache 2.0**.
