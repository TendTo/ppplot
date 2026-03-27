import { TemplateDefinition } from "./types";

export const templates: TemplateDefinition[] = [
  {
    id: "minimal",
    name: "Minimal Slate",
    chartStyle: {
      background: "#f6f8fa",
      gridColor: "#d4dce3",
      textColor: "#1f2933",
    },
    palette: ["#0f766e", "#2563eb", "#ea580c", "#7c3aed", "#be123c", "#0891b2"],
  },
  {
    id: "journal",
    name: "Journal Print",
    chartStyle: {
      background: "#fffaf0",
      gridColor: "#d8ccb4",
      textColor: "#2f241a",
    },
    palette: ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#6d597a"],
  },
  {
    id: "presentation",
    name: "Presentation Contrast",
    chartStyle: {
      background: "#0b1b2b",
      gridColor: "#375a7f",
      textColor: "#f6fbff",
    },
    palette: ["#66d9ef", "#a6e22e", "#fd971f", "#f92672", "#ffd866", "#5bc0eb"],
  },
];

export function getTemplateById(id: string): TemplateDefinition {
  return templates.find((template) => template.id === id) ?? templates[0];
}
