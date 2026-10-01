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

