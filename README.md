# <img alt="Icon" src="docs/_static/logo.svg" align="left" width="35" height="35"> ppplot

[![ppplot CI](https://img.shields.io/badge/github-Web_app-blue?logo=github)](https://tendto.github.io/ppplot)
[![ppplot CI](https://github.com/TendTo/ppplot/actions/workflows/page.yml/badge.svg)](https://github.com/TendTo/ppplot/actions/workflows/page.yml)

ppplot is a Python package and web app for generating performance profiles, as defined in [_Benchmarking optimization software with performance profiles_](https://doi.org/10.1007/s101070100263) by Elizabeth D. Dolan & Jorge J. Moré.

## Performance Profile Definition

For each problem $p$ and solver $s$, we define

$$
t_{p,s} = \text{metric obtained by solver } s \text{ on problem } p
$$

We compare the performance of solver $s$ on problem $p$ with the best performance achieved by any solver on that same problem. That is, we use the performance ratio

$$
r_{p,s} = \frac{t_{p,s}}{\min_s t_{p,s}}
$$

If the solver fails to solve the problem, we set $t_{p,s}=+\infty$ and thus $r_{p,s}=+\infty$.

To evaluate the overall performance of solver $s$, we compute

$$
\rho_s(\tau)=\frac{1}{|n_p|}\left\vert\left\lbrace p\in P: r_{p,s}\le\tau\right\rbrace\right\vert
$$

where $P$ is the set of all problems, $n_p$ is the total number of problems, and $\tau\ge 1$ is the performance factor.

## Web App

This repository includes a web page to generate performance profile plots from CSV files.
A live demo is available at [https://tendto.github.io/ppplot/](https://tendto.github.io/ppplot/).

### Run

```bash
pnpm install
pnpm web:dev
```

The dev server starts on [http://localhost:5173](http://localhost:5173).

Production build:

```bash
pnpm web:build
pnpm web:preview
```

### Expected CSV Format

The app expects one row per problem instance.

- `<solverName><metricSuffix>`: solver metric value. Empty, `NaN`, or `null` are treated as missing.
- `<solverName><outputSuffix>` (optional): solver output/status text used for filtering.

For example, assuming the suffixes `_metric` and `_output` are used for metric and output columns respectively, a CSV file such as the one below

| instance | solverA_metric | solverA_output | solverB_metric | solverB_output |
| -------- | -------------- | -------------- | -------------- | -------------- |
| inst1    | 1.2            | success        | 0.8            | success        |
| inst2    | 2.5            | timeout        | 2.0            | success        |
| inst3    |                |                | 1.5            | success        |
| inst4    | 0.5            | success        | NaN            | success        |

`solverA`'s metric will be set to $+\infty$ for `inst2` (timeout) and `inst3` (missing), while `solverB`'s metric will be set to $+\infty$ for `inst4` (NaN).

### MathJax in Plotly

The app loads MathJax, which allows you to use TeX expressions in Plotly labels and titles, following the usual Markdown math syntax:

- `$d^t_{qs,100}$`
- `$\rho_s(\tau)$`
- `$r_{p,s}$`

> [!NOTE]  
> Due to a [bug in Plotly](https://github.com/plotly/plotly.js/issues/559), math text does not render in hover labels.

## Alternatives

Alternatives with similar functionality to ppplot include:

- [perfprof.py](https://github.com/dmsteck/perfprof.py)
- [performance-profiles-in-python](https://github.com/Jvanschoubroeck/performance-profiles-in-python)
- [perfprof.m](https://github.com/higham/matlab-guide-3ed/blob/master/perfprof.m)
- [perprof-py](https://github.com/abelsiqueira/perprof-py)
- [BenchmarkProfiles.jl](https://github.com/JuliaSmoothOptimizers/BenchmarkProfiles.jl)

## Acknowledgment

If you use ppplot in your research, please consider acknowledging it, adding a link to the repository as a footnote, or citing it in the bibliography (see the _Cite this repository_ section).
This helps more people discover ppplot and performance profiles, use them in their research, and possibly contribute to improving the tool.
