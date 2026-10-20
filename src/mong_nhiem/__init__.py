"""Mộng Nhiễm Cognitive Architecture Package.

Authoritative cognitive governance kernel for real-time cyber-physical interaction,
bimodal emission, continuous state maintenance, and human supervisory control.
"""

from mong_nhiem.bimodal import (
    BimodalEmission,
    BimodalParser,
    CommClass,
    compile_bimodal_gbnf_grammar,
)
from mong_nhiem.kernel import MongNhiemKernel, StepResult
from mong_nhiem.preemption import HumanCommandRecord, HumanSupervisoryBridge
from mong_nhiem.runtime.backends import (
    BaseInferenceBackend,
    LlamaServerBackend,
    MockBackend,
    OpenAICompatBackend,
    SubprocessLlamaBackend,
    find_free_port,
    is_port_in_use,
)
from mong_nhiem.runtime.slot_cache import SlotCacheManager, SlotExecutionMode
from mong_nhiem.schema import CompiledWorldSchema, DeclarativeSchemaLoader
from mong_nhiem.state import ContinuousStateEngine
from mong_nhiem.temporal import ClockMode, TemporalBridge

__version__ = "0.2.0"

__all__ = [
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
