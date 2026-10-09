"""Domain-Agnostic State Affordance Engine and Provider Interfaces.

Provides declarative and extensible abstractions for computing valid, executable
state affordances (READ, INSPECT, DISPATCH, RESOLVE) without coupling to any
specific benchmark workload or domain schema.
100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .phase_gate import PhaseGate
from .protocol import AffordanceSpec


class BaseAffordanceProvider(ABC):
    """Abstract interface for calculating state-dependent action affordances."""

    @abstractmethod
    def get_affordances(
        self,
        env: Dict[str, Any],
        query: str,
        rejected_actions: Set[str],
        executed_actions: Set[str],
        target_predicate: Optional[Dict[str, Any]] = None,
        turn_index: int = 1,
    ) -> AffordanceSpec:
        """Calculate currently active affordance specification.
        
        Args:
            env: Current L2 environment dictionary S_t
            query: Task query string
            rejected_actions: Set of action_key strings rejected in prior rollbacks
            executed_actions: Set of action_key strings successfully executed in prior turns
            target_predicate: Goal specification predicate
            turn_index: Current execution turn index (1-based)
            
        Returns:
            AffordanceSpec with active reads, inspects, dispatches, and resolves.
        """
        raise NotImplementedError


class DeclarativeAffordanceEngine(BaseAffordanceProvider):
    """General-purpose, schema-driven affordance engine.
    
    Enables declarative registration of tools, inspectors, readers, and resolution
    guards with O(1) state precondition evaluation.
    """

    def __init__(self, phase_gate: Optional[PhaseGate] = None) -> None:
        self.phase_gate = phase_gate or PhaseGate()
        self._action_generators: List[
            Callable[
                [Dict[str, Any], str, Set[str], Set[str], int],
                List[Tuple[str, str]]
            ]
        ] = []
        self._read_generators: List[
            Callable[[Dict[str, Any], str, Set[str], Set[str]], List[str]]
        ] = []
        self._inspect_generators: List[
            Callable[[Dict[str, Any], str, Set[str], Set[str]], List[str]]
        ] = []
        self._resolution_extractor: Optional[
            Callable[[Dict[str, Any], Dict[str, Any], str], Optional[str]]
        ] = None

    def register_action_generator(
        self,
        generator_fn: Callable[
            [Dict[str, Any], str, Set[str], Set[str], int],
            List[Tuple[str, str]]
        ],
    ) -> None:
        """Register a generator that yields candidate (tool_name, payload) pairs."""
        self._action_generators.append(generator_fn)

    def register_read_generator(
        self,
        generator_fn: Callable[[Dict[str, Any], str, Set[str], Set[str]], List[str]],
    ) -> None:
        """Register a generator that yields candidate readable targets."""
        self._read_generators.append(generator_fn)

    def register_inspect_generator(
        self,
        generator_fn: Callable[[Dict[str, Any], str, Set[str], Set[str]], List[str]],
    ) -> None:
        """Register a generator that yields candidate inspectable entity.property paths."""
        self._inspect_generators.append(generator_fn)

    def set_resolution_extractor(
        self,
        extractor_fn: Callable[[Dict[str, Any], Dict[str, Any], str], Optional[str]],
    ) -> None:
        """Register an extractor that determines expected resolution payload from predicate."""
        self._resolution_extractor = extractor_fn

    def get_affordances(
        self,
        env: Dict[str, Any],
        query: str,
        rejected_actions: Set[str],
        executed_actions: Set[str],
        target_predicate: Optional[Dict[str, Any]] = None,
        turn_index: int = 1,
    ) -> AffordanceSpec:
        """Compute active affordances using registered generators and phase gating."""
        spec = AffordanceSpec()

        # 1. Check if goal is satisfied
        if target_predicate and self.phase_gate.verify_predicate(env, target_predicate):
            if self._resolution_extractor:
                res_val = self._resolution_extractor(env, target_predicate, query)
                if res_val:
                    spec.resolves.append(res_val)
                    return spec
            elif "expected_value" in target_predicate:
                spec.resolves.append(str(target_predicate["expected_value"]))
                return spec

        # 2. READ affordances
        for r_gen in self._read_generators:
            candidates = r_gen(env, query, rejected_actions, executed_actions)
            for cand in candidates:
                if f"READ:{cand}" not in rejected_actions and f"READ:{cand}" not in executed_actions:
                    if cand not in spec.reads:
                        spec.reads.append(cand)

        # 3. INSPECT affordances
        for i_gen in self._inspect_generators:
            candidates = i_gen(env, query, rejected_actions, executed_actions)
            for cand in candidates:
                if f"INSPECT:{cand}" not in rejected_actions and f"INSPECT:{cand}" not in executed_actions:
                    if cand not in spec.inspects:
                        spec.inspects.append(cand)

        # 4. DISPATCH affordances
        for a_gen in self._action_generators:
            candidates = a_gen(env, query, rejected_actions, executed_actions, turn_index)
            for tool, payload in candidates:
                key = f"DISPATCH:{tool}:{payload}"
                if key not in rejected_actions:
                    pair = (tool, payload)
                    if pair not in spec.dispatches:
                        spec.dispatches.append(pair)

        return spec
