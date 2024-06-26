# define standard colors
ifneq (,$(findstring xterm,${TERM}))
	BLACK        := $(shell tput -Txterm setaf 0)
	RED          := $(shell tput -Txterm setaf 1)
	GREEN        := $(shell tput -Txterm setaf 2)
	YELLOW       := $(shell tput -Txterm setaf 3)
	LIGHTPURPLE  := $(shell tput -Txterm setaf 4)
	PURPLE       := $(shell tput -Txterm setaf 5)
	BLUE         := $(shell tput -Txterm setaf 6)
	WHITE        := $(shell tput -Txterm setaf 7)
	RESET := $(shell tput -Txterm sgr0)
else
	BLACK        := ""
	RED          := ""
	GREEN        := ""
	YELLOW       := ""
	LIGHTPURPLE  := ""
	PURPLE       := ""
	BLUE         := ""
	WHITE        := ""
	RESET        := ""
endif

.PHONY: help
help: ## describe all commands
	@grep -E '^[a-zA-Z_]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: default
default: build

install: ## Installs dependencies
	poetry install

run: ## Runs application
	python -m pytree

.PHONY: test
test: ## Runs tests
	poetry run pytest -vv -s -o log_cli=true -o log_cli_level=DEBUG -o cache_dir=/tmp tests/$(test)

.PHONY: test-cover
test-cover: ## Runs tests with coverage
	poetry run coverage run --source='./sanctumlabs_dbkit/' -m pytest -v --junitxml junit-report.xml tests/ && coverage xml && coverage report -m

.PHONY: format-black
format-black: ## Formats the files with black
	poetry run black .

.PHONY: format-ruff
format-ruff: ## Runs formatting with ruff
	poetry run ruff format sanctumlabs_dbkit

.PHONY: lint-flake8
lint-flake8: ## lints project using flake8
	poetry run pre-commit run -a flake8

.PHONY: lint-mypy
lint-mypy: ## runs type checker with mypy
	poetry run mypy .

.PHONY: lint-pylint
lint-pylint: ## Runs linting with pylint
	poetry run pylint sanctumlabs_dbkit

.PHONY: lint-ruff
lint-ruff: ## Runs linting with ruff
	poetry run ruff check sanctumlabs_dbkit

.PHONY: lint
lint: format-black lint-flake8 lint-mypy lint-pylint

.PHONY: clean
clean: ## removes dist folder
	rm -rf dist

.PHONY: build
build: ## builds project
	poetry self add "poetry-dynamic-versioning[plugin]"
	poetry dynamic-versioning enable
	poetry build

.PHONY: publish-gitlab
publish-gitlab: build ## publish python package to Gitlab package registry
	TWINE_PASSWORD=${CI_JOB_TOKEN} TWINE_USERNAME=gitlab-ci-token poetry run twine upload --repository-url ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/pypi dist/*

.PHONY: publish-pypi
publish-pypi: build ## publish python package to PyPI
	poetry run twine upload --verbose -u '__token__' dist/*
