# CVcompiler

Compile your Markdown resume/CV to a beautiful single-page website.

[Here is an example](https://vanolucas.com/).

## Run

1. Edit your resume in [cv.md](cv.md) and put your image assets in [img/](img/).

2. Run the website generator:

    ```sh
    uv run cvcompiler
    ```

3. Follow instructions to select your themes.

4. `index.html` gets generated.

5. Host your single-page CV website wherever you like (`index.html` + `img/` directory).

## Edit colors

You can create and use your own themes by placing them in [themes/](themes/).

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
