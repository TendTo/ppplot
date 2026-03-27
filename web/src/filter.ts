import { FilterConfig, RawRecord, SolverSpec } from "./types";

export function normalizeOutput(value: string): string {
  return value.trim().toLowerCase();
}

export function applyOutputFilter(
  rows: RawRecord[],
  solverSpecs: SolverSpec[],
  { allowedOutputs }: FilterConfig,
): RawRecord[] {
  if (allowedOutputs.size === 0) return rows;

  const filteredRows = rows.map((row) => {
    const next: RawRecord = {
      metrics: new Map(row.metrics),
      outputs: new Map(row.outputs),
    };

    for (const spec of solverSpecs) {
      if (!spec.outputHeader) continue;
      const output = row.outputs.get(spec.solverName) ?? null;
      if (output === null) continue;
      if (!allowedOutputs.has(normalizeOutput(output))) {
        next.metrics.set(spec.solverName, null);
      }
    }

    return next;
  });

  return filteredRows;
}
