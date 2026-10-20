"""Mộng Nhiễm Cognitive Architecture Package.

Authoritative cognitive governance kernel for real-time cyber-physical interaction,
bimodal emission, continuous state maintenance, and human supervisory control.
"""

from mong_nhiem.bimodal import BimodalEmission, BimodalParser, CommClass
from mong_nhiem.kernel import MongNhiemKernel, StepResult
from mong_nhiem.runtime.backends import (
    BaseInferenceBackend,
    LlamaServerBackend,
    MockBackend,
    OpenAICompatBackend,
    SubprocessLlamaBackend,
)
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
    "LlamaServerBackend",
    "MockBackend",
    "MongNhiemKernel",
    "OpenAICompatBackend",
    "StepResult",
    "SubprocessLlamaBackend",
    "TemporalBridge",
]
