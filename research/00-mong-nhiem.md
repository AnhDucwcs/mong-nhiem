# Project

Mộng Nhiễm is intended to become a reusable research engine/library for exploring how small language models can reliably operate over information and context spaces substantially larger than their current effective capability.

## Current initial direction

Investigate efficient use of large external knowledge and context spaces while keeping the model's usable context constrained. No retrieval, storage, or context-management technique has been selected.

## Possible later direction

Investigate substantial effective or native context expansion while reducing long-context degradation, including positional degradation, lost-in-the-middle behavior, weaker logical reasoning over long contexts, context-overload hallucination, and failure to use information introduced much earlier. These are research concerns, not solved problems or committed technical approaches.

## Intended reuse

The library may later be integrated into agentic AI, games, chatbots, and local AI applications. Those integrations, along with research algorithms, model adapters, vector databases, and embedding choices, are explicitly out of scope for MN-001.
