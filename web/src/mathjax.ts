declare global {
  interface Window {
    MathJax?: unknown;
    PlotlyConfig?: {
      MathJaxConfig?: "local" | "cdn";
    };
  }
}

let loadingPromise: Promise<void> | null = null;

function hasMathJax(): boolean {
  return typeof window !== "undefined" && window.MathJax != null;
}

export async function ensureMathJax(): Promise<void> {
  if (hasMathJax()) {
    return;
  }

  if (loadingPromise) {
    return loadingPromise;
  }

  loadingPromise = (async () => {
    window.PlotlyConfig = {
      ...(window.PlotlyConfig ?? {}),
      MathJaxConfig: "local",
    };

    await import("mathjax/es5/tex-svg.js");
  })();

  try {
    await loadingPromise;
  } catch {
    throw new Error("Failed to load MathJax from npm bundle.");
  } finally {
    if (!hasMathJax()) {
      loadingPromise = null;
    }
  }
}
