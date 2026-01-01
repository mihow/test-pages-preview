#!/bin/bash
# Run all tests for CTO Sidekick

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Running CTO Sidekick Test Suite"
echo "========================================="
echo ""

# Ensure virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d ".venv" ]; then
        echo "🔧 Activating virtual environment..."
        source .venv/bin/activate
    else
        echo "❌ No virtual environment found. Run:"
        echo "   uv venv && source .venv/bin/activate && uv pip install -e ."
        exit 1
    fi
fi

# Run tests
TESTS=(
    "tests/test_scheduler.py"
    "tests/test_orchestrator.py"
    "tests/test_workflows.py"
)

PASSED=0
FAILED=0

for test in "${TESTS[@]}"; do
    echo "───────────────────────────────────────"
    echo "Running: $test"
    echo "───────────────────────────────────────"

    if python "$test"; then
        ((PASSED++))
    else
        ((FAILED++))
    fi

    echo ""
done

echo "========================================="
echo "Test Summary"
echo "========================================="
echo "Test files passed: $PASSED/${#TESTS[@]}"
echo "Test files failed: $FAILED/${#TESTS[@]}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All test suites passed!"
    exit 0
else
    echo "❌ Some test suites failed"
    exit 1
fi
