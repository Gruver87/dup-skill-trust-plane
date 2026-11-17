# Cross-platform targets (GNU Make). Windows: use `.\scripts\demo.ps1` equivalently.
# Optional sibling gates: pip install -e ../dup-skills-eval -e ../dup-skill-security-scan -e ../dup-policy-gate
.PHONY: install test demo lint

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

lint:
	python -m ruff check src tests

demo: install
	python -m skill_trust demo
