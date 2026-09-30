# MN-009 Gate B: Measurement Contract & Evaluation Protocol

## 1. Mục tiêu & Nguyên tắc Đo lường

Tài liệu này đóng băng hợp đồng đo lường thực nghiệm cho **MN-009: Scoped Context Delivery Engine**.
Mục tiêu là kiểm chứng toán học và thực nghiệm khả năng nén, cắt gọt và đóng gói các luồng dữ liệu lớn ($2\text{k} - 32\text{k}$ tokens) xuống ngân sách $\le 512$ tokens mà không làm mất mát ngữ nghĩa, không đứt gãy cấu trúc cú pháp và bảo toàn $100\%$ tính toàn vẹn thời gian (temporal invariants).

Toàn bộ quá trình đánh giá tuân thủ nguyên tắc:
1. **Đo lường Token Cứng (Hard Token Accounting):** Sử dụng trực tiếp binary `llama-tokenize.exe` và file model `Llama-3.2-3B-Instruct-Q4_K_M.gguf`.
2. **Cách ly Tuyệt đối (Hermetic Sandbox):** Mọi mã nguồn thử nghiệm nằm tại `research/experiments/prototypes/mn-009-context-scaffolding/`. Thư mục `src/mong_nhiem/` tiếp tục đóng và không nhận code cho đến khi Gate D phê chuẩn.
3. **Tính Tất định & Khả năng Tái lặp (Deterministic Reproducibility):** Dữ liệu kiểm chuẩn được sinh bằng seed cố định, có mã băm SHA-256 xác thực trong `manifest.json`.

---

## 2. Thiết kế Tập Dữ liệu Kiểm chuẩn (Corpus 30 Cases)

Tập dữ liệu gồm 30 trường hợp thử nghiệm độc lập (`mn009-case-0001` đến `mn009-case-0030`), bao phủ 5 bậc quy mô ngữ cảnh ($2\text{k}, 4\text{k}, 8\text{k}, 16\text{k}, 32\text{k}$ tokens) qua 3 nhóm cấu trúc dữ liệu thực tế:

| Nhóm bài toán | Số cases | Phân bố kích thước | Đặc tính kỹ thuật kiểm tra |
| :--- | :---: | :---: | :--- |
| **Nhóm A: Văn bản & Dòng sự kiện (Text & Story Stream)** | 10 | 2k: 2, 4k: 2, 8k: 2, 16k: 2, 32k: 2 | - Cơ chế **Anchor-and-Spoke**: Ghim 60 tokens mở đầu + trật tự thời gian gốc.<br>- **Causal Timeline**: Nén sự kiện đan xen thành dòng biến đổi trạng thái.<br>- Giải quyết bẫy mất đại từ ("anh ấy", "công ty đó") của RAG thông thường. |
| **Nhóm B: Đồ thị Tri thức & Bảng Trạng thái (Graph & State Tables)** | 10 | 2k: 2, 4k: 2, 8k: 2, 16k: 2, 32k: 2 | - **Invariant Temporal Check:** $100\%$ thực thể xuất hiện phải có Latest State.<br>- **k-Hop Subgraph BFS ($k \le 2$):** Cắt tỉa đồ thị 500 nodes xuống $\le 8$ nodes.<br>- **Shortest Path Bridging:** Bảo toàn đường đi kết nối giữa 2 thực thể mục tiêu.<br>- **Column/Row Projection:** Lọc bảng 50 dòng xuống đúng 2 dòng hữu quan. |
| **Nhóm C: Codebase AST Slicing (Mã nguồn phần mềm)** | 10 | 2k: 2, 4k: 2, 8k: 2, 16k: 2, 32k: 2 | - **AST Skeletoning:** Thu gọn 25 hàm phụ thành `def name(...): ...`.<br>- **Untyped Handling:** Trích xuất default values và biến trong câu lệnh `return`.<br>- **Adaptive Inlining:** Tự động giữ nguyên thân hàm nếu hàm phụ ngắn $\le 5$ dòng.<br>- **Syntax Integrity:** Mã sau khi nén phải vượt qua `ast.parse` không lỗi cú pháp. |

---

## 3. Năm Tiêu chuẩn Nghiệm thu Đóng băng (Frozen Support Rules)

Để đạt điều kiện đề xuất promote tại Gate D, kết quả chạy thực nghiệm bắt buộc phải thỏa mãn đồng thời cả 5 tiêu chí sau:

### Rule 1: Ngân sách Token Cứng (Hard Token Budget Ceiling)
- **Tiêu chuẩn:** $100\%$ ($30/30$ cases) đầu ra sau khi đóng gói đo bằng `llama-tokenize.exe` phải có độ dài:
  $$\text{TokenCount}(\text{packed\_context}) \le 512$$
- **Sai số cho phép:** $0$ trường hợp vượt ngưỡng (Zero Overflow Tolerance).

### Rule 2: Tính Toàn vẹn Ranh giới Cú pháp (Boundary & AST Integrity)
- **Tiêu chuẩn:** 
  - $0$ câu văn bị đứt gãy giữa chừng (phải kết thúc bằng dấu chấm câu hoặc ngắt dòng hợp lệ).
  - $100\%$ các đoạn mã sau nén trong Nhóm C phải là mã nguồn Python hợp lệ (`ast.parse` trả về hợp lệ).

### Rule 3: Bảo tồn Dữ kiện Mục tiêu (Salience Information Recall)
- **Tiêu chuẩn:** Ít nhất $28/30$ cases ($93.3\%$) phải bảo toàn được dữ kiện mục tiêu (Target Fact / State / Logic) trong ngữ cảnh 512 tokens.

### Rule 4: Độ trễ Xử lý CPU (CPU Packing Latency Gate)
- **Tiêu chuẩn:** Thời gian đóng gói trung bình trên CPU của máy host:
  $$\text{MeanLatency}_{\text{CPU}} < 15.0\text{ ms}$$
  (Thời gian tối đa cho case 32k tokens $< 35\text{ ms}$).

### Rule 5: Căn chỉnh Tiền tố Prompt Cache (Prefix Cache Invariant)
- **Tiêu chuẩn:** Cấu trúc System Header cố định ở đầu context đạt tỷ lệ tái sử dụng bộ nhớ đệm KV Cache trên `llama-server.exe`:
  $$\text{CacheHitRate} = 100\%$$
  Giúp giảm độ trễ Time-to-First-Token (TTFT) của model $\ge 80\%$ so với nạp thô 8k/16k tokens.

---

## 4. Định dạng Schema Dữ liệu Kiểm chuẩn

Mỗi trường hợp trong tập 30 cases được lưu trữ dưới định dạng JSON Lines gồm các trường:
```json
{
  "case_id": "mn009-case-0001",
  "category": "text_stream | graph_table | code_ast",
  "raw_token_count": 8192,
  "raw_content": "... [Văn bản, Code hoặc Đồ thị đầy đủ] ...",
  "query": "Trạng thái cuối cùng của Thực thể X là gì?",
  "target_fact": "Thực thể X đang ở trạng thái ACTIVE tại Khu vực B",
  "required_entities": ["Entity_X", "Entity_Y"],
  "oracle_answer": "ACTIVE"
}
```

---

## 5. Ranh giới Phủ quyết (Rejection Boundary)

Nếu xảy ra bất kỳ điều kiện nào sau đây, milestone tự động bị bác bỏ tại Gate D:
1. Có dù chỉ 1 case có độ dài $> 512$ tokens sau khi đóng gói.
2. Phát hiện lỗi cú pháp `SyntaxError` hoặc đứt đoạn AST trong code sinh ra.
3. Vi phạm `Invariant Temporal Check`: Tồn tại thực thể mục tiêu trong query nhưng thiếu Latest State tương ứng trong context.
4. Tỷ lệ giữ dữ kiện mục tiêu $< 28/30$.
