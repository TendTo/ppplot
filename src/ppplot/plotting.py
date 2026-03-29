from __future__ import annotations

from .types import ProfileResult, XScale


def render_with_matplotlib(
    profile: ProfileResult,
    title: str,
    x_label: str,
    y_label: str,
    x_scale: XScale,
    solver_labels: dict[str, str] | None = None,
):
    import matplotlib.pyplot as plt

    solver_labels = solver_labels or {}
    fig, ax = plt.subplots(figsize=(8.5, 5.2))

    for curve in profile.curves:
        ax.plot(
            curve.tau,
            curve.rho,
            label=solver_labels.get(curve.solver_name, curve.solver_name),
            linewidth=2.0,
        )

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xscale(x_scale)
    ax.set_ylim(-0.01, 1.01)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def render_with_plotly(
    profile: ProfileResult,
    title: str,
    x_label: str,
    y_label: str,
    x_scale: XScale,
    solver_labels: dict[str, str] | None = None,
):
    import plotly.graph_objects as go

    solver_labels = solver_labels or {}
    fig = go.Figure()
    for curve in profile.curves:
        fig.add_trace(
            go.Scatter(
                x=curve.tau,
                y=curve.rho,
                mode="lines",
                name=solver_labels.get(curve.solver_name, curve.solver_name),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.08},
    )
    fig.update_xaxes(type=x_scale)
    fig.update_yaxes(range=[-0.01, 1.01])
    return fig


def render_profile(
    backend: str,
    profile: ProfileResult,
    title: str,
    x_label: str,
    y_label: str,
    x_scale: XScale,
    solver_labels: dict[str, str] | None = None,
):
    render_fun = {
        "matplotlib": render_with_matplotlib,
        "plotly": render_with_plotly,
    }.get(backend)
    if not render_fun:
        raise ValueError("Unsupported backend. Use 'matplotlib' or 'plotly'.")
    return render_fun(
        profile,
        title=title,
        x_label=x_label,
        y_label=y_label,
        x_scale=x_scale,
        solver_labels=solver_labels,
    )
