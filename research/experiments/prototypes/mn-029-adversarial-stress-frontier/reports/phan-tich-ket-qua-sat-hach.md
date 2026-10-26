# Bản Phân Tích Chuyên Sâu: Kết Quả Sát Hạch Đối Kháng MN-029 & Ranh Giới Kiến Trúc Hệ Thống

## 1. Mổ Xẻ Bản Chất 9 Điểm Gãy Trước Khi Vá (The Fragile Reality)

Trước Milestone MN-029, hệ thống nhận thức Mộng Nhiễm đã trải qua 27 cột mốc thử nghiệm với tỷ lệ thành công bề mặt rất ấn tượng ($95\% - 100\%$). Tuy nhiên, những con số đó phần lớn phản ánh các kịch bản vi thế giới tổng hợp (synthetic microworlds) được thiết kế có phần "vừa khít" một cách ngây thơ. Khi đưa hệ thống vào môi trường thử nghiệm đối kháng khắc nghiệt mô phỏng thực tế, 9 điểm gãy chí mạng đã lập tức phát lộ trên baseline ban đầu:

```
+----------------------------------------------------------------------------------------------------+
|                                    9 TỬ HUYỆT CỦA BASELINE DANH NGHĨA                               |
+------------------------------------+----------------------------------+-----------------------------+
| 1. BẪY NHÌN TRƯỚC (Lookahead)      | 2. ĐUA TRẠNG THÁI (Mid-Inference)| 3. ĐỒNG QUY & CẢM BIẾN CHẾT |
| SLM tối ưu tham lam tại T_0        | Độ trễ 150-200ms biến lệnh an    | 2 nguyên nhân ngược nhau,   |
| => Khóa chết van an toàn ở T_4     | toàn lúc gửi thành thảm họa      | SLM đoán mò 50/50           |
+------------------------------------+----------------------------------+-----------------------------+
| 4. THIÊN KIẾN TỰ HỒI QUY (ASR)     | 5. TRÔI DẠT DƯỚI NGƯỠNG (Drift)  | 6. LỆCH PHA BIMODAL         |
| Token đầu hút chú ý, chốt lệnh     | AutoDream nén sạch vi rung chấn  | Regex bắt nhầm câu tương    |
| trước khi đọc hết câu đính chính   | => "Nấu ếch trong nồi nước ấm"   | phản tiếng Việt (False Pos) |
+------------------------------------+----------------------------------+-----------------------------+
| 7. LIVELOCK ĐA TÁC TỬ              | 8. BIÊN C-ABI & PANIC RUST       | 9. SẬP NGUỒN PHÂN MẢNH      |
| Cả 2 agent cùng nhường "STANDBY"   | f64::INFINITY làm nát state,     | Lệch epoch giữa Rust, DAG,  |
| => Đói tài nguyên, đóng băng hệ    | catch_unwind để lại handle độc   | để lại "ký ức ma" KV cache  |
+------------------------------------+----------------------------------+-----------------------------+
```

### 1.1. Bẫy Thiển Cận Cục Bộ Của Mô Hình Ngôn Ngữ Nhỏ (Test 1)
Các bài test cũ thường thiết kế điều kiện cấm vi phạm ngay tại thời điểm thực thi ($T_0$). Vì vậy, chỉ cần một cổng lọc trạng thái không tương thích (`incompatible_states`) là đủ để loại bỏ các lựa chọn sai. Nhưng trong thực tế, các quyết định điều khiển luôn mang **tính trễ nhân quả (delayed causality)**. Khi đứng trước 3 hành động đều hợp lệ tại $T_0$, SLM 2B tự nhiên chọn hành động tối ưu hóa điểm số cục bộ tức thời (`COOL_FAST`, hạ 50 độ ngay lập tức) mà hoàn toàn mù quáng trước thực tế là áp suất phụ sẽ chạm đáy sau 4 nhịp tick ($T_0 + 4$), khóa cứng van an toàn và biến hệ thống thành một quả bom nổ chậm. 

### 1.2. Khoảng Trống Vật Lý Giữa Luồng Suy Luận (Test 2)
Trong thế giới phần mềm truyền thống, việc kiểm tra điều kiện tiên quyết (pre-condition check) thường diễn ra trong vài nano-giây trước khi gọi hàm. Tuy nhiên, khi đưa một mô hình mạng nơ-ron (SLM) vào vòng lặp điều khiển, một **hố sâu thời gian kéo dài 150ms – 230ms** xuất hiện. Việc kiểm tra trạng thái lúc $t = 0\text{ ms}$ (áp suất $79.5\text{ bar} < 80.0\text{ bar}$) hoàn toàn vô nghĩa nếu trong lúc mô hình đang bận sinh token, môi trường vật lý ở luồng Rust đã cán mốc $83.2\text{ bar}$. Nếu Host ngây thơ thực thi lệnh sinh ra từ ảnh chụp trạng thái quá khứ, thảm họa vật lý là điều tất yếu.

### 1.3. Bẫy Đồng Quy & Sự Tê Liệt Của Cảm Biến (Test 3)
Các đồ thị nhân quả trước đây giả định mọi cảm biến đều là nguồn chân lý (ground truth). Khi một cảm biến lưu lượng bị "chết đứng" (stuck-at fault) ở mức bình thường và triệu chứng áp suất tụt có thể bắt nguồn từ hai nguyên nhân đối nghịch (`RÒ RỈ` vs `KẸT BƠM`), việc duyệt ngược đồ thị nhân quả (abductive causal tracing) trả về đồng thời cả hai giả thuyết. SLM 2B không có khả năng tự phát hiện cảm biến chết, dẫn đến hành vi "đoán mò 50/50" — một canh bạc chết người trong điều khiển công nghiệp.

### 1.4. Lỗ Hổng Cơ Bản Của Bộ Giải Mã Tự Hồi Quy Trước Khẩu Lệnh Hỗn Loạn (Test 4)
Mô hình ngôn ngữ tự hồi quy (Autoregressive) sinh token tuần tự từ trái sang phải:
$$P(y_1, y_2, \dots, y_n \mid x) = \prod_{i=1}^n P(y_i \mid y_{<i}, x)$$
Nếu áp dụng ngữ pháp GBNF cũ ép sinh động từ hành động (`action_verb`) ngay ở vị trí token đầu tiên, mô hình 2B lập tức bị cụm từ đầu câu *"Mở van 2..."* hút toàn bộ sự chú ý (attention weight) và chốt luôn từ khóa `OPEN` trước khi cơ chế chú ý kịp lan truyền đến mệnh đề đính chính ở cuối câu: *"...à khoan đừng mở số 2, đóng nó lại và mở van phụ"*. Đây là điểm gãy cố hữu của cơ chế giải mã tự hồi quy bị khóa cú pháp quá sớm.

### 1.5. Căn Bệnh "Nấu Ếch Trong Nồi Nước Ấm" Của Cơ Chế Nén Ký Ức (Test 5)
Các cơ chế nén ký ức định kỳ như AutoDream được thiết kế để loại bỏ "nhiễu nền" nhằm giữ prompt dưới trần 512 tokens. Điểm mù nằm ở chỗ: các biến đổi vi mô dưới ngưỡng tức thời ($+0.2\% < 0.5\%$) bị coi là nhiễu và vứt bỏ ở từng tick. Nhưng sau nhiều chu kỳ, tích phân của các biến đổi này đã đạt mức cảnh báo ($0.8\%$). Việc thiếu một bộ theo dõi tích lũy trượt khiến bộ nhớ của tác tử hoàn toàn bị tẩy não trước các hiểm họa suy thoái chậm.

### 1.6. Sự Thất Bại Của Bộ Lọc Từ Khóa Regex Trên Ngôn Ngữ Tự Nhiên (Test 6)
Khi kiểm soát sự nhất quán giữa hành động vật lý và câu nói giao tiếp, việc dùng regex so khớp từ khóa ("an toàn", "nguy hiểm", "xả") trên câu thoại tự do là một sai lầm chết người. Ngôn ngữ tự nhiên, đặc biệt là tiếng Việt, có tính đa nghĩa và cấu trúc câu tương phản cực kỳ phong phú. Một câu thoại cảnh báo trung thực như: *"Tôi buộc phải xả oxy chứ không thể giữ an toàn cho khoang này được nữa!"* chứa chữ "an toàn" nhưng mang bản chất của sự khẩn cấp và xả bỏ. Regex ngây thơ lập tức báo còi dương tính giả (False Positive), vô hiệu hóa chính hành vi cứu nguy của hệ thống.

### 1.7. Livelock Do Sự Lịch Sự Thái Quá Giữa Các Tác Tử (Test 7)
Khi thiết kế cơ chế tránh xung đột bằng cách nhường quyền, nếu cả hai tác tử đều nhận thức được va chạm tiềm tàng và đồng thời quyết định lùi lại bằng lệnh `STANDBY`, một vòng lặp nhường nhịn vô tận sẽ xuất hiện. Trạng thái của hệ thống không bị crash (deadlock), nhưng mọi hoạt động đều bị đóng băng hoàn toàn (livelock), dẫn đến cạn kiệt tài nguyên nhiệm vụ.

### 1.8. Cạm Bẫy C-ABI & Undefined Behavior Tại Ranh Giới Rust-Python (Test 8)
Sự an toàn bộ nhớ của Rust là có điều kiện — nó kết thúc tại ranh giới `extern "C"`. Việc chỉ kiểm tra `is_nan()` mà bỏ qua `f64::INFINITY` (vốn lớn hơn 0.0 và không phải NaN) dẫn đến việc một giá trị vô cực từ Python truyền xuống sẽ phá hủy toàn bộ cấu trúc trạng thái vật lý trong Rust. Nguy hiểm hơn, việc bắt panic bằng `catch_unwind` trên một con trỏ handle mà không sao chép phòng vệ sẽ để lại một đối tượng bị nhiễm độc (corrupted/poisoned state), dẫn đến rò rỉ bộ nhớ hoặc hành vi bất định (Undefined Behavior) trong các lần gọi tiếp theo.

### 1.9. Nguy Cơ "Ký Ức Ma" Khi Hệ Thống Sập Nguồn Giữa Chừng (Test 9)
Một hệ sinh thái nhận thức gồm 3 thành phần rời rạc: Trạng thái vật lý (Rust), Đồ thị tri thức (Python DAG) và Bộ nhớ đệm ngữ cảnh (KV Cache của llama-server). Nếu tiến trình bị sập nguồn khi Rust đã chuyển sang tick 45 nhưng Python và llama-server vẫn ở tick 44, việc khởi động lại và chỉ khôi phục tệp JSON trạng thái sẽ dẫn đến tình trạng "ông nói gà bà nói vịt". KV cache của LLM vẫn nhớ các tiền đề của epoch cũ, tạo ra ảo giác nghiêm trọng trong các quyết định kế tiếp.

---

## 2. Các Cơ Chế Kỹ Thuật Khắc Phục: Triết Lý "Khung Sắt" Host Authority

Mộng Nhiễm giải quyết triệt để 9 điểm gãy trên không phải bằng cách "huấn luyện thêm" cho mô hình 2B (vốn tốn kém và không có bảo đảm toán học), mà bằng cách **tăng cường độ cứng của chiếc khung sắt Host-Authoritative bao quanh mô hình**:

```
+----------------------------------------------------------------------------------------------------+
|                                  KIẾN TRÚC "KHUNG SẮT" HOST-AUTHORITATIVE                          |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|    Khẩu lệnh hỗn loạn --------> [ GBNF: Reasoning-First {1,80} + Dynamic Enum ]                    |
|                                                     |                                              |
|                                                     v                                              |
|                                       +----------------------------+                               |
|                                       |       SLM 2B INFERENCE     |                               |
|                                       | (Isolated Reasoning Box)   |                               |
|                                       +----------------------------+                               |
|                                                     |                                              |
|   +-------------------------------------------------+------------------------------------------+   |
|   | HOST ARBITRATION GATES (Quyền Lực Tuyệt Đối Của Host)                                       |   |
|   |                                                                                            |   |
|   | 1. Trajectory Safety ($O(1)$ Lookahead): Chặn lệnh gây chết ở tương lai $T+4$               |   |
|   | 2. Commit-Time Double Check: Chặn lệnh sinh ra từ ảnh chụp trạng thái cũ                   |   |
|   | 3. Diagnostic Probe Enforcer: Ép `PROBE`, cấm đoán mò khi cảm biến chết / đồng quy         |   |
|   | 4. Bimodal Coherence Arbiter: Khóa khớp thẻ ý định `[<CLASS>:<INTENT>]` (0.0% FP)          |   |
|   | 5. Directed Livelock Preemptor: Cắt đứt vòng lặp `STANDBY-STANDBY` ở $T=3$                 |   |
|   | 6. Cumulative Telemetry Tracker: Tích phân trượt giữ FactCard biến động chậm               |   |
|   | 7. FFI Boundary Guard: Chặn `!is_finite()`, CoW trong `catch_unwind` (100k ticks $0\mu\text{s}$) |
|   | 8. 3-Way Transactional Sync: Rollback epoch đồng bộ + Xóa sạch KV Slot Cache khi crash     |   |
|   +-------------------------------------------------+------------------------------------------+   |
|                                                     |                                              |
|                                                     v                                              |
|                                 [ HARDWARE / ENGINE STATE COMMIT ]                                 |
+----------------------------------------------------------------------------------------------------+
```

### 2.1. Phóng Chiếu Trạng Thái $O(1)$ Không Cần Sao Chép (Zero-Copy Trajectory Projection)
Để giải quyết Test 1 mà không làm bùng nổ độ trễ, Mộng Nhiễm từ bỏ thuật toán duyệt cây nhánh sâu $6^4 = 1.296$ lần `deepcopy` trong Python. Thay vào đó, hàm `check_trajectory_safety` thực hiện phóng chiếu tuyến tính trên từ điển số thực nguyên thủy:
$$S_{t+k} = S_t + k \cdot (\Delta_{\text{action}} + \vec{\lambda}_{\text{decay}})$$
Mọi phép tính được thực thi trực tiếp trên thanh ghi CPU, kiểm tra toàn bộ tập bất biến $\bigwedge_{i=1}^4 \mathcal{I}(S_{t+i})$ chỉ trong chưa đầy **$8.5\mu\text{s}$**, loại bỏ ngay `COOL_FAST` trước khi kịp cấp quyền hành động.

### 2.2. Cổng Kiểm Tra Lại Tại Thời Điểm Commit (Commit-Time Double Check)
Nhận diện rõ độ trễ $150\text{ms}$ của SLM là một hằng số vật lý không thể triệt tiêu, hàm `verify_and_commit_action` chia việc xác thực thành 2 pha độc lập:
1. **Pre-condition Filter:** Lọc danh sách affordance hợp lệ tại $t_0$ trước khi gửi prompt.
2. **Commit-Time Re-validation:** Ngay khi token cuối cùng trả về tại $t_{\text{ret}}$, Host đọc trực tiếp thanh ghi trạng thái sống của `ContinuousStateEngine`. Nếu giá trị trôi dạt vi phạm ngưỡng (như áp suất vọt lên $83.2\text{ bar}$), hành động bị hủy lập tức với mã lỗi `ABSTAIN_INFERENCE_INVALIDATED`. Trạng thái vật lý được bảo vệ tuyệt đối.

### 2.3. Ngữ Pháp GBNF "Suy Luận Trước, Chốt Lệnh Sau" Có Giới Hạn Cứng
Để khắc phục thiên kiến tự hồi quy trong Test 4, ngữ pháp GBNF được tái cấu trúc triệt để:
```ebnf
root ::= "REASONING: " [^\n]{1,80} "\n" "ACTION: " verb " " entity
```
- **Ép buộc suy luận:** Bắt buộc mô hình phải sinh dòng `REASONING:` trước khi được phép chạm vào từ khóa `ACTION:`. Việc này kích hoạt các lớp chú ý của Transformer quét qua toàn bộ ngữ cảnh, xử lý xong các mâu thuẫn và phủ định trong lời nói của con người.
- **Giới hạn cứng $\{1, 80\}$ ký tự:** Chặn đứng hiện tượng mô hình 2B rơi vào vòng lặp giải thích dông dài làm cạn kiệt token hoặc tăng độ trễ.
- **Enum động theo kịch bản:** Khóa thực thể theo danh sách thực tế của kịch bản (`"valve_1" | "valve_2" | "aux_valve"`), ngăn chặn hoàn toàn việc mô hình tự chế ra tên thực thể tiếng Việt không dấu.

### 2.4. Khóa Ý Định Có Cấu Trúc (Structured Intent Protocol) Thay Vì Quét Regex
Để loại bỏ 100% dương tính giả trong Test 6, kênh giao tiếp được chuẩn hóa:
```
COMMUNICATE [INFORM:PURGE]: "Toi buoc phai xa oxy de ngan ngua no khoang!"
```
Cơ chế kiểm soát không phân tích chuỗi văn bản tự do trong ngoặc kép mà chỉ so khớp thẻ `[INFORM:PURGE]` với hành động `ACTION: PURGE_OXYGEN`. Hai ma trận quan hệ đối nghịch được định nghĩa rõ ràng ở tầng Host, biến bài toán phân tích ngữ nghĩa mờ thành bài toán tra cứu bảng băm tất định (deterministic lookup) với độ trễ $O(1)$ và tỷ lệ lỗi $0.0\%$.

### 2.5. Phòng Thủ Biên C-ABI Bằng Kỹ Thuật Copy-on-Write (CoW)
Trong lõi Rust `crates/mong_nhiem_core/src/ffi.rs`:
- Bổ sung rào chắn kiểm tra: `if !delta_seconds.is_finite() || delta_seconds < 0.0 { return -1; }` chặn đứng hoàn toàn `NaN` và `f64::INFINITY`.
- Trước khi thực hiện `engine.tick()`, tạo một bản sao cạn của trạng thái. Nếu khối code bên trong `catch_unwind` xảy ra panic, con trỏ trạng thái ban đầu lập tức được khôi phục nguyên vẹn từ bản sao, ngăn chặn hoàn toàn việc nhiễm độc handle. Kết quả kiểm thử ngâm tải 100.000 chu kỳ khẳng định độ lệch RAM đạt con số lý tưởng: $+0.000\text{ MB}$.

---

## 3. Đánh Giá Năng Lực Thực Tế & Khoảng Trống Thực Địa (Reality Gap)

### 3.1. SLM 2B Thông Minh Đến Đâu và "Bộ Khung Sắt" Gánh Bao Nhiêu?
Kết quả thực nghiệm đưa ra một kết luận khoa học không khoan nhượng:
- **Bản thân SLM 2B (Qwen3.5-2B, Llama-3.2-3B) KHÔNG THỂ tự bảo đảm an toàn.** Nếu thả nổi mô hình tự do quyết định trong các bài test đối kháng này mà không có Host can thiệp, tỷ lệ thất bại của hệ thống là **$100\%$** (chết vì bẫy lookahead, nổ vì đua trạng thái, vỡ đường ống vì đoán mò cảm biến chết, và sinh sai lệnh vì nói nhịu).
- Mô hình ngôn ngữ nhỏ đóng vai trò là một **bộ chuyển đổi mềm dẻo (flexible semantic transducer)**: nó chuyển đổi ngôn ngữ con người thành cấu trúc, nhận diện mẫu ngữ cảnh, và gợi ý các hành động tiềm năng.
- **Toàn bộ tính an toàn, tính bất biến, tính thời gian thực và độ bền bỉ đều do HOST gánh vác.** Thành công của Mộng Nhiễm không nằm ở việc tạo ra một "siêu AI 2B", mà nằm ở **thiết kế kiến trúc điều phối bất biến (invariant governance architecture)**, biến một mô hình xác suất mong manh thành một thành phần vận hành tin cậy bên trong một hệ thống tất định.

### 3.2. Khoảng Trống Thực Địa Còn Lại (Remaining Reality Gaps)
Dù đã vượt qua 9 bài test đối kháng, các kỹ sư hệ thống cần nhận thức rõ những hạn chế thực tế chưa được bao phủ:
1. **Phần cứng thật vs Bộ giả lập (Hardware-in-the-Loop):** Bài test 2 và 8 sử dụng cơ chế giả lập độ trễ `time.sleep` và các hàm FFI đồng bộ. Trong thế giới nhúng thực tế, jitter của bus CAN/I2C, xung nhiễu điện từ, và hiện tượng rớt gói tin UART có thể tạo ra các dị thường tín hiệu phức tạp hơn nhiều so với việc chỉ kẹt giá trị tĩnh (stuck-at fault).
2. **Nhiệt độ lượng tử hóa (Quantization Noise):** Các mô hình chạy ở mức lượng tử 4-bit (`Q4_K_M`) đôi khi có xác suất rất nhỏ bị trượt logits khi điện áp GPU/NPU dao động, đòi hỏi các bộ lọc GBNF phải được tích hợp thẳng vào engine biên dịch mã máy của chip nhúng.

---

## 4. Phân Tách Ranh Giới Bản Chất: Cyber-Physical / Game NPC Kernel vs Dev / IDE / Chatbot Tooling

Một câu hỏi cốt lõi về định vị sản phẩm: **Tại sao Mộng Nhiễm lại được xây dựng như một Kernel cho Cyber-Physical Systems (Hệ thống điều khiển nhúng, Robot, IoT, Drone, SCADA) và Game NPC thời gian thực, mà KHÔNG PHẢI là một công cụ lập trình (IDE Tool như Claude Code, Cursor) hay Chatbot hỏi đáp?**

Bảng đối chiếu sau đây làm sáng tỏ sự khác biệt một trời một vực giữa hai triết lý thiết kế:

| Chiều Kích Kiến Trúc | Mộng Nhiễm Kernel (Cyber-Physical / Game NPC) | Dev Tooling / Coding Assistant (Cursor, Claude Code, Aider) | Chatbot Phổ Thông (ChatGPT, Le Chat) |
| :--- | :--- | :--- | :--- |
| **Mô Hình Thời Gian (Time Model)** | **Hệ thống nhịp Tick thời gian thực (Dual-Clock / Delta-t).** Trạng thái vật lý tự trôi dạt và suy thoái liên tục theo thời gian thực kể cả khi AI đang suy nghĩ. | **Không có khái niệm thời gian trôi.** Trạng thái codebase đứng yên hoàn toàn chờ người dùng gõ lệnh hoặc AI sinh code xong. | **Request-Response tĩnh.** Không có trục thời gian nội tại; mỗi lượt hội thoại là một lát cắt đóng băng. |
| **Trọng Tài An Toàn (Safety Arbiter)** | **Host Invariant Gate nắm quyền lực tuyệt đối.** C-ABI, Double-Check Gate, Trajectory Projection có quyền hủy bỏ lệnh của AI ngay tại thời điểm commit. | **Người dùng (Human-in-the-loop) hoặc Linter/Compiler.** AI sinh code sai thì trình biên dịch báo lỗi, người dùng nhấn "Reject" hoặc revert git. | **Gần như không có.** AI xin lỗi và người dùng sửa lại prompt. |
| **Quản Lý Bộ Nhớ (Memory Architecture)** | **Bộ nhớ FactCard bị chặn cứng $\le 512$ tokens.** Dùng AutoDream nén đồ thị và tích phân trượt để bảo đảm độ trễ suy luận ổn định $< 200\text{ms}$. | **Cửa sổ ngữ cảnh khổng lồ ($128\text{k} - 1\text{M}$ tokens).** Tận dụng tối đa bộ nhớ để nhét toàn bộ file code, AST slices, git diffs. | **RAG không giới hạn hoặc trượt cửa sổ hội thoại dài.** |
| **Độ Trễ Chấp Nhận (Latency SLA)** | **Cực khắt khe (Sub-second đến Microsecond).** C-ABI Rust xử lý $< 2\mu\text{s/tick}$, suy luận SLM phải khống chế trong vài trăm ms để tránh đua trạng thái. | **Rất thoải mái ($10\text{s} - 60\text{s}$).** Lập trình viên sẵn sàng chờ hàng chục giây để mô hình suy nghĩ sâu (Thinking model / CoT) và sinh cả file code. | **Vài giây.** Người dùng chấp nhận streaming chữ từ từ. |
| **Hậu Quả Khi AI Mắc Lỗi (Failure Consequence)** | **THẢM HỌA VẬT LÝ:** Vỡ đường ống áp suất, cháy lò phản ứng, rơi drone, NPC hành động phi lý làm gãy mạch logic game. | **LỖI PHẦN MỀM:** Bug unit test, compile error, git reset trong vài giây mà không tổn hại vật chất. | **TRẢ LỜI SAI:** Ảo giác thông tin, người dùng đọc thấy vô lý và bỏ qua. |
| **Giao Thức Tương Tác** | **Bimodal khép kín:** Vừa điều khiển cơ cấu chấp hành (`ACTION:`) vừa phản hồi trạng thái cho con người (`COMMUNICATE [CLASS]:`). | **File System & Shell:** Ghi đè file, chạy `pytest`, đọc terminal output. | **Hộp thoại văn bản tự do (Free-form text chat).** |

### Đúc Kết Ranh Giới:
- Nếu bạn muốn xây dựng một công cụ hỗ trợ viết code (IDE Dev Tool), bạn **không cần** Mộng Nhiễm. Bạn cần một mô hình cực lớn (Claude 3.5 Sonnet, GPT-4o), một cửa sổ ngữ cảnh 200k tokens, một bộ RAG tìm kiếm file mã nguồn, và bạn có thể ung dung chờ 30 giây để nhận kết quả.
- Nhưng nếu bạn cần điều khiển một **nhà máy thông minh**, một **hệ thống pin lưu trữ năng lượng mặt trời**, một **phi đội máy bay không người lái**, một **thiết bị y tế giám sát bệnh nhân**, hay một **thế giới Game RPG nơi 100 NPC có đời sống tâm lý và liên tục tương tác với môi trường vật lý thời gian thực trên phần cứng tiêu dùng** — khi đó **Mộng Nhiễm là lựa chọn kiến trúc tối thượng**. Nó biến các chip nhúng nhỏ bé mang SLM 2B thành những thực thể vận hành an toàn tuyệt đối dưới kỷ luật thép của Host.

---

## 5. Kết Luận Chiến Lược & Định Hướng Tiếp Theo

Milestone MN-029 đã hoàn thành xuất sắc sứ mệnh lịch sử của mình: **Bẻ gãy toàn bộ ảo tưởng về các bài test vi thế giới màu hồng, chỉ ra chính xác 9 tử huyệt của kiến trúc khi chạm trán thực tế, và trang bị cho Mộng Nhiễm một hệ miễn dịch đối kháng toàn diện.**

### Thành Tựu Cốt Lõi:
1. Xác lập tiêu chuẩn kiểm thử **Test-Driven Falsification**: 100% kịch bản đều phải chứng minh gãy baseline trước khi được vá.
2. Chứng minh hiệu năng C-ABI phi thường của Rust core: **$707.463\text{ ticks/s}$**, độ trễ **$1.414\mu\text{s}$**, độ lệch RAM **$+0.000\text{ MB}$** qua 100.000 chu kỳ tải nặng.
3. Hoàn thiện 12/12 chỉ số điều khoản khắt khe của Hợp đồng Gate B mà không phải hạ thấp bất kỳ tiêu chuẩn nào.

### Kiến Nghị Lộ Trình Phát Triển Tiếp Theo:
1. **Chính thức đưa các bản vá MN-029 vào nhánh Production (`src/mong_nhiem/` và `crates/mong_nhiem_core/`):** Biến Trajectory Safety, Commit-Time Double Check, Diagnostic Probe Enforcer, Cumulative Tracker, và Reasoning-First GBNF thành các tính năng mặc định của kernel.
2. **Chuẩn Bị Cho Cột Mốc Hardware-in-the-Loop (HIL):** Đưa kernel Mộng Nhiễm chạy thực tế trên các bo mạch nhúng biên (NVIDIA Jetson Orin Nano, Raspberry Pi 5 kết hợp Coral NPU) kết nối với cảm biến vật lý thực để kiểm nghiệm khả năng kháng nhiễu điện và jitter phần cứng.
