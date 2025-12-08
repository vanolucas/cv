# CVcompiler

Compile your Markdown CV to a beautiful single-page website.

## Run

```sh
uv run --env-file .env cvcompiler
```

## Contribute

### Setup Python venv

```sh
uv sync --all-packages
```

### Lint code

```sh
uvx pre-commit run --all-files
```

### Upgrade pre-commit hooks

```sh
uvx pre-commit autoupdate
```
