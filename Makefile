PYTHONPATH=src

.PHONY: test

test:
	export PYTHONPATH=src && poetry run pytest --cov=metadata_registry_svc --cov-report=term-missing --cov-fail-under=100 tests/unit

.PHONY: lint
lint:
	poetry run flake8 src/metadata_registry_svc

.PHONY: format
format:
	poetry run black src/metadata_registry_svc tests/unit

.PHONY: check
check: lint test
