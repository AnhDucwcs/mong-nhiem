# ECC-007 pre-freeze calibration

The calibration contract fixed direct context, a 512 requested-token anchor, midpoint placement, the causal-record template, deterministic seed, temperature 0, and a 16-token exact YES/NO response. It compared two and three causal hops with four cases each (two YES and two NO).

| Qualified model | 2-hop | 3-hop | Interpretation |
| --- | ---: | ---: | --- |
| Llama 3.2 3B | 0/4 | 0/4 | All outputs began an explanation and exhausted the 16-token budget without an exact YES/NO; an output-format floor under this fixed contract. |
| Qwen3-4B | 4/4 | 4/4 | Both candidate difficulties are above the 0.75 non-floor threshold. |

The selection rule therefore freezes two hops for the Qwen3-4B canonical run: it is the simpler candidate with sufficient short-context headroom. Calibration artifacts are retained in `runs/`; they are pre-freeze selection evidence, not canonical ECC measurement evidence.
