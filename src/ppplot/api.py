from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import numpy as np
import numpy.typing as npt
import pandas as pd

from .filtering import apply_output_filter, parse_allowed_outputs
from .io import parse_input_data, parse_input_file
from .plotting import render_profile
from .profile import compute_performance_profiles
from .types import Backend, MetricDirection, ProfileResult, XScale

DEFAULT_ALLOWED_OUTPUTS = ("ok", "success", "optimal")
DEFAULT_TITLE = "Performance Profile"
DEFAULT_X_LABEL = "Performance ratio (tau)"
DEFAULT_Y_LABEL = "Percentage of problems solved"


def compute_performance_profile_data(
    *,
    data: pd.DataFrame | npt.NDArray[np.float64] | dict[str, Any] | None = None,
    file_path: str | Path | None = None,
    metric_suffix: str = "metric",
    output_suffix: str = "output",
    allowed_outputs: Iterable[str] = DEFAULT_ALLOWED_OUTPUTS,
    direction: MetricDirection = "minimize",
    tau_max: float = 5,
    tau_samples: int = 150,
    solver_names: list[str] | None = None,
) -> ProfileResult:
    if (data is None) == (file_path is None):
        raise ValueError("Provide exactly one source: either 'data' or 'file_path'.")

    if data is not None:
        parsed = parse_input_data(
            data,
            metric_suffix=metric_suffix,
            output_suffix=output_suffix,
            solver_names=solver_names,
        )
    elif file_path is not None:
        parsed = parse_input_file(
            file_path=file_path,
            metric_suffix=metric_suffix,
            output_suffix=output_suffix,
        )
    else:
        raise ValueError("Unexpected error: no data source provided.")

    allowed = parse_allowed_outputs(allowed_outputs)
    filtered_rows = apply_output_filter(parsed.rows, parsed.solver_specs, allowed_outputs=allowed)

    return compute_performance_profiles(
        rows=filtered_rows,
        solver_specs=parsed.solver_specs,
        direction=direction,
        tau_max=tau_max,
        tau_samples=tau_samples,
    )


def plot_performance_profile(
    *,
    data: pd.DataFrame | npt.NDArray[np.float64] | dict[str, Any] | None = None,
    file_path: str | Path | None = None,
    backend: Backend = "matplotlib",
    metric_suffix: str = "metric",
    output_suffix: str = "output",
    allowed_outputs: Iterable[str] = DEFAULT_ALLOWED_OUTPUTS,
    direction: MetricDirection = "minimize",
    title: str = DEFAULT_TITLE,
    x_label: str = DEFAULT_X_LABEL,
    y_label: str = DEFAULT_Y_LABEL,
    x_scale: XScale = "linear",
    tau_max: float = 5,
    tau_samples: int = 150,
    solver_names: list[str] | None = None,
    solver_labels: dict[str, str] | None = None,
):
    profile = compute_performance_profile_data(
        data=data,
        file_path=file_path,
        metric_suffix=metric_suffix,
        output_suffix=output_suffix,
        allowed_outputs=allowed_outputs,
        direction=direction,
        tau_max=tau_max,
        tau_samples=tau_samples,
        solver_names=solver_names,
    )

    return render_profile(
        backend=backend,
        profile=profile,
        title=title,
        x_label=x_label,
        y_label=y_label,
        x_scale=x_scale,
        solver_labels=solver_labels,
    )
