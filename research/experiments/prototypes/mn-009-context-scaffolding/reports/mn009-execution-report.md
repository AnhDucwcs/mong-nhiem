# MN-009 Gate C: Scoped Context Delivery Engine Execution Report

**Run ID:** `mn009-execution-run-0001`  
**Timestamp:** `2026-09-30T14:40:15.579635+00:00`  
**Evaluated Binary:** `D:\Materials\llama.cpp\build\bin\Release\llama-tokenize.exe`  
**Model Weights:** `Llama-3.2-3B-Instruct-Q4_K_M.gguf`  

---

## 1. Kết Quả Nghiệm Thu 5 Tiêu Chuẩn Đóng Băng (Frozen Rules)

| Tiêu chuẩn (Rule) | Ngưỡng yêu cầu (Threshold) | Kết quả thực nghiệm (Measured) | Trạng thái |
| :--- | :--- | :--- | :---: |
| **Rule 1: Hard Token Ceiling** | $\le 512$ tokens ($100\%$) | Max: **501**, Mean: **229.7** | **PASS** |
| **Rule 2: Boundary & AST Integrity** | $100\%$ valid syntax / boundaries | Pass rate: **30/30** ($100\%$) | **PASS** |
| **Rule 3: Salience Recall** | $\ge 28/30$ cases ($93.3\%$) | Recall rate: **30/30 (100.0%)** | **PASS** |
| **Rule 4: CPU Latency Gate** | Mean $< 15.0\text{ ms}$, Max $< 35.0\text{ ms}$ | Mean: **3.62 ms**, Max: **16.83 ms** | **PASS** |
| **Rule 5: Prefix Cache Invariant** | $100\%$ identical prefix header | Hit rate: **100%** | **PASS** |

---

## 2. Phân Bố Theo Nhóm Dữ Liệu & Quy Mô

| Nhóm bài toán | Số cases | Quy mô thô (Tokens) | Token sau đóng gói | Mean CPU Latency | AST / Cú pháp |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Nhóm A: Text Stream** | 10 | 2k - 32k | $\le 512$ | 3.9 ms | $10/10$ Hoàn chỉnh |
| **Nhóm B: Graph & State Tables** | 10 | 2k - 32k | $\le 512$ | 0.55 ms | $10/10$ Chuẩn hóa |
| **Nhóm C: Codebase AST Slicing** | 10 | 2k - 32k | $\le 512$ | 6.39 ms | $10/10$ Valid AST |

---

## 3. Khuyến Nghị Phê Chuẩn Gate D (Gate D Disposition)

- **Đánh giá tổng thể:** **RECOMMEND_PROCEED**
- Cả 5/5 tiêu chuẩn hỗ trợ đều đạt 100% yêu cầu.
- Không phát hiện bất kỳ trường hợp nào tràn ngưỡng 512 tokens hoặc lỗi cú pháp AST.
- Thuật toán đóng gói CPU hoàn thành toàn bộ 30 cases với thời gian trung bình 3.62 ms, sẵn sàng cho việc xúc tiến vào production pipeline `src/mong_nhiem/context/`.
