import math

from ppplot.profile import build_tau_grid, compute_performance_profiles
from ppplot.types import RawRecord, SolverSpec


def _sample_rows():
    return [
        RawRecord(metrics={"A_": 1.0, "B_": 2.0}, outputs={"A_": "ok", "B_": "ok"}),
        RawRecord(metrics={"A_": 2.0, "B_": 1.0}, outputs={"A_": "ok", "B_": "ok"}),
        RawRecord(metrics={"A_": None, "B_": 1.0}, outputs={"A_": None, "B_": "ok"}),
    ]


def _sample_specs():
    return [
        SolverSpec(solver_name="A_", metric_header="A_metric", output_header="A_output"),
        SolverSpec(solver_name="B_", metric_header="B_metric", output_header="B_output"),
    ]


def test_tau_grid_bounds_and_min_samples():
    tau = build_tau_grid(max_tau=3, sample_count=4)
    assert len(tau) == 10
    assert math.isclose(tau[0], 1.0)
    assert math.isclose(tau[-1], 3.0)


def test_profile_minimize_direction():
    result = compute_performance_profiles(
        rows=_sample_rows(),
        solver_specs=_sample_specs(),
        direction="minimize",
        tau_max=2,
        tau_samples=10,
    )
    assert result.rows == 3
    curves = {curve.solver_name: curve for curve in result.curves}
    assert curves["A_"].rho[0] == 1 / 3
    assert curves["B_"].rho[0] == 2 / 3


def test_profile_maximize_direction():
    rows = [
        RawRecord(metrics={"A_": 10.0, "B_": 5.0}, outputs={"A_": "ok", "B_": "ok"}),
        RawRecord(metrics={"A_": 3.0, "B_": 6.0}, outputs={"A_": "ok", "B_": "ok"}),
    ]
    result = compute_performance_profiles(
        rows=rows,
        solver_specs=_sample_specs(),
        direction="maximize",
        tau_max=2,
        tau_samples=10,
    )
    curves = {curve.solver_name: curve for curve in result.curves}
    assert curves["A_"].rho[0] == 1 / 2
    assert curves["B_"].rho[0] == 1 / 2
