import "./styles.css";
import { parseCsvFile } from "./csv";
import { applyOutputFilter, normalizeOutput } from "./filter";
import { ensureMathJax } from "./mathjax";
import { clearPlot, renderProfilePlot } from "./plot";
import { computePerformanceProfiles, isValidMetric } from "./profile";
import { getTemplateById, templates } from "./templates";
import {
  MetricDirection,
  ParsedDataset,
  PlotOptions,
  SolverStyle,
  TemplateDefinition,
  XScale,
} from "./types";

type InputElements = {
  csvFile: HTMLInputElement;
  clearFileButton: HTMLButtonElement;
  metricSuffix: HTMLInputElement;
  outputSuffix: HTMLInputElement;
  allowedOutputs: HTMLInputElement;
  //   metricDirection: HTMLSelectElement;
  plotTitle: HTMLInputElement;
  xLabel: HTMLInputElement;
  yLabel: HTMLInputElement;
  xScaleLog: HTMLInputElement;
  tauMax: HTMLInputElement;
  tauPoints: HTMLInputElement;
  templateSelect: HTMLSelectElement;
  solverStyleRows: HTMLDivElement;
  plotButton: HTMLButtonElement;
  resetButton: HTMLButtonElement;
  status: HTMLParagraphElement;
  tablePreview: HTMLDivElement;
  plotTarget: HTMLDivElement;
};

const DEFAULTS = {
  metricSuffix: "metric",
  outputSuffix: "output",
  allowedOutputs: "ok,success,optimal",
  metricDirection: "minimize" as MetricDirection,
  plotTitle: "Performance Profile",
  xLabel: "Performance ratio (tau)",
  yLabel: "Percentage of problems solved",
  xScale: "linear" as XScale,
  tauMax: 5,
  tauPoints: 150,
  template: "minimal",
};

let dataset: ParsedDataset | null = null;
let solverStyles: SolverStyle[] = [];
let mathJaxReady = false;

const ui = getInputElements();
initializeTemplates();
wireEvents();

function getInputElements(): InputElements {
  function getById<T extends HTMLElement>(id: string): T {
    const node = document.getElementById(id);
    if (!node) throw new Error(`Expected element #${id} not found.`);
    return node as T;
  }

  return {
    csvFile: getById<HTMLInputElement>("csvFile"),
    clearFileButton: getById<HTMLButtonElement>("clearFileButton"),
    metricSuffix: getById<HTMLInputElement>("metricSuffix"),
    outputSuffix: getById<HTMLInputElement>("outputSuffix"),
    allowedOutputs: getById<HTMLInputElement>("allowedOutputs"),
    // metricDirection: getById<HTMLSelectElement>("metricDirection"),
    plotTitle: getById<HTMLInputElement>("plotTitle"),
    xLabel: getById<HTMLInputElement>("xLabel"),
    yLabel: getById<HTMLInputElement>("yLabel"),
    xScaleLog: getById<HTMLInputElement>("xScaleLog"),
    tauMax: getById<HTMLInputElement>("tauMax"),
    tauPoints: getById<HTMLInputElement>("tauPoints"),
    templateSelect: getById<HTMLSelectElement>("templateSelect"),
    solverStyleRows: getById<HTMLDivElement>("solverStyleRows"),
    plotButton: getById<HTMLButtonElement>("plotButton"),
    resetButton: getById<HTMLButtonElement>("resetButton"),
    status: getById<HTMLParagraphElement>("status"),
    tablePreview: getById<HTMLDivElement>("tablePreview"),
    plotTarget: getById<HTMLDivElement>("plot"),
  };
}

function initializeTemplates() {
  ui.templateSelect.innerHTML = "";
  for (const template of templates) {
    const option = document.createElement("option");
    option.value = template.id;
    option.textContent = template.name;
    if (template.id === DEFAULTS.template) {
      option.selected = true;
    }
    ui.templateSelect.appendChild(option);
  }
}

function wireEvents() {
  ui.csvFile.addEventListener("change", async () => {
    const file = ui.csvFile.files?.[0];
    if (!file) return;

    setStatus("Parsing CSV file...", "info");
    try {
      dataset = await parseCsvFile(file, {
        metricSuffix: ui.metricSuffix.value.trim(),
        outputSuffix: ui.outputSuffix.value.trim(),
      });
      solverStyles = buildDefaultSolverStyles(
        dataset.solverSpecs.map((x) => x.solverName),
      );
      applyTemplatePalette(getTemplateById(ui.templateSelect.value));
      renderSolverStyleControls();
      renderPreviewTable(parseAllowedOutputs());
      setStatus(
        `Parsed ${dataset.rows.length} rows and detected ${dataset.solverSpecs.length} solvers.`,
        "success",
      );
      void renderCurrentPlot();
    } catch (error) {
      dataset = null;
      solverStyles = [];
      renderSolverStyleControls();
      renderPreviewTable();
      setStatus((error as Error).message, "error");
    }
  });

  ui.plotButton.addEventListener("click", () => {
    void renderCurrentPlot();
  });

  ui.clearFileButton.addEventListener("click", () => {
    ui.csvFile.value = "";
    dataset = null;
    solverStyles = [];
    renderSolverStyleControls();
    renderPreviewTable();
    clearPlot(ui.plotTarget);
    ui.plotTarget.innerHTML = "";
    setStatus("File cleared. Upload a CSV file to continue.", "info");
  });

  ui.resetButton.addEventListener("click", () => {
    resetSettings();
    if (dataset) {
      solverStyles = buildDefaultSolverStyles(
        dataset.solverSpecs.map((x) => x.solverName),
      );
      applyTemplatePalette(getTemplateById(ui.templateSelect.value));
      renderSolverStyleControls();
      void renderCurrentPlot();
      setStatus("Settings reset to defaults.", "info");
    } else {
      setStatus("Settings reset. Upload a CSV file to continue.", "info");
    }
  });

  ui.templateSelect.addEventListener("change", () => {
    const template = getTemplateById(ui.templateSelect.value);
    applyTemplatePalette(template);
    renderSolverStyleControls();
    if (dataset) {
      void renderCurrentPlot();
    }
  });

  ui.xScaleLog.addEventListener("change", () => {
    if (dataset) {
      void renderCurrentPlot();
    }
  });

  const plotControlInputs = [
    ui.plotTitle,
    ui.xLabel,
    ui.yLabel,
    ui.tauMax,
    ui.tauPoints,
    ui.allowedOutputs,
  ];

  plotControlInputs.forEach((input) => {
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        void renderCurrentPlot();
      }
    });
  });
}

function resetSettings() {
  ui.metricSuffix.value = DEFAULTS.metricSuffix;
  ui.outputSuffix.value = DEFAULTS.outputSuffix;
  ui.allowedOutputs.value = DEFAULTS.allowedOutputs;
  //   ui.metricDirection.value = DEFAULTS.metricDirection;
  ui.plotTitle.value = DEFAULTS.plotTitle;
  ui.xLabel.value = DEFAULTS.xLabel;
  ui.yLabel.value = DEFAULTS.yLabel;
  ui.xScaleLog.checked = DEFAULTS.xScale === "log";
  ui.tauMax.value = String(DEFAULTS.tauMax);
  ui.tauPoints.value = String(DEFAULTS.tauPoints);
  ui.templateSelect.value = DEFAULTS.template;
}

function buildDefaultSolverStyles(solverNames: string[]): SolverStyle[] {
  const template = getTemplateById(ui.templateSelect.value);

  return solverNames.map((solverName, index) => ({
    id: index,
    solverName,
    label: solverName,
    color: template.palette[index % template.palette.length],
    lineStyle: "solid",
  }));
}

function applyTemplatePalette(template: TemplateDefinition) {
  solverStyles = solverStyles.map((style, index) => ({
    ...style,
    color: template.palette[index % template.palette.length],
  }));
}

function renderSolverStyleControls() {
  ui.solverStyleRows.innerHTML = "";

  if (solverStyles.length === 0) {
    const p = document.createElement("p");
    p.className = "help";
    p.textContent = "Solver style controls appear after CSV parsing.";
    ui.solverStyleRows.appendChild(p);
    return;
  }

  solverStyles.forEach((style, index) => {
    const row = document.createElement("div");
    row.className = "solver-style-row";

    const name = document.createElement("code");
    name.textContent = `Solver ${style.id + 1}`;

    const label = document.createElement("input");
    label.type = "text";
    label.value = style.label;
    label.title = "Display label";
    label.name = `label-${style.id}`;
    label.addEventListener("change", () => {
      solverStyles[index].label = label.value.trim() || style.solverName;
      void renderCurrentPlot();
    });

    const color = document.createElement("input");
    color.type = "color";
    color.title = "Line color";
    color.value = style.color;
    color.name = `color-${style.id}`;
    color.addEventListener("change", () => {
      solverStyles[index].color = color.value;
      void renderCurrentPlot();
    });

    const lineStyle = document.createElement("select");
    lineStyle.title = "Line style";
    lineStyle.name = `line-style-${style.id}`;
    ["solid", "dash", "dot", "longdash", "dashdot", "longdashdot"].forEach((line) => {
      const option = document.createElement("option");
      option.value = line;
      option.textContent = line;
      option.selected = line === style.lineStyle;
      lineStyle.appendChild(option);
    });
    lineStyle.addEventListener("change", () => {
      solverStyles[index].lineStyle =
        lineStyle.value as SolverStyle["lineStyle"];
      void renderCurrentPlot();
    });

    row.append(name, label, color, lineStyle);
    ui.solverStyleRows.appendChild(row);
  });
}

function insertCharBeforeSuffix(str: string, suffix: string, char: string) {
  return (
    str.substring(0, str.length - suffix.length) +
    char +
    str.substring(str.length - suffix.length)
  );
}

function renderPreviewTable(allowedOutputs: Set<string> = new Set()) {
  ui.tablePreview.innerHTML = "";

  if (!dataset || dataset.rows.length === 0) return;

  const table = document.createElement("table");
  const head = document.createElement("thead");
  const headRow = document.createElement("tr");

  const columns = [
    ...dataset.solverSpecs.map((spec) =>
      insertCharBeforeSuffix(spec.metricHeader, "metric", " "),
    ),
  ];

  for (const column of columns) {
    const th = document.createElement("th");
    th.textContent = column;
    headRow.appendChild(th);
  }
  head.appendChild(headRow);

  const body = document.createElement("tbody");
  for (const row of dataset.rows.slice(0, 10)) {
    const tr = document.createElement("tr");

    for (const spec of dataset.solverSpecs) {
      const metricTd = document.createElement("td");
      const metric = row.metrics.get(spec.solverName) ?? null;
      metricTd.className = isValidMetric(metric) ? "valid" : "invalid";
      if (
        spec.outputHeader &&
        !allowedOutputs.has(
          normalizeOutput(row.outputs.get(spec.solverName) ?? ""),
        )
      ) {
        metricTd.className = "invalid";
      }
      metricTd.title = metricTd.ariaLabel =
        metricTd.className === "invalid"
          ? "Invalid or missing metric"
          : "Valid metric";
      metricTd.textContent = String(metric ?? "/");
      tr.appendChild(metricTd);
    }

    body.appendChild(tr);
  }

  table.append(head, body);
  ui.tablePreview.appendChild(table);
}

function getPlotOptions(): PlotOptions {
  return {
    title: ui.plotTitle.value.trim(),
    xLabel: ui.xLabel.value.trim(),
    yLabel: ui.yLabel.value.trim(),
    xScale: ui.xScaleLog.checked ? "log" : "linear",
    tauMax: Number(ui.tauMax.value) || DEFAULTS.tauMax,
    tauSamples: Number(ui.tauPoints.value) || DEFAULTS.tauPoints,
    direction: DEFAULTS.metricDirection, // ui.metricDirection.value as MetricDirection,
  };
}

function parseAllowedOutputs(): Set<string> {
  return new Set(
    ui.allowedOutputs.value
      .split(",")
      .map((value) => value.trim().toLowerCase())
      .filter((value) => value.length > 0),
  );
}

async function renderCurrentPlot() {
  if (!dataset) {
    setStatus("Upload and parse a CSV file before plotting.", "error");
    return;
  }

  if (!mathJaxReady) {
    setStatus("Loading MathJax...", "info");
  }
  try {
    await ensureMathJax();
    mathJaxReady = true;
  } catch (error) {
    setStatus((error as Error).message, "error");
    return;
  }

  const options = getPlotOptions();

  const filteredRows = applyOutputFilter(dataset.rows, dataset.solverSpecs, {
    allowedOutputs: parseAllowedOutputs(),
  });

  const profile = computePerformanceProfiles({
    rows: filteredRows,
    solverSpecs: dataset.solverSpecs,
    direction: options.direction,
    tauMax: options.tauMax,
    tauSamples: options.tauSamples,
  });

  renderProfilePlot({
    target: ui.plotTarget,
    profile,
    styles: solverStyles,
    title: options.title,
    xLabel: options.xLabel,
    yLabel: options.yLabel,
    xScale: options.xScale,
    template: getTemplateById(ui.templateSelect.value),
  });

  setStatus(
    `Collected results for ${profile.curves.length} solvers across ${profile.rows} rows.`,
    "success",
  );
}

function setStatus(message: string, state: "info" | "success" | "error") {
  ui.status.textContent = message;
  ui.status.dataset.state = state;
}
