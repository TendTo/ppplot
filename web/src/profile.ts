import {
  MetricDirection,
  ProfileCurve,
  ProfileResult,
  RawRecord,
  SolverSpec,
} from "./types";

function buildTauGrid(maxTau: number, sampleCount: number): number[] {
  const max = Math.max(1, maxTau);
  const samples = Math.max(10, sampleCount);
  const step = (max - 1) / (samples - 1);

  const values: number[] = [];
  for (let i = 0; i < samples; i += 1) {
    values.push(1 + step * i);
  }
  return values;
}

export function isValidMetric(value?: number | null): value is number {
  return value != null && Number.isFinite(value) && value > 0;
}

function computeRatiosForRow(
  row: RawRecord,
  solverSpecs: SolverSpec[],
): Map<string, number> {
  const validValues = solverSpecs
    .map((spec) => row.metrics.get(spec.solverName))
    .filter(isValidMetric);

  const ratios = new Map<string, number>();

  if (validValues.length === 0) {
    for (const spec of solverSpecs) {
      ratios.set(spec.solverName, Number.POSITIVE_INFINITY);
    }
    return ratios;
  }

  const baseline = Math.min(...validValues);

  for (const spec of solverSpecs) {
    const value = row.metrics.get(spec.solverName);
    if (!isValidMetric(value)) {
      ratios.set(spec.solverName, Number.POSITIVE_INFINITY);
      continue;
    }

    ratios.set(spec.solverName, value / baseline);
  }

  return ratios;
}

function buildCurves(
  rows: RawRecord[],
  solverSpecs: SolverSpec[],
  tauValues: number[],
): ProfileCurve[] {
  const ratiosByRow = rows.map((row) => computeRatiosForRow(row, solverSpecs));

  return solverSpecs.map((spec) => {
    const solverName = spec.solverName;
    const rho = tauValues.map((tau) => {
      let count = 0;
      for (const rowRatios of ratiosByRow) {
        if ((rowRatios.get(solverName) ?? Number.POSITIVE_INFINITY) <= tau) {
          count += 1;
        }
      }
      return ratiosByRow.length > 0 ? count / ratiosByRow.length : 0;
    });

    return {
      solverName,
      tau: tauValues,
      rho,
    };
  });
}

export function computePerformanceProfiles(params: {
  rows: RawRecord[];
  solverSpecs: SolverSpec[];
  direction: MetricDirection;
  tauMax: number;
  tauSamples: number;
}): ProfileResult {
  const tau = buildTauGrid(params.tauMax, params.tauSamples);

  return {
    curves: buildCurves(params.rows, params.solverSpecs, tau),
    rows: params.rows.length,
  };
}
