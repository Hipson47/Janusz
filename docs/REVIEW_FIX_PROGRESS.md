# Review/Fix Progress

Date: 2026-05-27

## Loop 1: Baseline Review and Fix Batch

Completed a repository-wide production review focused on packaging, dependency
model, CI/release gates, optional-module imports, pre-commit consistency,
mutation-test readiness, hidden stale format references, and documentation
accuracy.

Fixed:

- removed the duplicate `dev` package extra and regenerated `uv.lock`;
- made optional AI `httpx` import lazy and actionable;
- aligned pre-commit `mypy` with the same command used by local release gates;
- repaired mutmut configuration for current mutmut behavior;
- removed hidden legacy-format references;
- updated stale quality-gate documentation;
- accepted final-newline fixes from pre-commit.

Verification run in this loop:

- `uv lock --check`: passed
- `uv sync --group dev --locked`: passed
- `uv run ruff check .`: passed
- `uv run ruff format --check .`: passed
- `uv run mypy src/janusz`: passed
- `uv run python -m compileall -q src scripts examples tests`: passed
- `uv run pytest tests -q`: passed, 60 tests
- `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`: passed, 70.87%
- `uv run bandit -q -r src/janusz`: passed
- `uv run pip-audit`: passed, no known vulnerabilities found; local `janusz` skipped because it is not on PyPI
- `uv build`: passed
- clean wheel smoke: passed
- `uv run pre-commit run --all-files`: passed after hook fix
- `uv run mutmut run`: completed with substantial remaining survivors tracked as P2
- `make release-check`: passed

## Loop 2: Fresh Review

Performed a fresh post-fix review instead of only rechecking the original issue
list.

Fresh searches performed:

- hardcoded paths and developer usernames;
- hidden/no-ignore legacy-format search;
- TODO/FIXME/HACK/dummy/mock/placeholder/nosec/type-ignore/skip/xfail/broad exception sweep;
- optional dependency import sweep;
- CI, Makefile, and documentation command consistency sweep.

Result:

- zero unresolved P0/P1 findings;
- remaining mutation score/test-depth gap documented as P2;
- release-check and pre-commit gates passed after the fix batch.
