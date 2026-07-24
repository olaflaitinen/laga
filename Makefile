.PHONY: install lint typecheck test build docs

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

typecheck:
	mypy src/laga

test:
	pytest

build:
	python -m build

docs:
	mkdocs build
