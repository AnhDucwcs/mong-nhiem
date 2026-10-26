# Mộng Nhiễm

[English](README.md) | [Tiếng Việt](README_vi.md)

**Hạt nhân điều phối nhận thức và theo dõi trạng thái tất định cho các mô hình ngôn ngữ nhỏ trong môi trường động.**

---

## 1. Nền tảng Kiến trúc (Architectural Foundations)

Mộng Nhiễm cung cấp hạ tầng điều phối nhận thức hình thức (formal cognitive governance substrate) cho các mô hình ngôn ngữ mở cỡ nhỏ (< 4B tham số) vận hành trong môi trường tương tác thời gian thực và hệ thống vật lý-không gian mạng (cyber-physical systems).

### 1.1 Nguyên lý Bất biến Host-Arbiter (Raison d'Être)
Các kiến trúc tác tử AI truyền thống thường trao cho mô hình ngôn ngữ quyền ghi trực tiếp vào bộ nhớ, trạng thái mô phỏng thế giới, cũng như quyền gọi công cụ. Đối với các mô hình ngôn ngữ nhỏ (< 4B tham số), cách tiếp cận này thường xuyên dẫn đến hiện tượng trôi dạt trạng thái (state drift), sai lệch mục tiêu (horizon jumping), và lỗi cú pháp đầu ra.

Mộng Nhiễm thiết lập ranh giới phân tách rõ ràng:
1. **Mô hình suy luận (LLM) là khối tính toán hộp đen biệt lập.** Mô hình chỉ tiếp nhận ngữ cảnh có giới hạn ($\le 512$ tokens) và phát ra các đề xuất hành động. Trọng số mô hình được giữ nguyên (zero fine-tuning, không can thiệp trọng số).
2. **Hạt nhân Host đóng vai trò trọng tài trạng thái có thẩm quyền (Host-Authoritative State Arbiter).** Host kiểm soát toàn bộ tiến trình biến đổi trạng thái vật lý, các định luật bảo toàn, dòng chảy thời gian ($\Delta t$), cơ chế lưu và hoàn tác trạng thái (Mementos), cùng rào chắn can thiệp khẩn cấp.

### 1.2 Các Nguyên lý Kiến trúc Cốt lõi
- **Phát xạ Nhị thức Bất biến (Bimodal Emission Invariant):** Mỗi lượt suy luận của mô hình bắt buộc phải đồng thời phát sinh hai kênh song song (`ACTION: <verb> [params]` và `COMMUNICATE [<CLASS>]: "<message>"`). Cấu trúc ngữ pháp được ràng buộc trực tiếp ở cấp độ logits thông qua văn phạm phi ngữ cảnh GBNF, loại bỏ 100% lỗi cú pháp và ảo giác.
- **Trạng thái Liên tục & Rào chắn Ngắt mạch Phản xạ (Continuous State & Reflex Breakers):** Các chỉ số thực thể liên tục (pin, độ đói, nhiệt độ, áp suất) tự động suy hao theo các phương trình vi phân biến thiên theo thời gian thực ($\Delta t$). Khi một chỉ số vi phạm ngưỡng an toàn, cơ chế ngắt mạch phản xạ của Host lập tức can thiệp và thực thi hành động phòng hộ khẩn cấp mà không cần chờ độ trễ phản hồi của LLM.
- **Quyền Can thiệp Giám sát của Con người (Human Supervisory Preemption):** Cầu nối giám sát tất định cho phép người vận hành can thiệp ngay lập tức (Standby, Pause, Override) giữa chu kỳ hoạt động.
- **Dò tìm Cổng Mạng Ngẫu nhiên Khả dụng (Zero-Conflict Ephemeral Port Hunting):** Cơ chế quản lý tiến trình con tự động kiểm tra socket hệ điều hành và cấp phát cổng trống ngẫu nhiên, triệt tiêu nguy cơ xung đột mạng với các dịch vụ khác (Database, Web server).
- **Phân phối Thuần Python Chuẩn 100% (Pure Python Standard Library):** Không phụ thuộc bất kỳ thư viện ngoài nào (Zero external dependencies). Chỉ yêu cầu thư viện chuẩn của Python 3.11+, triệt tiêu hoàn toàn rào cản biên dịch C-ABI, rủi ro hỏng bộ nhớ FFI, và sự phân mảnh nhị phân trên các hệ điều hành khác nhau.

---

## 2. Cài đặt & Phân phối (Installation & Distribution)

Yêu cầu môi trường Python 3.11+. Người dùng có 2 cách cài đặt:

### Cách 1: Cài đặt trực tiếp qua mạng (Khuyến nghị — Không cần tải file thủ công)
Pip sẽ tự động clone mã nguồn từ GitHub và cài đặt vào môi trường của bạn:
```powershell
pip install git+https://github.com/AnhDucwcs/mong-nhiem.git
```

### Cách 2: Cài đặt từ file Wheel (`.whl`) đã đóng gói sẵn
1. Truy cập mục **[Releases trên GitHub](https://github.com/AnhDucwcs/mong-nhiem/releases)** và tải file `mong_nhiem-0.3.0-py3-none-any.whl` về máy.
2. Mở terminal tại thư mục chứa file vừa tải và chạy lệnh:
   ```powershell
   pip install mong_nhiem-0.3.0-py3-none-any.whl
   ```

Kiểm tra cài đặt:
```bash
python -c "import mong_nhiem; print(mong_nhiem.__name__, mong_nhiem.__version__)"
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

# Bước 2: Khởi tạo kernel trong context manager tiêu chuẩn
with MongNhiemKernel(schema=schema, backend=MockBackend()) as kernel:
    # Chu kỳ danh định: dt = 10s (hunger: 30 -> 50)
    step_1 = kernel.tick(stimulus="Kích thích môi trường", delta_time=10.0)
    print(f"Hành động chu kỳ 1: {step_1.action_verb} | Trạng thái: {step_1.state_snapshot}")

    # Chu kỳ chạm ngưỡng: dt = 20s (hunger: 50 -> 90 >= 80.0 -> Kích hoạt Rào chắn Phản xạ)
    step_2 = kernel.tick(stimulus="Vận hành danh định", delta_time=20.0)
    print(f"Hành động can thiệp: {step_2.action_verb} | Invariant: {step_2.fired_invariants}")
```

### 3.2 Quyền Giám sát của Con người & Tự động Cấp phát Cổng Mạng

Khởi động backend cục bộ an toàn, tự động dò cổng trống và cho phép người vận hành ép trạng thái Standby khẩn cấp.

```python
from mong_nhiem import MongNhiemKernel, SubprocessLlamaBackend

# Bước 1: Khởi tạo backend suy luận cục bộ với port=0 để hệ điều hành cấp cổng ngẫu nhiên
backend = SubprocessLlamaBackend(
    weights_path="./models/qwen2.5-3b-instruct.gguf",
    port=0,
)

kernel = MongNhiemKernel(
    schema="configs/assistant_schema.yaml",
    backend=backend,
)

# Bước 2: Người vận hành gửi tín hiệu dừng khẩn cấp
kernel.human_bridge.enter_standby(reason="Người giám sát tạm dừng hệ thống")

# Bước 3: Chu kỳ tick lập tức hủy yêu cầu gọi LLM và duy trì trạng thái an toàn
result = kernel.tick(stimulus="Yêu cầu lệnh đặc quyền", delta_time=1.0)
assert result.in_standby is True
assert result.action_verb == "STANDBY"

kernel.close()
```

### 3.3 Vận Hành Pipeline Hợp Nhất Toàn Diện (Unified End-to-End Pipeline)

Minh họa việc vận hành `MongNhiemKernel` tự động điều phối các chốt chặn chẩn đoán, chiếu trước quỹ đạo phòng ngừa deadlock, kiểm tra kép trạng thái thực tế tại thời điểm commit, và phân xử chống đói tài nguyên livelock.

```python
from mong_nhiem import MongNhiemKernel
from mong_nhiem.runtime.backends import MockBackend

# Bước 1: Khởi tạo kernel thẩm quyền với schema vật lý khai báo
kernel = MongNhiemKernel(
    schema="configs/reactor_core_schema.yaml",
    backend=MockBackend(),
)

# Bước 2: Một lệnh kernel.tick() duy nhất tự động kích hoạt đồng bộ các lớp bảo vệ:
# - Tích hợp trôi dạt vi mô sinh FactCard bền vững (AutoDream)
# - Ép phát lệnh PROBE khi gặp cảm biến kẹt gây mù nhận thức (Byzantine Equifinality)
# - Chiếu trước quỹ đạo 4 bước để chặn trước bẫy bế tắc (Lookahead Deadlock Avoidance)
# - Kiểm tra kép trạng thái vật lý tại thời điểm commit (Commit-Time Double-Check)
# - Phân xử chống đói tài nguyên livelock giữa các tác tử (Starvation-Free Arbitration)
result = kernel.tick(stimulus="Phát hiện dị thường phương sai cảm biến", delta_time=1.0)
print(f"Hành động thẩm quyền: {result.action_verb} | FactCards: {len(result.fact_cards)}")
```

---

## 4. Cấu trúc Hệ thống (Subsystem Topology)

```
mong-nhiem/
├── src/mong_nhiem/              # Hạt nhân Python Production (100% Python Standard Library)
│   ├── kernel.py                # MongNhiemKernel: Mặt tiền hợp nhất điều phối toàn bộ hệ thống con
│   ├── state/continuous.py      # ContinuousStateEngine: Suy hao vi phân & bộ kích hoạt ngưỡng an toàn
│   ├── bimodal/                 # Bộ phân tích phát xạ nhị thức & bộ sinh văn phạm GBNF động
│   ├── temporal/bridge.py       # TemporalBridge: Trọng tài thời gian thực và đồng hồ mô phỏng
│   ├── runtime/slot_cache.py    # SlotCacheManager: Tối ưu prefix KV cache và cô lập ngữ cảnh
│   ├── runtime/backends.py      # Backends suy luận (llama-server, Ollama, Mock, auto-port hunting)
│   ├── preemption/supervisory.py# HumanSupervisoryBridge: Can thiệp giám sát và cổng dừng khẩn cấp
│   ├── orchestration/           # LivelockDetector, phân xử tài nguyên, Memento rollback, rào chắn phản xạ
│   ├── context/                 # Context Packer & Bộ trích xuất AST giới hạn <= 512 tokens
│   ├── knowledge/               # Đồ thị Nhân quả Causal DAG, Abductive Tracer, Diagnostic Probe Enforcer
│   └── extensions/autodream/    # Theo dõi sai số vi mô tích lũy & sinh FactCard bền vững
│
└── research/                    # Kho Tri thức Nghiên cứu Hình thức (Obsidian Vault)
    ├── 00-mong-nhiem.md         # Điểm truy cập trung tâm kho tri thức
    ├── roadmap.md               # Sổ cái tiến trình kiểm chứng qua các mốc nghiên cứu
    ├── current-state.md         # Các trạng thái nghiệm thu hợp đồng Gate B/D có thẩm quyền
    └── decisions/decisions.md   # Bản ghi Quyết định Kiến trúc (ADRs)
```

---

## 5. Kiểm thử & Đảm bảo Chất lượng (Quality Assurance)

Mộng Nhiễm duy trì chính sách không khoan nhượng với bất kỳ lỗi hồi quy nào.

```powershell
# 1. Chạy toàn bộ 515 bài test đơn vị (Unit Tests)
python -m pytest tests/unit/ -v

# 2. Chạy 11 bài test đối kháng sức bền (Adversarial Stress Tests)
python -m pytest tests/stress/ -v

# 3. Chạy bài test tích hợp đường ống hợp nhất End-to-End
python -m pytest tests/integration/ -v

# 4. Tùy chọn: Chạy kiểm thử trực tiếp SLM với llama-server (Qwen3.5-2B)
python -m pytest tests/stress/test_live_slm_multilingual_operator.py --live-slm -v

# 5. Kiểm tra định dạng chuẩn PEP 8 với Ruff
ruff check src/ tests/
```

---

## 6. Giấy phép (License)

Dự án được phát hành theo giấy phép kép: **MIT License** và **Apache License 2.0**.
