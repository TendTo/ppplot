export type MetricDirection = "minimize" | "maximize";
export type XScale = "linear" | "log";

export interface ParsedDataset {
  headers: string[];
  rows: RawRecord[];
  solverSpecs: SolverSpec[];
}

export interface RawRecord {
  metrics: Map<string, number | null>;
  outputs: Map<string, string | null>;
}

export interface SolverSpec {
  solverName: string;
  metricHeader: string;
  outputHeader: string | null;
}

export interface ParseConfig {
  metricSuffix: string;
  outputSuffix: string;
}

export interface FilterConfig {
  allowedOutputs: Set<string>;
}

export interface SolverStyle {
  id: number;
  solverName: string;
  label: string;
  color: string;
  lineStyle: "solid" | "dash" | "dot" | "longdash" | "dashdot" | "longdashdot";
}

export interface PlotOptions {
  title: string;
  xLabel: string;
  yLabel: string;
  xScale: XScale;
  tauMax: number;
  tauSamples: number;
  direction: MetricDirection;
}

export interface ProfileCurve {
  solverName: string;
  tau: number[];
  rho: number[];
}

export interface ProfileResult {
  curves: ProfileCurve[];
  rows: number;
}

export interface TemplateDefinition {
  id: string;
  name: string;
  chartStyle: {
    background: string;
    gridColor: string;
    textColor: string;
  };
  palette: string[];
}
