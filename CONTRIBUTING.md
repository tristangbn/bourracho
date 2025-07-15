# Contributing guidelines

Welcome dear bourracho contributor !

## Dependency manager

This project uses [uv](https://docs.astral.sh/uv/) as a dependency manager. To install requirements run :

```bash
uv sync
```

To add a dependency simply run 

```bash
uv add <dependency>
```

## Formatting and linting

This project rely on [ruff](https://docs.astral.sh/ruff/) to format and lint code base.

To format code simply run :

```bash
uv run ruff format .
```

For linting run

```bash
uv run ruff check .
```

## Tests

To run tests run :

```bash
uv run pytest .
```

To run API tests run 

```bash
uv run manage.py test
```
