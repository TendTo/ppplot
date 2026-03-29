from __future__ import annotations

from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
from scipy.io import loadmat

from .types import ParsedDataset, RawRecord, SolverSpec


def normalize_header_name(value: str) -> str:
    return str(value).strip()


def _is_missing_scalar(cell: Any) -> bool:
    if cell is None:
        return True
    if isinstance(cell, (np.ndarray, list, tuple, dict, set)):
        return False
    try:
        return bool(pd.isna(cell))
    except (TypeError, ValueError):
        return False


def parse_metric_cell(cell: Any) -> float | None:
    if _is_missing_scalar(cell):
        return None
    if isinstance(cell, str):
        text = cell.strip()
        if not text or text.lower() in {"inf", "infinity", "+inf", "+infinity", "nan", "null"}:
            return None
        try:
            numeric = float(text)
        except ValueError:
            return None
    else:
        try:
            numeric = float(cell)
        except (TypeError, ValueError):
            return None

    if not np.isfinite(numeric):
        return None
    return numeric


def parse_output_cell(cell: Any) -> str | None:
    if _is_missing_scalar(cell):
        return None
    text = str(cell).strip()
    if not text:
        return None
    return text


def detect_solvers(headers: list[str], metric_suffix: str, output_suffix: str) -> list[SolverSpec]:
    metric_suffix = metric_suffix.strip()
    output_suffix = output_suffix.strip()

    if not metric_suffix:
        raise ValueError("Metric suffix cannot be empty.")

    normalized_headers = [normalize_header_name(header) for header in headers]
    metric_headers = [header for header in normalized_headers if header.endswith(metric_suffix)]
    if not metric_headers:
        raise ValueError(f"No metric columns found. Expected one or more headers ending with '{metric_suffix}'.")

    solver_specs: list[SolverSpec] = []
    header_set = set(normalized_headers)
    for metric_header in metric_headers:
        solver_name = metric_header[: -len(metric_suffix)]
        output_header_candidate = f"{solver_name}{output_suffix}" if output_suffix else ""
        output_header = output_header_candidate if output_header_candidate in header_set else None
        solver_specs.append(
            SolverSpec(
                solver_name=solver_name,
                metric_header=metric_header,
                output_header=output_header,
            )
        )

    return solver_specs


def parse_rows_from_dataframe(df: pd.DataFrame, solver_specs: list[SolverSpec]) -> list[RawRecord]:
    rows: list[RawRecord] = []
    for _, row in df.iterrows():
        metrics: dict[str, float | None] = {}
        outputs: dict[str, str | None] = {}
        for spec in solver_specs:
            metrics[spec.solver_name] = parse_metric_cell(row.get(spec.metric_header))
            outputs[spec.solver_name] = parse_output_cell(row.get(spec.output_header)) if spec.output_header else None
        rows.append(RawRecord(metrics=metrics, outputs=outputs))
    return rows


def parse_dataframe(
    dataframe: pd.DataFrame,
    metric_suffix: str = "metric",
    output_suffix: str = "output",
) -> ParsedDataset:
    headers = [normalize_header_name(col) for col in dataframe.columns]
    df: pd.DataFrame = dataframe.copy()  # type: ignore
    df.columns = headers
    solver_specs = detect_solvers(headers, metric_suffix=metric_suffix, output_suffix=output_suffix)
    rows = parse_rows_from_dataframe(df, solver_specs)
    return ParsedDataset(headers=headers, rows=rows, solver_specs=solver_specs)


def parse_ndarray(
    matrix: np.ndarray,
    solver_names: list[str] | None = None,
) -> ParsedDataset:
    arr = np.asarray(matrix)
    if arr.ndim != 2:
        raise ValueError("NumPy input must be a 2D array of shape (rows, solvers).")

    _, solver_count = arr.shape
    if solver_names is not None and len(solver_names) != solver_count:
        raise ValueError("solver_names length must match matrix column count.")

    names = solver_names or [f"solver{i + 1}_" for i in range(solver_count)]

    columns: dict[str, list[Any]] = {}
    for index, solver_name in enumerate(names):
        columns[f"{solver_name}metric"] = arr[:, index].tolist()

    return parse_dataframe(pd.DataFrame(columns), metric_suffix="metric", output_suffix="output")


def _is_sequence_like(value: Any) -> bool:
    return isinstance(value, (list, tuple, np.ndarray, pd.Series))


def _normalize_tabular_dict(data: dict[str, Any]) -> pd.DataFrame | None:
    if not data:
        return None
    if not all(_is_sequence_like(v) for v in data.values()):
        return None

    lengths = {len(v) for v in data.values()}
    if len(lengths) != 1:
        return None

    return pd.DataFrame({k: list(v) for k, v in data.items()})


def _normalize_nested_solver_dict(data: dict[str, Any]) -> dict[str, list[Any]] | None:
    if not data:
        return None

    if "solvers" in data and isinstance(data["solvers"], dict):
        solver_blob = data["solvers"]
    else:
        solver_blob = data

    if not isinstance(solver_blob, dict):
        return None

    result: dict[str, list[Any]] = {}
    for solver_name, payload in solver_blob.items():
        if not isinstance(payload, dict):
            return None

        metric_values = payload.get("metric") or payload.get("metrics")
        output_values = payload.get("output") or payload.get("outputs")
        if metric_values is None or not _is_sequence_like(metric_values):
            return None

        result[f"{solver_name}metric"] = list(metric_values)
        if output_values is not None:
            if not _is_sequence_like(output_values):
                return None
            result[f"{solver_name}output"] = list(output_values)

    lengths = {len(v) for v in result.values()}
    if len(lengths) != 1:
        return None

    return result


def parse_dict(
    data: dict[str, Any],
    metric_suffix: str = "metric",
    output_suffix: str = "output",
) -> ParsedDataset:
    tabular = _normalize_tabular_dict(data)
    if tabular is not None:
        return parse_dataframe(tabular, metric_suffix=metric_suffix, output_suffix=output_suffix)

    nested = _normalize_nested_solver_dict(data)
    if nested is not None:
        return parse_dataframe(pd.DataFrame(nested), metric_suffix=metric_suffix, output_suffix=output_suffix)

    raise ValueError("Dictionary input must be either tabular (column->sequence) or nested (solver->{metric,output}).")


def parse_csv_file(
    file_path: str | Path,
    metric_suffix: str = "metric",
    output_suffix: str = "output",
) -> ParsedDataset:
    df = pd.read_csv(file_path, dtype=object)
    return parse_dataframe(df, metric_suffix=metric_suffix, output_suffix=output_suffix)


def _mat_to_dict(blob: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in blob.items():
        if key.startswith("__"):
            continue
        result[key] = value
    return result


def parse_mat_file(
    file_path: str | Path,
    metric_suffix: str = "metric",
    output_suffix: str = "output",
) -> ParsedDataset:
    content = loadmat(file_path, simplify_cells=True)
    usable = _mat_to_dict(content)

    tabular = _normalize_tabular_dict(usable)
    if tabular is not None:
        return parse_dataframe(tabular, metric_suffix=metric_suffix, output_suffix=output_suffix)

    for key in ("table", "data", "dataset"):
        value = usable.get(key)
        if isinstance(value, dict):
            nested_tabular = _normalize_tabular_dict(value)
            if nested_tabular is not None:
                return parse_dataframe(nested_tabular, metric_suffix=metric_suffix, output_suffix=output_suffix)
            nested_solver = _normalize_nested_solver_dict(value)
            if nested_solver is not None:
                return parse_dataframe(
                    pd.DataFrame(nested_solver),
                    metric_suffix=metric_suffix,
                    output_suffix=output_suffix,
                )

    nested_solver = _normalize_nested_solver_dict(usable)
    if nested_solver is not None:
        return parse_dataframe(pd.DataFrame(nested_solver), metric_suffix=metric_suffix, output_suffix=output_suffix)

    raise ValueError("Unsupported MAT layout. Expected tabular columns or nested solver data.")


def _read_h5_node(node: h5py.Dataset | h5py.Group) -> Any:
    if isinstance(node, h5py.Dataset):
        value = node[()]
        if isinstance(value, bytes):
            return value.decode("utf-8")
        if isinstance(value, np.ndarray) and value.dtype.kind in {"S", "O"}:
            return [x.decode("utf-8") if isinstance(x, (bytes, bytearray)) else x for x in value]
        if isinstance(value, np.ndarray):
            return value.tolist()
        return value

    result: dict[str, Any] = {}
    for key, child in node.items():
        result[key] = _read_h5_node(child)
    return result


def parse_h5_file(
    file_path: str | Path,
    metric_suffix: str = "metric",
    output_suffix: str = "output",
) -> ParsedDataset:
    with h5py.File(file_path, "r") as handle:
        content = {key: _read_h5_node(node) for key, node in handle.items()}

    tabular = _normalize_tabular_dict(content)
    if tabular is not None:
        return parse_dataframe(tabular, metric_suffix=metric_suffix, output_suffix=output_suffix)

    for key in ("table", "data", "dataset"):
        value = content.get(key)
        if isinstance(value, dict):
            nested_tabular = _normalize_tabular_dict(value)
            if nested_tabular is not None:
                return parse_dataframe(nested_tabular, metric_suffix=metric_suffix, output_suffix=output_suffix)
            nested_solver = _normalize_nested_solver_dict(value)
            if nested_solver is not None:
                return parse_dataframe(
                    pd.DataFrame(nested_solver),
                    metric_suffix=metric_suffix,
                    output_suffix=output_suffix,
                )

    nested_solver = _normalize_nested_solver_dict(content)
    if nested_solver is not None:
        return parse_dataframe(pd.DataFrame(nested_solver), metric_suffix=metric_suffix, output_suffix=output_suffix)

    raise ValueError("Unsupported H5 layout. Expected tabular columns or nested solver data.")


def parse_input_data(
    data: pd.DataFrame | np.ndarray | dict[str, Any],
    metric_suffix: str = "metric",
    output_suffix: str = "output",
    solver_names: list[str] | None = None,
) -> ParsedDataset:
    if isinstance(data, pd.DataFrame):
        return parse_dataframe(data, metric_suffix=metric_suffix, output_suffix=output_suffix)
    if isinstance(data, np.ndarray):
        return parse_ndarray(data, solver_names=solver_names)
    if isinstance(data, dict):
        return parse_dict(data, metric_suffix=metric_suffix, output_suffix=output_suffix)

    raise TypeError("Unsupported in-memory input type. Use DataFrame, ndarray, or dict.")


def parse_input_file(
    file_path: str | Path,
    metric_suffix: str = "metric",
    output_suffix: str = "output",
) -> ParsedDataset:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return parse_csv_file(path, metric_suffix=metric_suffix, output_suffix=output_suffix)
    if suffix == ".mat":
        return parse_mat_file(path, metric_suffix=metric_suffix, output_suffix=output_suffix)
    if suffix in {".h5", ".hdf5"}:
        return parse_h5_file(path, metric_suffix=metric_suffix, output_suffix=output_suffix)

    raise ValueError("Unsupported file type. Expected .csv, .mat, .h5, or .hdf5")
