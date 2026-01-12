.PHONY: help test test-integration test-unit test-all install uninstall clean build package lint

# Default target
help:
	@echo "mgit - Multi-repository Git operations tool"
	@echo ""
	@echo "Available targets:"
	@echo "  make test             - Run integration tests (fast)"
	@echo "  make test-unit        - Run unit tests (detailed)"
	@echo "  make test-all         - Run all tests"
	@echo "  make build            - Build Debian package"
	@echo "  make install          - Install mgit (requires sudo)"
	@echo "  make uninstall        - Uninstall mgit (requires sudo)"
	@echo "  make clean            - Clean build artifacts"
	@echo "  make lint             - Run linting checks"
	@echo ""

# Run integration tests (fast, recommended)
test: test-integration

test-integration:
	@echo "Running integration tests..."
	@./test_integration.sh

# Run unit tests (detailed)
test-unit:
	@echo "Running unit tests..."
	@python3 test_mgit.py

# Run all tests
test-all: test-integration test-unit
	@echo ""
	@echo "✓ All test suites passed!"

# Build Debian package
build: clean
	@echo "Building Debian package..."
	@./build-deb.sh

# Install package
install:
	@if [ ! -f mgit_1.2.0_all.deb ]; then \
		echo "Package not found. Building..."; \
		make build; \
	fi
	@echo "Installing mgit..."
	@sudo dpkg -i mgit_1.2.0_all.deb
	@echo "✓ mgit installed successfully!"
	@echo "  Run 'mgit --help' to get started"

# Uninstall package
uninstall:
	@echo "Uninstalling mgit..."
	@sudo dpkg -r mgit
	@echo "✓ mgit uninstalled"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf mgit-package
	@rm -f mgit_*.deb
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -f *.pyc
	@echo "✓ Clean complete"

# Package (alias for build)
package: build

# Lint Python code (requires pylint)
lint:
	@if command -v pylint >/dev/null 2>&1; then \
		echo "Running pylint..."; \
		pylint raw/main/mgit test_mgit.py || true; \
	else \
		echo "pylint not installed. Install with: pip3 install pylint"; \
	fi
	@if command -v flake8 >/dev/null 2>&1; then \
		echo "Running flake8..."; \
		flake8 raw/main/mgit test_mgit.py || true; \
	else \
		echo "flake8 not installed. Install with: pip3 install flake8"; \
	fi

# Development workflow
dev-test:
	@make test-integration
	@echo ""
	@echo "Integration tests passed. Ready to commit!"

# Quick smoke test
smoke-test:
	@echo "Running quick smoke test..."
	@python3 raw/main/mgit --help > /dev/null
	@echo "✓ Basic functionality OK"

# Check if requirements are met
check-requirements:
	@echo "Checking requirements..."
	@command -v python3 >/dev/null 2>&1 || (echo "❌ python3 not found" && exit 1)
	@command -v git >/dev/null 2>&1 || (echo "❌ git not found" && exit 1)
	@python3 -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" || \
		(echo "❌ Python 3.6+ required" && exit 1)
	@echo "✓ All requirements met"

# Full pre-release check
pre-release: check-requirements test-all lint
	@echo ""
	@echo "=========================================="
	@echo "Pre-release checks complete!"
	@echo "=========================================="
	@echo "✓ Requirements OK"
	@echo "✓ All tests passed"
	@echo "✓ Linting complete"
	@echo ""
	@echo "Ready to:"
	@echo "  1. make build    - Build package"
	@echo "  2. git tag v1.2.0"
	@echo "  3. git push --tags"
