.PHONY: codestyle
codestyle:
	uv run ruff check src tests --fix --unsafe-fixes
	uv run ruff format src tests
