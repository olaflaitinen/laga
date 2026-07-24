# Contributing

## Setup

1. Create and activate a virtual environment.
2. Install development dependencies with `python -m pip install -e ".[dev]"`.
3. Install pre-commit hooks with `pre-commit install`.

## Local Checks

Run the full check set before sending a change:

```bash
make lint
make typecheck
make test
make build
```

## Pull Requests

1. Keep changes focused and easy to review.
2. Add or update tests for behavior changes.
3. Update documentation when the public API changes.
4. Include screenshots only when the change is visual.
5. Make sure the CI workflow passes before requesting review.
