# MN-009 Gate A: Charter & Scientific Hypothesis

## 1. Problem Statement

Empirical results across `MN-003`, `MN-004`, `MN-007`, and `MN-008` established that `Llama-3.2-3B` suffers catastrophic capability loss on complex tasks (state tracking, multi-entity reasoning, conditional conjunction) as context expands beyond 512 tokens, collapsing to 0% at 8,192 tokens. Furthermore, running 8k-16k direct context incurs severe latency penalties (~18-25s per call on consumer 4GB VRAM hardware) and frequent KV-cache evictions.

Small models (<4B) cannot reliably manage their own global context in-context. A host-side deterministic scaffolding system is strictly required.

## 2. Falsifiable Hypothesis

A deterministic, CPU-bound Lexical Salience Knapsack Packer operating on natural semantic boundaries (paragraphs/sentences) can compress an unstructured document stream of $2\text{k} - 32\text{k}$ tokens into a strictly bounded $\le 512$-token context window such that:
1. Hard Budget Invariant: Exactly $100\%$ ($30/30$) of packed outputs measure $\le 512$ tokens under the model's exact tokenizer (`llama-tokenize.exe`).
2. Boundary Preservation: $0$ sentences or structural fields are truncated midway.
3. Information Salience: Target query-relevant facts are preserved with $\ge 93.3\%$ recall ($\ge 28/30$ cases).
4. Runtime Overhead: Mean host packaging time is $< 15\text{ms}$ on CPU, while reducing inference Time-to-First-Token (TTFT) by $\ge 80\%$ compared to direct 8k ingestion.

## 3. Scope & Non-Goals

- **In Scope:**
  - Prototype implementation in `research/experiments/prototypes/mn-009-context-scaffolding/src/packer.py`.
  - Prefix-aligned system headers for prompt caching.
  - Deterministic evaluation corpus and offline unit tests (`tests/unit/test_mn009_packer.py`).
  - Comparative end-to-end validation against local `llama-server.exe`.
- **Out of Scope (Non-Goals):**
  - External vector databases, embedding models, or neural rerankers (VRAM and dependency bloat prohibited).
  - Premature promotion into `src/mong_nhiem/context/` prior to Gate D disposition.

## 4. Promotion Criteria (Gate D Gatekeeper)

Mã nguồn chỉ được xem xét promote vào `src/mong_nhiem/context/packer.py` khi:
1. Toàn bộ các tiêu chí nghiệm thu của Gate B đạt chuẩn tuyệt đối.
2. Không phát sinh hồi quy hoặc lỗi tràn token (zero overflow).
3. Biên bản Gate D Disposition Review được phê duyệt chính thức.
