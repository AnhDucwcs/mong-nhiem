#!/usr/bin/env python3
"""Deterministic benchmark corpus generator for MN-011.

Generates 40 evaluation cases across two suites:
- Suite A: Parametric Budget Scaling Frontier (24 cases = 6 base tasks x 4 budgets: 256, 512, 1024, 2048)
- Suite B: Causal Reachability Scaffolding Restoration (16 cases across 512, 2k, 8k, 16k context lengths)

Outputs:
- definition/corpus-v1/cases.jsonl
- definition/corpus-v1/manifest.json
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "corpus-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CASES_FILE = OUT_DIR / "cases.jsonl"
MANIFEST_FILE = OUT_DIR / "manifest.json"


def generate_suite_a() -> list[dict]:
    """Suite A: 6 base integration problems evaluated across 4 budget tiers."""
    base_problems = [
        {
            "id": "policy_audit",
            "query": "Is user 'dev_alice' authorized to export production database dumps?",
            "oracle": "NO",
            "salient_facts": [
                "User 'dev_alice' has role 'Junior Developer'.",
                "Policy P-101: Role 'Junior Developer' clearance level is Tier 1.",
                "Policy P-205: Exporting production database dumps requires Tier 3 clearance.",
                "Override O-09: No emergency clearance granted to dev_alice.",
            ],
            "distractors": [
                f"Log event #{1000 + i}: Routine health check on server node {i % 10}. Status: OK."
                for i in range(40)
            ],
            "salient_tokens": 78,
        },
        {
            "id": "latency_budget",
            "query": "What is the total round-trip latency along the payment critical path?",
            "oracle": "85ms",
            "salient_facts": [
                "Hop 1: Edge Router to API Gateway takes 12ms.",
                "Hop 2: API Gateway to Auth Filter takes 18ms.",
                "Hop 3: Auth Filter to Payment Ledger takes 45ms.",
                "Hop 4: Payment Ledger local commit takes 10ms.",
            ],
            "distractors": [
                f"Telemetry item #{2000 + i}: Microservice telemetry metric heartbeat recorded at cluster {i}."
                for i in range(40)
            ],
            "salient_tokens": 65,
        },
        {
            "id": "risk_scoring",
            "query": "Does transaction TX-9921 trigger immediate anti-fraud suspension?",
            "oracle": "YES",
            "salient_facts": [
                "Transaction TX-9921 amount is $14,500 USD.",
                "Rule R-1: Cross-border transfers exceeding $10,000 USD require geo-verification.",
                "Condition C-4: Origin IP country 'NL' differs from card issue country 'US'.",
                "Action A-9: High-value cross-border geo-mismatch triggers immediate suspension.",
            ],
            "distractors": [
                f"Metric record #{3000 + i}: Normal card checkout completed for account ACC-{i}."
                for i in range(40)
            ],
            "salient_tokens": 72,
        },
        {
            "id": "deployment_health",
            "query": "What is the cluster deployment status for Release-v4.2?",
            "oracle": "DEGRADED",
            "salient_facts": [
                "Pod web-frontend is HEALTHY with 10/10 replicas ready.",
                "Pod auth-worker is HEALTHY with 5/5 replicas ready.",
                "Pod billing-worker is CRASH_LOOP_BACKOFF with 0/3 replicas ready.",
                "Release rule: Any essential worker in crash state marks release as DEGRADED.",
            ],
            "distractors": [
                f"System metric #{4000 + i}: CPU temperature on worker node worker-{i % 8} is normal."
                for i in range(40)
            ],
            "salient_tokens": 70,
        },
        {
            "id": "quorum_consistency",
            "query": "Has Raft group consensus been achieved on commit index 504?",
            "oracle": "YES",
            "salient_facts": [
                "Cluster total voter count is 5 nodes.",
                "Quorum rule: Consensus requires at least 3 positive ACKs.",
                "Node 1 (Leader), Node 2, and Node 3 have persisted index 504.",
                "Node 4 and Node 5 have uncommitted status for index 504.",
            ],
            "distractors": [
                f"Heartbeat line #{5000 + i}: Follower ping received within 150ms timeout window."
                for i in range(40)
            ],
            "salient_tokens": 68,
        },
        {
            "id": "storage_replication",
            "query": "Is customer volume VOL-331 fully multi-region replicated?",
            "oracle": "NO",
            "salient_facts": [
                "Customer volume VOL-331 replication policy requires 3 distinct zones.",
                "Zone us-east-1a status is SYNCED.",
                "Zone us-east-1b status is SYNCED.",
                "Zone eu-central-1a status is REPLICATION_LAGGING_PAUSED.",
            ],
            "distractors": [
                f"Disk telemetry #{6000 + i}: IOPS read throughput within target SLO baseline."
                for i in range(40)
            ],
            "salient_tokens": 66,
        },
    ]

    budgets = [256, 512, 1024, 2048]
    cases = []
    case_idx = 1

    for bp in base_problems:
        for b in budgets:
            cases.append({
                "case_id": f"mn011-suite-a-{case_idx:04d}",
                "suite": "suite_a_budget_scaling",
                "problem_id": bp["id"],
                "budget": b,
                "query": bp["query"],
                "oracle_answer": bp["oracle"],
                "salient_facts": bp["salient_facts"],
                "distractors": bp["distractors"],
                "salient_token_count": bp["salient_tokens"],
            })
            case_idx += 1

    return cases


def generate_suite_b() -> list[dict]:
    """Suite B: 16 Causal Reachability cases across 512, 2k, 8k, 16k context tiers."""
    context_tiers = [512, 2048, 8192, 16384]
    distractor_counts = {512: 10, 2048: 60, 8192: 250, 16384: 520}
    cases = []
    case_idx = 1

    for tier in context_tiers:
        num_distractors = distractor_counts[tier]

        # 2 Positive cases (SOURCE causes TARGET via 2-hop chain)
        for p in range(1, 3):
            src = f"Alpha_{tier}_{p}"
            mid = f"Beta_{tier}_{p}"
            tgt = f"Omega_{tier}_{p}"

            chain = [
                f"{src} directly causes {mid}.",
                f"{mid} directly causes {tgt}.",
            ]

            distractors = [
                f"Node_Distractor_{i}_{tier} directly causes Node_Distractor_{i + 1}_{tier}."
                for i in range(num_distractors)
            ]

            cases.append({
                "case_id": f"mn011-suite-b-{case_idx:04d}",
                "suite": "suite_b_causal_reachability",
                "context_tier": tier,
                "reachability_type": "POSITIVE",
                "source": src,
                "target": tgt,
                "query": f"Does {src} eventually cause {tgt}? Return only YES or NO.",
                "oracle_answer": "YES",
                "causal_chain": chain,
                "distractors": distractors,
            })
            case_idx += 1

        # 2 Negative cases (SOURCE does NOT cause TARGET)
        for n in range(1, 3):
            src = f"Gamma_{tier}_{n}"
            mid = f"Delta_{tier}_{n}"
            other = f"Epsilon_{tier}_{n}"
            tgt = f"Zeta_{tier}_{n}"

            chain = [
                f"{src} directly causes {mid}.",
                f"{other} directly causes {tgt}.",  # Disconnected from src
            ]

            distractors = [
                f"Node_Distractor_{i}_{tier} directly causes Node_Distractor_{i + 1}_{tier}."
                for i in range(num_distractors)
            ]

            cases.append({
                "case_id": f"mn011-suite-b-{case_idx:04d}",
                "suite": "suite_b_causal_reachability",
                "context_tier": tier,
                "reachability_type": "NEGATIVE",
                "source": src,
                "target": tgt,
                "query": f"Does {src} eventually cause {tgt}? Return only YES or NO.",
                "oracle_answer": "NO",
                "causal_chain": chain,
                "distractors": distractors,
            })
            case_idx += 1

    return cases


def main() -> None:
    suite_a = generate_suite_a()
    suite_b = generate_suite_b()
    all_cases = suite_a + suite_b

    lines = [json.dumps(c, ensure_ascii=False) for c in all_cases]
    content = "\n".join(lines) + "\n"

    CASES_FILE.write_text(content, encoding="utf-8")
    sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

    manifest = {
        "version": "1.0.0",
        "total_cases": len(all_cases),
        "suites": {
            "suite_a_budget_scaling": len(suite_a),
            "suite_b_causal_reachability": len(suite_b),
        },
        "sha256": sha256,
        "cases_file": CASES_FILE.name,
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(all_cases)} cases -> {CASES_FILE} (SHA256: {sha256})")


if __name__ == "__main__":
    main()
