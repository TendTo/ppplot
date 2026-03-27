# Contributing

## Folder structure

```bash
.
├── docs   # Documentation files
│   └── Contributing.md
├── src    # Source code
│   └── ppplot
│       └── __init__.py
├── tests  # Test files
│   ├── unit
│   │   └── test_ppplot.py
│   └── integration
│       └── test_integration.py
├── pyproject.toml  # Project configuration file
├── LICENSE         # License file
└── README.md       # README file
```

## Dev dependencies

To install the development dependencies, use the following command:

```bash
pip install -e .[dev]
```

### Testing

To run the tests, use the following command:

```bash
pytest tests
```

or, with uv:

```bash
uv run pytest
```

### Linting and formatting

To run the linters and formatters, use the following command:

```bash
ruff check
ruff format
```

or, with uv:

```bash
uv run ruff check
uv run ruff format
```

### Documentation

To build the documentation, use the following command:

```bash
uv run sphinx-build -M html docs docs/_build
```
