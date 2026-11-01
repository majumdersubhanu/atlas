# Development and GitHub handoff

## Environment

Use uv for all Python dependency changes and commands. The default environment
includes the package, tests, lint tools, and notebooks:

```bash
uv sync --locked
uv run --locked pytest -q
uv run --locked ruff check src tests scripts
uv run --locked ruff format --check src tests scripts
```

Add runtime dependencies with `uv add PACKAGE`, development tools with
`uv add --group dev PACKAGE`, and notebook tools with
`uv add --group notebook PACKAGE`. Commit `pyproject.toml` and `uv.lock` together.
Do not commit `.venv` or maintain a parallel requirements/pip environment. Optional
browser tooling has its own npm lockfile; see `browser-tests/README.md`.

## Changes and evidence

Start with [the codebase index](docs/CODEBASE_INDEX.md). Keep observed financials
and synthetic exposures distinct, document monetary units, and preserve input
provenance. Changes to model behavior need independent numerical controls or
boundary tests. Formatting-only changes do not establish new scientific results.
Do not edit frozen raw inputs as part of routine cleanup.

Use `uv run --locked ruff format src tests scripts` to format Python. GitHub Actions
runs lint, format, tests, input checksums, fresh notebook execution, CLI smoke
checks, and package build. Browser QA remains a separate optional workflow.

Reference experiment JSON records retain the hashes of the source used to produce
them. Older verification documents are historical evidence, not a claim that their
hashes identify the latest source. Record new checks in `docs/VERIFICATION.md`.

## Package build

```bash
uv build --no-sources
```

The wheel includes `src/atlas` and its packaged fixtures. The source distribution
includes source, tests, scripts, docs, notebooks, frozen/processed data, and uv
configuration; it excludes local environments and archived releases.

## Upload this repository to GitHub

The checkout has not been pushed by this cleanup. Create an empty GitHub repository
in your account. Then, from this project directory:

```bash
git status --short
git add .
git diff --cached --stat
git commit -m "Prepare Atlas research milestone for academic review"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

If starting from the review ZIP rather than this Git checkout, run `git init` first.
Replace the example URL with your repository URL. `.gitignore` excludes runtime
tokens/logs, environments, downloaded tools, caches, assistant scratch folders,
and archived release copies. The upload commands intentionally leave the commit
and destination under your control. Share the repository README as the professor's
entry point; notebook 03 has saved outputs readable on GitHub.

## Licensing and data

No code license is selected. Academic review access and an open-source license are
separate decisions. See `THIRD_PARTY_NOTICES.md` for the existing market-data
restrictions and provenance. A future code license must not purport to relicense
third-party data or dependencies.
