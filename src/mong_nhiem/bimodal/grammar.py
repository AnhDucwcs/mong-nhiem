"""GBNF Grammar Compiler for Bimodal Cognitive Emission.

Constrains small language models (<4B) to emit single-pass operational actions
alongside triadic communicative acts (INFORM, QUERY, EXPRESS) under strict CFG.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from mong_nhiem.bimodal.protocol import CommClass


def compile_bimodal_gbnf_grammar(
    allowed_verbs: list[str] | None = None,
    allowed_comm_classes: list[CommClass] | None = None,
) -> str:
    """Compiles a Context-Free GBNF Grammar constraining single-pass bimodal emission."""
    if allowed_verbs:
        verb_alts = " | ".join(f'"{v}"' for v in allowed_verbs)
        verb_rule = f"action-verb ::= {verb_alts}"
    else:
        verb_rule = 'action-verb ::= [A-Z_]+'

    if allowed_comm_classes:
        comm_alts = " | ".join(f'"{c.value}"' for c in allowed_comm_classes)
        comm_class_rule = f"comm-type ::= {comm_alts}"
    else:
        comm_class_rule = 'comm-type ::= "INFORM" | "QUERY" | "EXPRESS"'

    grammar = f"""root ::= action-line "\\n" comm-line
action-line ::= "ACTION: " action-verb action-args?
action-args ::= (" " [a-zA-Z0-9_=.:/-]+)+
{verb_rule}
comm-line ::= "COMMUNICATE [" comm-type "]: \\"" message-body "\\""
{comm_class_rule}
message-body ::= [^"\\r\\n]+
"""
    return grammar
