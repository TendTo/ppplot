from __future__ import annotations

from typing import Iterable, Set

from .types import RawRecord, SolverSpec


def normalize_output(value: str) -> str:
    return value.strip().lower()


def parse_allowed_outputs(values: Iterable[str] | None) -> Set[str]:
    if values is None:
        return set()
    return {normalize_output(part) for part in values if part.strip()}


def apply_output_filter(
    rows: list[RawRecord],
    solver_specs: list[SolverSpec],
    allowed_outputs: Set[str],
) -> list[RawRecord]:
    if not allowed_outputs:
        return rows

    filtered_rows: list[RawRecord] = []
    for row in rows:
        next_metrics = dict(row.metrics)
        next_outputs = dict(row.outputs)
        for spec in solver_specs:
            if not spec.output_header:
                continue
            output = row.outputs.get(spec.solver_name)
            if output is None:
                continue
            if normalize_output(output) not in allowed_outputs:
                next_metrics[spec.solver_name] = None
        filtered_rows.append(RawRecord(metrics=next_metrics, outputs=next_outputs))

    return filtered_rows
