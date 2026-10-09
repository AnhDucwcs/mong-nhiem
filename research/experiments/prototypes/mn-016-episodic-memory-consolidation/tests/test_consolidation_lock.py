"""Unit tests for Consolidation Mutex Lock."""

import sys
import tempfile
import time
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from consolidation_lock import ConsolidationLock, ConsolidationState


def test_lock_acquire_and_release() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        lock = ConsolidationLock(Path(tmpdir))
        assert not lock.is_locked()

        # Acquire lock
        assert lock.try_acquire(pid=1234)
        assert lock.is_locked()

        # Second acquire should fail while active
        assert not lock.try_acquire(pid=5678)

        # Release
        lock.release()
        assert not lock.is_locked()
        assert lock.try_acquire(pid=5678)


def test_lock_stale_recovery() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create lock with 1 second stale window
        lock = ConsolidationLock(Path(tmpdir), stale_seconds=1)
        assert lock.try_acquire(pid=100)

        # Wait until lock becomes stale
        time.sleep(1.2)
        assert not lock.is_locked()  # Outdated lock treated as released

        # New process should be able to take over stale lock
        assert lock.try_acquire(pid=200)


def test_state_load_and_save() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        lock = ConsolidationLock(Path(tmpdir))
        state = lock.load_state()
        assert state.consolidation_count == 0
        assert state.last_consolidated_tick == 0

        state.consolidation_count = 3
        state.last_consolidated_tick = 45
        lock.save_state(state)

        reloaded = lock.load_state()
        assert reloaded.consolidation_count == 3
        assert reloaded.last_consolidated_tick == 45
