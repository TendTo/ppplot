import Papa from "papaparse";
import { ParseConfig, ParsedDataset, RawRecord, SolverSpec } from "./types";

interface CsvRow {
  [key: string]: string;
}

function normalizeHeaderName(value: string): string {
  return value.trim();
}

function parseMetricCell(cell: string | undefined): number | null {
  if (cell == null) {
    return null;
  }
  const text = cell.trim();
  if (text.length === 0) {
    return null;
  }
  if (text.toLowerCase() === "nan" || text.toLowerCase() === "null") {
    return null;
  }
  const numeric = Number(text);
  if (!Number.isFinite(numeric)) {
    return null;
  }
  return numeric;
}

function parseOutputCell(cell: string | undefined): string | null {
  if (cell == null) {
    return null;
  }
  const text = cell.trim();
  if (text.length === 0) {
    return null;
  }
  return text;
}

function detectSolvers(headers: string[], config: ParseConfig): SolverSpec[] {
  const metricSuffix = config.metricSuffix.trim();
  if (!metricSuffix) throw new Error("Metric suffix cannot be empty.");

  const outputSuffix = config.outputSuffix.trim();
  const normalizedHeaders = headers.map(normalizeHeaderName);

  const metricHeaders = normalizedHeaders.filter((header) =>
    header.endsWith(metricSuffix),
  );

  if (metricHeaders.length === 0) {
    throw new Error(
      `No metric columns found. Expected one or more headers ending with '${metricSuffix}'.`,
    );
  }

  return metricHeaders.map((metricHeader) => {
    const solverName = metricHeader.slice(0, -metricSuffix.length);
    const outputHeaderCandidate = outputSuffix
      ? `${solverName}${outputSuffix}`
      : "";
    const outputHeader = normalizedHeaders.includes(outputHeaderCandidate)
      ? outputHeaderCandidate
      : null;

    return {
      solverName,
      metricHeader,
      outputHeader,
    };
  });
}

function parseRows(
  rows: CsvRow[],
  solverSpecs: SolverSpec[],
  config: ParseConfig,
): RawRecord[] {
  return rows.map(row => {
    const metrics = new Map<string, number | null>();
    const outputs = new Map<string, string | null>();

    for (const spec of solverSpecs) {
      metrics.set(spec.solverName, parseMetricCell(row[spec.metricHeader]));
      outputs.set(
        spec.solverName,
        spec.outputHeader ? parseOutputCell(row[spec.outputHeader]) : null,
      );
    }

    return {
      metrics,
      outputs,
    };
  });
}

export function parseCsvFile(
  file: File,
  config: ParseConfig,
): Promise<ParsedDataset> {
  return new Promise((resolve, reject) => {
    Papa.parse<CsvRow>(file, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: false,
      complete(results: Papa.ParseResult<CsvRow>) {
        const headers = (results.meta.fields ?? []).map(normalizeHeaderName);

        try {
          const solverSpecs = detectSolvers(headers, config);
          const dataRows = results.data;
          const rows = parseRows(dataRows, solverSpecs, config);

          resolve({
            headers,
            rows,
            solverSpecs,
          });
        } catch (error) {
          reject(error);
        }
      },
      error(error: Error) {
        reject(error);
      },
    });
  });
}
