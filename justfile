set dotenv-load := true

PYTHON_VERSION := "3.13"
SRC_PATH := "lectures_filter"
TEST_PATH := "tests"
PATHS_TO_LINT := SRC_PATH + " " + TEST_PATH
BUILD_PATH := "build"
CURRENT_DATETIME := `date +'%Y%m%d_%H%M%S'`
ANSWERS_FILE := ".copier/.copier-answers.copier-python-project.yml"

# --- Commands for development ---

# Run all checks and tests (lints, mypy, tests...)
all: lint_full test

# Run all checks and tests, but fail on first that returns error (lints, mypy, tests...)
all_ff: lint_full_ff test

# Run black lint check (code formatting)
black:
    uv run black {{ PATHS_TO_LINT }} --diff --check --color

build: build_create_env
	cd {{ BUILD_PATH }}/pkg && \
	zip -r ../lectures_filter_{{ CURRENT_DATETIME }}.zip .

build_create_env: build_generate_requirements build_install

build_generate_requirements:
	uv export --frozen --no-dev --no-editable -o {{ BUILD_PATH }}/requirements.txt

build_install:
	uv pip install \
	--no-installer-metadata \
	--no-compile-bytecode \
	--python-platform x86_64-manylinux2014 \
	--python {{ PYTHON_VERSION }} \
	--target {{ BUILD_PATH }}/pkg \
	-r {{ BUILD_PATH }}/requirements.txt

# Update project by rerunning copier questionnaire to modify some answers
copier_recopy answers=ANSWERS_FILE:
    copier recopy --answers-file {{ answers }}

# Update project using copier with respect to the answers file
copier_update answers=ANSWERS_FILE:
    copier update --answers-file {{ answers }} --skip-answered

# Run fawltydeps lint check (deopendency issues)
deps:
    uv run fawltydeps

# Run flake8 lint check (pep8 etc.)
flake:
    uv run flake8 {{ PATHS_TO_LINT }}

# Runs Grafana local stack (Loki, Tempo, Mimir)
grafana:
    docker run --name lgtm -p 3000:3000 -p 4317:4317 -p 4318:4318 --rm --network spoton_bridge -ti grafana/otel-lgtm

# Show this help message
@help:
    just --list

# Run isort lint check (import sorting)
isort:
    uv run isort {{ PATHS_TO_LINT }} --diff --check --color

# Run all lightweight lint checks (no mypy)
@lint:
    -just black
    -just deps
    -just flake
    -just isort

# Run all lightweight lint checks, but fail on first that returns error
lint_ff: black deps flake isort

# Automatically fix lint problems (only reported by black and isort)
lint_fix:
    uv run black {{ PATHS_TO_LINT }}
    uv run isort {{ PATHS_TO_LINT }}

# Run all lint checks and mypy
lint_full: lint mypy
alias full_lint := lint_full

# Run all lint checks and mypy, but fail on first that returns error
lint_full_ff: lint_ff mypy
alias full_lint_ff := lint_full_ff

# Run mypy check (type checking)
mypy:
    uv run mypy {{ PATHS_TO_LINT }} --show-error-codes --show-traceback --implicit-reexport

# Open python console (useful when prefixed with dc, as it opens python console inside docker)
ps:
    PYTHONSTARTUP=ipython_startup.py uv run ipython
alias ipython := ps

# Run non-integration tests (optionally specify file=path/to/test_file.py)
test test_path=TEST_PATH:
    uv run pytest {{ test_path }} --durations=10

# --- Separate command versions for github actions ---

_ci: _ci_black _ci_deps _ci_flake8 _ci_isort _ci_mypy _ci_test

_ci_lint: _ci_black _ci_deps _ci_flake8 _ci_isort _ci_mypy

_ci_black:
    uv run black {{ PATHS_TO_LINT }} --diff --check --quiet

_ci_deps:
    uv run fawltydeps --detailed

_ci_flake8:
    uv run flake8 {{ PATHS_TO_LINT }}

_ci_isort:
    uv run isort {{ PATHS_TO_LINT }} --diff --check --quiet

_ci_mypy:
    uv run mypy {{ PATHS_TO_LINT }} --show-error-codes --show-traceback --implicit-reexport --junit-xml=mypy-results.xml

_ci_test:
    uv run pytest {{ TEST_PATH }} --durations=10 --junit-xml=test-results.xml
