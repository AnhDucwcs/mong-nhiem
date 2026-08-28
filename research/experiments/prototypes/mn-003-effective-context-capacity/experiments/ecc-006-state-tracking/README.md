# ECC-006 — State Tracking under increasing context length

ECC-006 is the canonical MN-003 State Tracking baseline. It measures Llama 3.2 3B on six deterministic cases across 512, 2,048, 8,192, and 16,384 requested input tokens (24 measured requests). One target entity has exactly four chronological state updates; the model must return its final state. The entire update sequence is placed by the fixed midpoint policy while same-template distractor histories scale the context. Only context length varies.

The experiment does not test retrieval, RAG, memory, compression, routing, or another architecture. It also does not sweep update count, target count, sequence distribution, position, or a semantic-pressure dimension. A future ECC-007 is not justified by an imperfect result alone: it would require completed valid ECC-006 evidence whose ambiguity cannot be resolved through retained artifacts, validation, or a tooling correction.
