from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

MetricDirection = Literal["minimize", "maximize"]
XScale = Literal["linear", "log"]
Backend = Literal["matplotlib", "plotly"]


@dataclass(frozen=True)
class SolverSpec:
    solver_name: str
    metric_header: str
    output_header: Optional[str]


@dataclass(frozen=True)
class RawRecord:
    metrics: Dict[str, Optional[float]]
    outputs: Dict[str, Optional[str]]


@dataclass(frozen=True)
class ParsedDataset:
    headers: List[str]
    rows: List[RawRecord]
    solver_specs: List[SolverSpec]


@dataclass(frozen=True)
class ProfileCurve:
    solver_name: str
    tau: List[float]
    rho: List[float]


@dataclass(frozen=True)
class ProfileResult:
    curves: List[ProfileCurve]
    rows: int
