import Plotly from "plotly.js-basic-dist-min";
import { ProfileResult, SolverStyle, TemplateDefinition, XScale } from "./types";

const lineStyleMap: Record<SolverStyle["lineStyle"], string> = {
  solid: "solid",
  dash: "dash",
  dot: "dot",
  longdash: "longdash",
  dashdot: "dashdot",
  longdashdot: "longdashdot",
};

export function clearPlot(target: HTMLElement) {
  Plotly.purge(target);
}

export function renderProfilePlot(params: {
  target: HTMLElement;
  profile: ProfileResult;
  styles: SolverStyle[];
  title: string;
  xLabel: string;
  yLabel: string;
  xScale: XScale;
  template: TemplateDefinition;
}) {
  const styleMap = new Map(
    params.styles.map((style) => [style.solverName, style]),
  );

  const traces = params.profile.curves.map((curve) => {
    const style = styleMap.get(curve.solverName);
    return {
      type: "scatter",
      mode: "lines",
      x: curve.tau,
      y: curve.rho,
      name: style?.label ?? curve.solverName,
      line: {
        color: style?.color ?? "#2563eb",
        width: 2.5,
        dash: style ? lineStyleMap[style.lineStyle] : "solid",
      },
      hovertemplate: "<extra>%{fullData.name}</extra>%{y:.3f}",
    };
  });

  const template = params.template;

  return Plotly.react(
    params.target,
    traces,
    {
      title: {
        text: params.title,
        font: {
          size: 22,
          color: template.chartStyle.textColor,
          family: "Space Grotesk, sans-serif",
        },
      },
      paper_bgcolor: template.chartStyle.background,
      plot_bgcolor: template.chartStyle.background,
      font: {
        color: template.chartStyle.textColor,
        family: "IBM Plex Mono, monospace",
      },
      xaxis: {
        type: params.xScale,
        title: {
          text: params.xLabel,
        },
        gridcolor: template.chartStyle.gridColor,
        zeroline: false,
        unifiedhovertitle: {
          text: "<b>Tau: %{x:.3f}</b>",
        },
      },
      yaxis: {
        title: {
          text: params.yLabel,
        },
        range: [-0.01, 1.01],
        gridcolor: template.chartStyle.gridColor,
        zeroline: false,
      },
      margin: { l: 64, r: 28, t: 64, b: 62 },
      legend: {
        orientation: "h",
        y: 1.12,
      },
      hovermode: "x unified",
      autosize: true,
    },
    {
      displaylogo: false,
      responsive: true,
      modeBarButtonsToRemove: ["lasso2d", "select2d"],
    },
  );
}
