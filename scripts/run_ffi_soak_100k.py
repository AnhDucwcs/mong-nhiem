"""Standalone 100,000-Iteration C-ABI Soak Test for mong_nhiem.dll.

Measures process RSS memory before and after 100,000 C-ABI calls across FFI boundaries.
Zero external dependencies.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import gc
import sys
import time
from pathlib import Path


def get_working_set_bytes() -> int:
    if sys.platform == "win32":
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        pmc = PROCESS_MEMORY_COUNTERS()
        pmc.cb = ctypes.sizeof(pmc)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(pmc), pmc.cb):
            return int(pmc.WorkingSetSize)
    return 0


class FfiStepResult(ctypes.Structure):
    _fields_ = [
        ("action_verb", ctypes.c_char_p),
        ("comm_class", ctypes.c_char_p),
        ("comm_message", ctypes.c_char_p),
        ("tick", ctypes.c_ulonglong),
        ("delta_time", ctypes.c_double),
        ("state_json", ctypes.c_char_p),
        ("has_fired_invariants", ctypes.c_int),
    ]


def main() -> None:
    dll_path = Path(__file__).resolve().parent.parent / "target" / "release" / "mong_nhiem.dll"
    if not dll_path.exists():
        print(f"ERROR: DLL not found at {dll_path}")
        sys.exit(1)

    mn_core = ctypes.CDLL(str(dll_path))
    mn_core.mong_nhiem_kernel_new.restype = ctypes.c_void_p
    mn_core.mong_nhiem_kernel_free.argtypes = [ctypes.c_void_p]

    mn_core.mong_nhiem_tick.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_double,
        ctypes.POINTER(FfiStepResult),
    ]
    mn_core.mong_nhiem_tick.restype = ctypes.c_int
    mn_core.mong_nhiem_free_step_result.argtypes = [ctypes.POINTER(FfiStepResult)]

    kernel = mn_core.mong_nhiem_kernel_new()
    res = FfiStepResult()

    print("Running 100 warm-up cycles...")
    for _ in range(100):
        mn_core.mong_nhiem_tick(kernel, b"warmup", 0.1, ctypes.byref(res))
        mn_core.mong_nhiem_free_step_result(ctypes.byref(res))

    gc.collect()
    rss_start = get_working_set_bytes()
    t_start = time.perf_counter()

    iterations = 100000
    print(f"Starting {iterations:,} soak iterations...")
    for i in range(1, iterations + 1):
        ret = mn_core.mong_nhiem_tick(kernel, b"tick_stimulus", 0.05, ctypes.byref(res))
        mn_core.mong_nhiem_free_step_result(ctypes.byref(res))
        if i % 25000 == 0:
            current_rss = get_working_set_bytes()
            delta_mb = (current_rss - rss_start) / (1024 * 1024)
            print(f"  Iteration {i:,} / {iterations:,} - Current delta RSS: {delta_mb:+.3f} MB")

    t_end = time.perf_counter()
    gc.collect()
    rss_end = get_working_set_bytes()
    delta_total_mb = (rss_end - rss_start) / (1024 * 1024)
    elapsed_sec = t_end - t_start
    per_call_us = (elapsed_sec / iterations) * 1e6

    mn_core.mong_nhiem_kernel_free(kernel)

    print("\n--- 100k Soak Test Results ---")
    print(f"Total Iterations: {iterations:,}")
    print(f"Elapsed Time:     {elapsed_sec:.3f} s")
    print(f"Throughput:       {iterations / elapsed_sec:,.0f} ticks/s")
    print(f"Latency per tick: {per_call_us:.3f} microseconds")
    print(f"RSS Memory Delta: {delta_total_mb:+.3f} MB (Threshold: < 0.5 MB)")
    if delta_total_mb < 0.5:
        print("VERDICT: PASS (Zero Memory Leak)")
    else:
        print("VERDICT: FAIL (Memory Leak Detected)")


if __name__ == "__main__":
    main()
