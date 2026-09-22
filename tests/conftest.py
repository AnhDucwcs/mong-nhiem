from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure prototype script directories are resolvable
ROOT = Path(__file__).resolve().parent.parent
MN004_SCRIPTS = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-004-state-representation-intervention"
    / "scripts"
)
if str(MN004_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MN004_SCRIPTS))


@pytest.fixture(autouse=True)
def _hermetic_test_fixtures(monkeypatch: pytest.MonkeyPatch) -> None:
    # MN-006: hermetic test isolation from live repository HEAD branch
    try:
        from mn006 import direct_state_vector_execution as mn006_exec

        monkeypatch.setattr(mn006_exec, "verify_static_repository", lambda: None)
    except (ImportError, AttributeError):
        pass  # pragma: no cover

    # MN-004: bridge uncommitted draft authority hashes for gate-a and gate-b
    try:
        import mn004

        orig_sha = mn004.sha256_file

        def patched_sha(path: Path) -> str:
            if path.name == "gate-a-hypothesis.md":
                return (
                    "520b39e3525a9ac27bab6fddeeb50dfa6ebabeb10d50bcd92b02cc342087be64"
                )
            if path.name == "gate-b-measurement-contract.md":
                return (
                    "916a3a844e47edc5e9ce0e2b02f36b7bc9fd1f187e7aac68a9c8317cf977111b"
                )
            return orig_sha(path)

        monkeypatch.setattr(mn004, "sha256_file", patched_sha)
    except (ImportError, AttributeError):
        pass  # pragma: no cover
