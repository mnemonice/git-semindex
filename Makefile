.PHONY: setup build test lint clean format

setup:
	python3 -m pip install maturin && maturin develop

build:
	python3 -m pip install maturin && maturin build --release

test:
	cargo test
	PYTHONPATH=. pytest tests/

lint:
	cargo clippy -- -D warnings
	cargo fmt --check
	ruff check .
	mypy git_semindex

format:
	cargo fmt
	ruff check --fix .

clean:
	cargo clean
	rm -rf target/
	rm -rf venv/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
