from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from scipy.io import savemat

from ppplot.api import compute_performance_profile_data, plot_performance_profile
from ppplot.io import parse_dataframe


def _df():
    return pd.DataFrame(
        {
            "inst": ["p1", "p2", "p3"],
            "A_metric": [1.0, 2.0, ""],
            "A_output": ["success", "timeout", ""],
            "B_metric": [2.0, 1.0, 1.5],
            "B_output": ["success", "success", "success"],
        }
    )


def test_parse_dataframe_detects_solvers():
    parsed = parse_dataframe(_df(), metric_suffix="metric", output_suffix="output")
    assert len(parsed.solver_specs) == 2
    assert parsed.solver_specs[0].solver_name == "A_"
    assert parsed.rows[2].metrics["A_"] is None


def test_compute_from_dataframe_matches_expected_row_count():
    result = compute_performance_profile_data(data=_df())
    assert result.rows == 3
    assert len(result.curves) == 2


def test_compute_from_numpy():
    matrix = np.array([[1.0, 2.0], [2.0, 1.0], [np.nan, 1.5]])
    result = compute_performance_profile_data(data=matrix, solver_names=["A_", "B_"])
    assert result.rows == 3
    assert {c.solver_name for c in result.curves} == {"A_", "B_"}


def test_compute_from_nested_dict():
    data = {
        "solvers": {
            "A_": {"metric": [1.0, 2.0, None], "output": ["success", "timeout", None]},
            "B_": {"metric": [2.0, 1.0, 1.5], "output": ["success", "success", "success"]},
        }
    }
    result = compute_performance_profile_data(data=data)
    assert result.rows == 3


def test_csv_input(tmp_path: Path):
    csv_path = tmp_path / "data.csv"
    _df().to_csv(csv_path, index=False)
    result = compute_performance_profile_data(file_path=csv_path)
    assert result.rows == 3


def test_mat_input_tabular(tmp_path: Path):
    mat_path = tmp_path / "data.mat"
    savemat(
        mat_path,
        {
            "A_metric": np.array([1.0, 2.0, np.nan]),
            "A_output": np.array(["success", "timeout", ""], dtype=object),
            "B_metric": np.array([2.0, 1.0, 1.5]),
            "B_output": np.array(["success", "success", "success"], dtype=object),
        },
    )
    result = compute_performance_profile_data(file_path=mat_path)
    assert result.rows == 3


def test_h5_input_nested(tmp_path: Path):
    h5_path = tmp_path / "data.h5"
    with h5py.File(h5_path, "w") as handle:
        g_a = handle.create_group("A_")
        g_a.create_dataset("metric", data=np.array([1.0, 2.0, np.nan]))
        g_a.create_dataset("output", data=np.array([b"success", b"timeout", b""]))

        g_b = handle.create_group("B_")
        g_b.create_dataset("metric", data=np.array([2.0, 1.0, 1.5]))
        g_b.create_dataset("output", data=np.array([b"success", b"success", b"success"]))

    result = compute_performance_profile_data(file_path=h5_path)
    assert result.rows == 3


def test_backend_matplotlib_returns_figure():
    fig = plot_performance_profile(data=_df(), backend="matplotlib")
    assert fig.__class__.__name__ == "Figure"


def test_backend_plotly_returns_figure():
    fig = plot_performance_profile(data=_df(), backend="plotly")
    assert fig.__class__.__name__ == "Figure"
