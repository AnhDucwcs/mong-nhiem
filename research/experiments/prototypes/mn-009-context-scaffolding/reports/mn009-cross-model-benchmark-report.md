# MN-009 Downstream Cross-Model Benchmark Report

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../../concepts/architecture.md)
- Current Milestone State: [current-state](../../../../current-state.md)
- Parent Milestone Charter: [MN-009 Gate A Charter](../charter.md)
- Measurement Contract: [MN-009 Gate B Contract](../gate-b-contract.md)
- Architecture Comparison Report: [MN-009 Reasoning Architecture Comparison](mn009-reasoning-architecture-comparison.md)
- Canonical Evidence Files:
  - `runs/eval_llama_3_2_3b.json`
  - `runs/eval_qwen3_4b.json`
  - `runs/mn009-comparison-run-20261001T144940Z/summary.json`

---

## 1. Quantitative Benchmark Results (30 Cases)

**Benchmark Corpus:** 30 Scoped Context Cases from MN-009 Gate C ($2\text{k}-32\text{k}$ raw scale $\rightarrow \le 512$ tokens packed).  
**Runtime:** `llama-server.exe` (Flash Attention ON, Port 18502, Temperature 0.0, max_tokens 64).

| Metric | Mô hình Mới (`Qwen3.5-2B`) | Mô hình Cũ 1 (`Llama-3.2-3B`) | Mô hình Cũ 2 (`Qwen3-4B`) | Đánh giá / Xếp hạng |
| :--- | :---: | :---: | :---: | :---: |
| **Dung lượng file GGUF** | **1.40 GB** (Q4_K_M) | 2.02 GB (Q4_K_M) | 2.50 GB (Q4_K_M) | **Qwen 3.5 2B nhẹ nhất (-44%)** |
| **Độ chính xác tổng thể** | **100.0% (30/30)** | **96.67% (29/30)** | **66.67% (20/30)** | **Qwen 3.5 2B quán quân** |
| **Độ trễ trung bình (Latency)** | **471.7 ms** | 853.4 ms | 1,640.4 ms | **Qwen 3.5 2B nhanh nhất (3.5x)** |
| **Token đầu ra trung bình** | **21.7 tokens** | 38.3 tokens | 38.3 tokens | **Qwen 3.5 2B súc tích nhất** |
| **Domain A: Text Stream (10)** | **10/10 (100.0%)** | 9/10 (90.0%) | **10/10 (100.0%)** | Qwen 3.5 & Qwen 3 dẫn đầu |
| **Domain B: Graph / Table (10)**| **10/10 (100.0%)** | **10/10 (100.0%)** | **10/10 (100.0%)** | Cả 3 mô hình đạt 100% |
| **Domain C: Code AST (10)** | **10/10 (100.0%)** | **10/10 (100.0%)** | **0/10 (0.0%)** | Qwen 3 4B sụp đổ hoàn toàn |

---

## 2. Phân tích nguyên nhân chênh lệch giữa các mô hình

1. **Vì sao Qwen 3.5 2B chiến thắng toàn diện (100.0%):**
   - `Qwen3.5-2B` có khả năng tuân thủ định dạng trích xuất trực tiếp xuất sắc. Nó trả lời thẳng vào trọng tâm câu hỏi (`'RESULT_OK_21'`, `'Node_30: Access=AUTHORIZED, Role=ADMIN_TIER_3'`) mà không lặp lại các câu mở đầu dài dòng.
   - Nhờ số lượng token sinh ra cực ngắn (21.7 tokens), độ trễ chỉ tốn **471 ms**, nhanh gấp gần 2 lần Llama 3.2 3B và gấp 3.5 lần Qwen 3 4B.
2. **Vì sao Qwen 3 4B thất bại nặng nề ở Code AST (0/10):**
   - `Qwen3-4B` mắc tật "giải thích dông dài" (preamble conversational bloat). Khi nhận query trích xuất code, nó luôn mở đầu bằng một đoạn văn giải thích: `"The function execute_pipeline_21 takes val_a=2 and val_b=3 and computes..."`.
   - Vì budget đầu ra bị khóa ở `max_tokens: 64`, nó cạn sạch token trước khi kịp in ra chuỗi giá trị trả về (`'RESULT_OK_XX'`), dẫn đến điểm số 0/10 ở Domain C.
3. **Llama 3.2 3B giữ vị trí á quân (96.67%):**
   - `Llama-3.2-3B` chỉ trượt đúng 1 ca ở Text Stream (`mn009-case-0007`) do bị trôi dạt trạng thái trung gian, nhưng xử lý rất tốt Graph và Code AST.
