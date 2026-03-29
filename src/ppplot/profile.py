from __future__ import annotations

import math

from .types import MetricDirection, ProfileCurve, ProfileResult, RawRecord, SolverSpec


def is_valid_metric(value: float | None) -> bool:
    return value is not None and math.isfinite(value) and value > 0


def build_tau_grid(max_tau: float, sample_count: int) -> list[float]:
    max_value = max(1.0, float(max_tau))
    samples = max(10, int(sample_count))
    if samples == 1:
        return [1.0]
    step = (max_value - 1.0) / (samples - 1)
    return [1.0 + step * i for i in range(samples)]


def _baseline(values: list[float], direction: MetricDirection) -> float:
    if direction == "maximize":
        return max(values)
    return min(values)


def compute_ratios_for_row(
    row: RawRecord,
    solver_specs: list[SolverSpec],
    direction: MetricDirection,
) -> dict[str, float]:
    valid_values = [
        value if value is not None else math.inf
        for spec in solver_specs
        for value in [row.metrics.get(spec.solver_name)]
        if is_valid_metric(value)
    ]

    ratios: dict[str, float] = {}
    if not valid_values:
        for spec in solver_specs:
            ratios[spec.solver_name] = math.inf
        return ratios

    baseline = _baseline(valid_values, direction)

    for spec in solver_specs:
        value = row.metrics.get(spec.solver_name)
        if not is_valid_metric(value):
            ratios[spec.solver_name] = math.inf
            continue
        assert value is not None  # For type checker

        if direction == "maximize":
            ratios[spec.solver_name] = baseline / value
        else:
            ratios[spec.solver_name] = value / baseline

    return ratios


def compute_performance_profiles(
    rows: list[RawRecord],
    solver_specs: list[SolverSpec],
    direction: MetricDirection = "minimize",
    tau_max: float = 5,
    tau_samples: int = 150,
) -> ProfileResult:
    tau_values = build_tau_grid(tau_max, tau_samples)
    ratios_by_row = [compute_ratios_for_row(row, solver_specs, direction) for row in rows]

    curves: list[ProfileCurve] = []
    row_count = len(ratios_by_row)

    for spec in solver_specs:
        solver_name = spec.solver_name
        rho: list[float] = []
        for tau in tau_values:
            count = 0
            for row_ratios in ratios_by_row:
                if row_ratios.get(solver_name, math.inf) <= tau:
                    count += 1
            rho.append((count / row_count) if row_count else 0.0)

        curves.append(ProfileCurve(solver_name=solver_name, tau=tau_values, rho=rho))

    return ProfileResult(curves=curves, rows=len(rows))
