"""Unit Tests for Promoted Bimodal Cognitive Emission Module."""

from mong_nhiem.bimodal import (
    BimodalParser,
    CommClass,
    compile_bimodal_gbnf_grammar,
)


def test_bimodal_parser_valid_inform():
    raw = 'ACTION: PURGE_PRIMARY_CORE\nCOMMUNICATE [INFORM]: "Initiating core coolant venting."'
    emission = BimodalParser.parse(raw)
    assert emission.valid is True
    assert emission.action_verb == "PURGE_PRIMARY_CORE"
    assert emission.comm_class == CommClass.INFORM
    assert emission.comm_message == "Initiating core coolant venting."
    assert emission.full_action_str == "PURGE_PRIMARY_CORE"


def test_bimodal_parser_valid_query_with_params():
    raw = 'ACTION: ENGAGE_FEEDER circuit=grid_a duration=30\nCOMMUNICATE [QUERY]: "Confirm engagement of grid A?"'
    emission = BimodalParser.parse(raw)
    assert emission.valid is True
    assert emission.action_verb == "ENGAGE_FEEDER"
    assert emission.action_params == {"circuit": "grid_a", "duration": "30"}
    assert emission.comm_class == CommClass.QUERY
    assert emission.comm_message == "Confirm engagement of grid A?"


def test_bimodal_parser_valid_express():
    raw = 'ACTION: REPORT_STATUS\nCOMMUNICATE [EXPRESS]: "Reactor hums smoothly today."'
    emission = BimodalParser.parse(raw)
    assert emission.valid is True
    assert emission.action_verb == "REPORT_STATUS"
    assert emission.comm_class == CommClass.EXPRESS
    assert emission.comm_message == "Reactor hums smoothly today."


def test_bimodal_parser_malformed_syntax():
    # Missing COMMUNICATE line
    emission1 = BimodalParser.parse("ACTION: PURGE_CORE")
    assert emission1.valid is False
    assert emission1.action_verb == "SYNTAX_ERROR"
    assert "COMMUNICATE" in emission1.parse_error

    # Missing ACTION line
    emission2 = BimodalParser.parse('COMMUNICATE [INFORM]: "Hello"')
    assert emission2.valid is False
    assert emission2.action_verb == "SYNTAX_ERROR"
    assert "ACTION" in emission2.parse_error

    # Empty text
    emission3 = BimodalParser.parse("")
    assert emission3.valid is False
    assert emission3.action_verb == "ABSTAIN"


def test_compile_bimodal_gbnf_grammar():
    grammar = compile_bimodal_gbnf_grammar(
        allowed_verbs=["ENGAGE", "DISENGAGE", "ABSTAIN"],
        allowed_comm_classes=[CommClass.INFORM, CommClass.QUERY],
    )
    assert 'root ::= action-line "\\n" comm-line' in grammar
    assert '"ENGAGE" | "DISENGAGE" | "ABSTAIN"' in grammar
    assert '"INFORM" | "QUERY"' in grammar
    assert '"EXPRESS"' not in grammar  # strictly constrained
