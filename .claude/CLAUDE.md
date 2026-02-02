# CLAUDE.md - Project Instructions

<!--
This file is loaded at the start of every Claude Code session.
Keep it concise - only include things Claude can't infer from code.
Run `/init` to regenerate based on current project state.
-->

## Project

A Claude-first Python project template. See @README.md for full documentation.

## IMPORTANT: Verify Your Work

**Code is not "done" until you've run it and seen it work.**

Before declaring any task complete:
```bash
# 1. Verify imports
python -c "from my_project import *; print('imports ok')"

# 2. Run tests
pytest -x

# 3. Actually run the code you changed
my-project info
my-project run --name test
```

Unit tests are NECESSARY but NOT SUFFICIENT. Tests can fake success.
See `.claude/rules/verification.md` for full verification requirements.

## Commands

```bash
# Development
uv pip install -e ".[dev]"  # Install with dev deps
pytest                       # Run tests
pytest --cov=my_project      # With coverage
ruff check src tests         # Lint
ruff format src tests        # Format
mypy src                     # Type check

# Verify
python -c "from my_project import *"  # Import check
my-project info                        # CLI smoke test

# Docker
docker compose run --rm test      # Run tests in container
docker compose run --rm dev       # Development shell
```

## Code Style

- Python 3.12+ with modern type hints (`list[str]`, `X | None`)
- Use Pydantic for data validation
- Tests in `tests/` with pytest fixtures in `conftest.py`

## Project Structure

```
src/my_project/    # Main package
tests/             # Test suite
.claude/           # AI workspace (rules, skills, agents)
```

## Learnings

<!-- Add project-specific gotchas here as you discover them -->
- Clear settings cache between tests: `get_settings.cache_clear()`
- Use `tmp_path` fixture for temporary test files

---

*See `.claude/rules/` for detailed guidelines. Run `/memory` to see all loaded files.*
