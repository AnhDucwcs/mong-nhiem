def test_package_imports() -> None:
    import mong_nhiem

    assert mong_nhiem.__name__ == "mong_nhiem"


def test_context_subsystem_imports() -> None:
    from mong_nhiem.context import (
        ContextPacker,
        TextChunk,
        InvariantViolationError,
        sanitize_chat_tokens,
        assert_temporal_invariant,
        slice_graph_by_khop,
        slice_table_by_projection,
        CodebaseSlicer,
        slice_codebase,
    )

    packer = ContextPacker(max_budget=512)
    assert packer.max_budget == 512
    packed = packer.pack(["Hello world context."], query="Hello?")
    assert "Hello world" in packed

    code = "def add(a, b): return a + b\ndef target(): return add(1, 2)"
    sliced = slice_codebase(code, target_function="target")
    assert "def target():" in sliced


def test_orchestration_subsystem_imports() -> None:
    from mong_nhiem.orchestration import (
        ActionType,
        AffordanceSpec,
        BaseAffordanceProvider,
        CircuitBreaker,
        CircuitBreakerStatus,
        CognitiveOrchestrator,
        ContextRewindManager,
        DeclarativeAffordanceEngine,
        DynamicGBNFCompiler,
        Memento,
        MementoStack,
        OrchestratorResult,
        PhaseGate,
        ToolAction,
        TurnRecord,
        format_action,
        format_affordance_prior,
        parse_action,
    )

    spec = AffordanceSpec(reads=["doc1"], dispatches=[("fetch", "key")])
    gbnf = DynamicGBNFCompiler.compile(spec)
    assert "read-action" in gbnf
    assert "fetch key" in gbnf

    stack = MementoStack()
    stack.push(turn_index=0, state={"status": "init"})
    assert len(stack) == 1
    assert stack.pop().state == {"status": "init"}


def test_core_subsystem_imports() -> None:
    from mong_nhiem.core import (
        CausalEvent,
        ConservationInvariantGuard,
        InvariantViolationError,
        VectorClock,
    )

    evt = CausalEvent("e1", 0, "a1", "ACT", "res1")
    assert evt.verify_integrity() is True
    vc = VectorClock({"a1": 1})
    assert vc.get("a1") == 1
    guard = ConservationInvariantGuard()
    guard.enforce({"mass": 10.0})


def test_autodream_subsystem_imports() -> None:
    from mong_nhiem.extensions.autodream import (
        AutoDreamConsolidator,
        FactCardProjector,
        FrontierBranchPruner,
    )

    proj = FactCardProjector(default_token_ceiling=512)
    card = proj.render_card("res1", version=1)
    assert "[res1 v1]" in card

    consolidator = AutoDreamConsolidator()
    assert consolidator.target_compaction_ratio == 0.70


def test_knowledge_subsystem_imports() -> None:
    from mong_nhiem.knowledge import (
        CausalEventDAG,
        CausalNode,
        DynamicSchemaRegistry,
        EntitySchema,
        EpistemicObservation,
        EpistemicReconciler,
        ReconciliationResult,
    )

    dag = CausalEventDAG()
    node = dag.add_event("a1", "ACT", "target1")
    assert node.event_id in dag._nodes

    registry = DynamicSchemaRegistry()
    registry.emerge_entity("ent1", "type1", {"val": 1})
    assert registry.is_active("ent1") is True


def test_runtime_subsystem_imports() -> None:
    from mong_nhiem.runtime import AuthoritativeMicroworld

    world = AuthoritativeMicroworld(initial_state={"battery": 50.0})
    world.advance_tick()
    assert world.current_tick == 1


def test_root_package_cognitive_kernel_exports() -> None:
    import mong_nhiem

    expected_exports = [
        "BaseInferenceBackend",
        "BimodalEmission",
        "BimodalParser",
        "ClockMode",
        "CommClass",
        "CompiledWorldSchema",
        "ContinuousStateEngine",
        "DeclarativeSchemaLoader",
        "HumanCommandRecord",
        "HumanSupervisoryBridge",
        "LlamaServerBackend",
        "MockBackend",
        "MongNhiemKernel",
        "OpenAICompatBackend",
        "SlotCacheManager",
        "SlotExecutionMode",
        "StepResult",
        "SubprocessLlamaBackend",
        "TemporalBridge",
        "compile_bimodal_gbnf_grammar",
        "find_free_port",
        "is_port_in_use",
    ]

    for sym in expected_exports:
        assert hasattr(mong_nhiem, sym), f"Symbol {sym} missing from root mong_nhiem namespace"

    assert mong_nhiem.is_port_in_use(mong_nhiem.find_free_port()) is False




