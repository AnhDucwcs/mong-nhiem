"""Cross-platform guard for executable MN-004 script entries.

Windows worktrees normally do not expose the executable bit, while Ruff's
EXE001 check in Linux CI does.  Inspect the Git index directly so the same
condition is enforced before a squash merge on either platform.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIRECTORY = (
    REPOSITORY_ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-004-state-representation-intervention"
    / "scripts"
)


def test_mn004_shebang_scripts_are_tracked_as_executable() -> None:
    """Require the Git executable mode for each MN-004 Python shebang script."""
    script_paths = sorted(
        path
        for path in SCRIPTS_DIRECTORY.glob("*.py")
        if path.read_text(encoding="utf-8").startswith("#!")
    )
    relative_paths = [path.relative_to(REPOSITORY_ROOT).as_posix() for path in script_paths]

    result = subprocess.run(
        ["git", "ls-files", "-s", "--", *relative_paths],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    modes_by_path = {}
    for line in result.stdout.splitlines():
        mode, _blob, _stage, path = line.split(maxsplit=3)
        modes_by_path[path] = mode

    assert set(modes_by_path) == set(relative_paths)
    non_executable = [path for path in relative_paths if modes_by_path[path] != "100755"]
    assert not non_executable, (
        "MN-004 scripts with a shebang must be Git-tracked as executable "
        f"(100755): {', '.join(non_executable)}"
    )
