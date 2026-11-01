# Third-party data and tooling

## Historical market fixture

`src/atlas/data/sp500_2020.csv` contains S&P 500 observations distributed through
FRED. Provider: S&P Dow Jones Indices LLC. The existing provenance record identifies
copyright and reproduction restrictions; attribution alone is not a redistribution
license. See [the exact source, checksum, and provider notes](docs/DATA_PROVENANCE.md).
The fixture, derived displays, and bundled historical archives do not acquire an
open-data license from this repository. Review those terms before public
redistribution. This cleanup does not assert permission or publish the repository.

## FDIC observations

Frozen FDIC API responses and field definitions are identified by source URLs and
SHA-256 in `data/manifest.json`. They are revised historical observations retrieved
on the recorded date. They do not provide bilateral loan exposures. Consult the
FDIC source's usage guidance when redistributing data; retain provenance.

## Dependencies and historical presentation tooling

Python dependencies are declared in `pyproject.toml` and pinned in `uv.lock`;
JavaScript browser tools use `browser-tests/package-lock.json`. Each dependency
retains its own license.

The earlier PowerPoint authoring scripts use a Codex artifact runtime that is not
part of the uv environment. The checked-in PowerPoint is an earlier synthetic
study, not the current observed-data evaluation. See `presentation/README.md`.

No project-wide code license has been selected. No author identity or license grant
has been invented as part of repository preparation.
