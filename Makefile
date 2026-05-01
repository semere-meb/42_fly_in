STUBS_DIR := stubs
TEST_DIR := tests

SRC := *.py
VENV := .venv

run: install
	uv run python main.py

install: $(VENV)

$(VENV): pyproject.toml uv.lock
	pipx install uv || pip install uv
	uv venv --python 3.10
	uv sync

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf .pytest_cache

fclean: clean
	uv cache clean
	rm -rf $(VENV)

lint: $(VENV)
	uvx ruff check $(SRC) $(STUBS_DIR)
	uvx flake8 $(SRC) $(STUBS_DIR)
	uv run mypy $(SRC) \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict: $(VENV)
	uvx ruff check $(SRC) $(STUBS_DIR)
	uvx flake8 $(SRC) $(STUBS_DIR)
	uv run mypy $(SRC) --strict

test: $(VENV)
	uv run pytest

format:
	uvx ruff format $(SRC) $(STUB_DIR) $(TEST_DIR)

debug: $(VENV)
	uv run python -m pdb main.py

re: clean install

fre: fclean install

.PHONY: install run clean lint lint-strict debug re reset-env test
