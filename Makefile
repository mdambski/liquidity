.PHONY: delint
delint:
	poetry run ruff check --fix-only
	poetry run ruff format .

.PHONY: lint
lint:
	poetry run ruff check
	poetry run ruff format . --check

.PHONY: mypy
mypy:
	poetry run mypy .

.PHONY: test
test:
	poetry run pytest tests/ --cov=liquidity --ignore tests/e2e --tb=short

.PHONY: test-e2e
test-e2e:
	poetry run pytest tests/e2e --tb=short

.PHONY: install-deps
install-deps:
	poetry install --with dev
