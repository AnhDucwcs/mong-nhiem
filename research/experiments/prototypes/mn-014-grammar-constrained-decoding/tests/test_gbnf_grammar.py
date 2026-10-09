"""Unit tests validating GBNF grammar file structure for MN-014."""
from pathlib import Path


def test_gbnf_file_exists_and_valid():
    grammar_path = Path(__file__).parent.parent / "definition" / "grammar" / "action_grammar.gbnf"
    assert grammar_path.exists(), "action_grammar.gbnf must exist"
    
    content = grammar_path.read_text(encoding="utf-8")
    assert "root ::= action" in content
    assert "action ::= \"ACTION: \"" in content
    assert "read_action ::=" in content
    assert "inspect_action ::=" in content
    assert "dispatch_action ::=" in content
    assert "resolve_action ::=" in content
    assert "identifier ::=" in content
    assert "payload ::=" in content
