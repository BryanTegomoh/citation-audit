# Citation Hallucination Audit - Common Commands

.PHONY: install test verify check clean help

# Install dependencies
install:
	pip install -r requirements.txt

# Install in development mode
dev:
	pip install -e .

# Run tests
test:
	python -m pytest tests/ -v

# Verify a single DOI (usage: make verify DOI=10.1038/xxx)
verify:
	python -m citation_toolkit verify $(DOI)

# Check a document (usage: make check FILE=document.md)
check:
	python -m citation_toolkit check $(FILE)

# Batch verify DOIs (usage: make batch FILE=dois.txt)
batch:
	python -m citation_toolkit batch $(FILE) --output report.md

# Extract citations from a file (usage: make extract FILE=document.md)
extract:
	python -m citation_toolkit extract $(FILE)

# Clean generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf *.egg-info
	rm -rf dist build

# Show help
help:
	@echo "Citation Hallucination Audit"
	@echo ""
	@echo "Commands:"
	@echo "  make install       Install dependencies"
	@echo "  make dev           Install in development mode"
	@echo "  make test          Run tests"
	@echo "  make verify DOI=x  Verify a single DOI"
	@echo "  make check FILE=x  Check all citations in a file"
	@echo "  make batch FILE=x  Batch verify DOIs from a text file"
	@echo "  make extract FILE=x Extract citations from a file"
	@echo "  make clean         Remove generated files"
