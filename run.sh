#!/bin/bash
# Simple runner script for CTO Sidekick

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if config exists
if [ ! -f "config.yaml" ]; then
    echo "❌ config.yaml not found"
    echo ""
    echo "Run this first:"
    echo "  cp config.yaml.example config.yaml"
    echo "  nano config.yaml  # Edit your settings"
    echo ""
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."
if ! python3 -c "import gspread, oauth2client, yaml, psutil" 2>/dev/null; then
    echo "❌ Missing dependencies"
    echo ""
    echo "Install with:"
    echo "  uv pip install -e ."
    echo ""
    exit 1
fi

echo "✅ Dependencies OK"

# Check for command
case "${1:-run}" in
    test)
        echo "🧪 Running basic tests..."
        python3 src/test_basic.py
        ;;
    status)
        echo "📊 Checking status..."
        python3 src/status.py
        ;;
    run)
        echo "🚀 Starting CTO Sidekick daemon..."
        echo "   Press Ctrl+C to stop"
        echo ""
        python3 src/daemon.py
        ;;
    bg)
        echo "🚀 Starting CTO Sidekick in background..."
        nohup python3 src/daemon.py > orchestrator.log 2>&1 &
        PID=$!
        echo "   PID: $PID"
        echo "   Logs: tail -f orchestrator.log"
        echo "   Stop: kill $PID"
        ;;
    *)
        echo "Usage: $0 {test|status|run|bg}"
        echo ""
        echo "Commands:"
        echo "  test   - Run basic setup tests"
        echo "  status - Show current status"
        echo "  run    - Run daemon in foreground (default)"
        echo "  bg     - Run daemon in background"
        exit 1
        ;;
esac
