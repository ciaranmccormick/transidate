SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	poetry run mypy transidate tests/*.py
	poetry run flake8 transidate tests/*.py

.PHONY: unit
unit:
	poetry run pytest tests/

.PHONY: package
package:
	poetry check
	poetry run pip check
	poetry run pip-audit

.PHONY: test
test: lint package unit
