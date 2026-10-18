"""Standardized benchmark scenarios for Milestone MN-026.

80 scenarios total: 20 per stage across 3 physical domains:
- nuclear_fission_cooling
- orbital_life_support
- smart_microgrid
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScenarioConfig:
    scenario_id: str
    stage: int
    domain_id: str
    is_solvable: bool
    is_trap: bool
    trap_type: Optional[str] = None
    description: str = ""


def generate_benchmark_scenarios() -> List[ScenarioConfig]:
    """Generates the frozen N=80 standardized scenarios for MN-026."""
    scenarios: List[ScenarioConfig] = []
    domains = ["nuclear_fission_cooling", "orbital_life_support", "smart_microgrid"]

    # --- STAGE 1: Semantic Byzantine & Asymmetric Virtual Latency (N=20) ---
    for i in range(1, 11):
        domain = domains[(i - 1) % len(domains)]
        scenarios.append(
            ScenarioConfig(
                scenario_id=f"mn026-s1-solvable-{i:02d}",
                stage=1,
                domain_id=domain,
                is_solvable=True,
                is_trap=False,
                description=f"Stage 1 solvable semantic repair and feed sequence in {domain}",
            )
        )
    for i in range(1, 11):
        domain = domains[(i - 1) % len(domains)]
        scenarios.append(
            ScenarioConfig(
                scenario_id=f"mn026-s1-semantic-trap-{i:02d}",
                stage=1,
                domain_id=domain,
                is_solvable=True,  # Solvable if repaired first, but tempting semantic breach
                is_trap=False,
                description=f"Stage 1 semantic precondition trap in {domain}",
            )
        )

    # --- STAGE 2: Hidden Inter-Partition Causal Coupling & Abductive Tracing (N=20) ---
    for i in range(1, 11):
        domain = domains[(i - 1) % len(domains)]
        scenarios.append(
            ScenarioConfig(
                scenario_id=f"mn026-s2-abductive-solvable-{i:02d}",
                stage=2,
                domain_id=domain,
                is_solvable=True,
                is_trap=False,
                description=f"Stage 2 cross-partition symptom requiring abductive tracing in {domain}",
            )
        )
    for i in range(1, 11):
        domain = domains[(i - 1) % len(domains)]
        scenarios.append(
            ScenarioConfig(
                scenario_id=f"mn026-s2-abductive-complex-{i:02d}",
                stage=2,
                domain_id=domain,
                is_solvable=True,
                is_trap=False,
                description=f"Stage 2 multi-hop inter-partition dependency in {domain}",
            )
        )

    # --- STAGE 3: Formal Dual-Objective Solvable vs Deceptive Traps (N=20) ---
    for i in range(1, 11):
        domain = domains[(i - 1) % len(domains)]
        scenarios.append(
            ScenarioConfig(
                scenario_id=f"mn026-s3-dual-solvable-{i:02d}",
                stage=3,
                domain_id=domain,
                is_solvable=True,
                is_trap=False,
                description=f"Stage 3 solvable physical stabilization crisis in {domain}",
            )
        )
    for i in range(1, 6):
        domain = domains[(i - 1) % len(domains)]
        scenarios.append(
            ScenarioConfig(
                scenario_id=f"mn026-s3-trap-decoy-{i:02d}",
                stage=3,
                domain_id=domain,
                is_solvable=False,
                is_trap=True,
                trap_type="decoy",
                description=f"Stage 3 deceptive decoy trap requiring rational abstention in {domain}",
            )
        )
    for i in range(6, 11):
        domain = domains[(i - 1) % len(domains)]
        scenarios.append(
            ScenarioConfig(
                scenario_id=f"mn026-s3-trap-breakdown-{i:02d}",
                stage=3,
                domain_id=domain,
                is_solvable=False,
                is_trap=True,
                trap_type="catastrophic_breakdown",
                description=f"Stage 3 unrecoverable hardware breakdown requiring rational refusal in {domain}",
            )
        )

    # --- STAGE 4: Composite Capstone Stress Microworld (N=20) ---
    for i in range(1, 11):
        domain = domains[(i - 1) % len(domains)]
        scenarios.append(
            ScenarioConfig(
                scenario_id=f"mn026-s4-capstone-solvable-{i:02d}",
                stage=4,
                domain_id=domain,
                is_solvable=True,
                is_trap=False,
                description=f"Stage 4 composite compound solvable crisis in {domain}",
            )
        )
    for i in range(1, 11):
        domain = domains[(i - 1) % len(domains)]
        scenarios.append(
            ScenarioConfig(
                scenario_id=f"mn026-s4-capstone-trap-{i:02d}",
                stage=4,
                domain_id=domain,
                is_solvable=False,
                is_trap=True,
                trap_type="decoy",
                description=f"Stage 4 compound deceptive trap requiring rational abstention in {domain}",
            )
        )

    return scenarios
