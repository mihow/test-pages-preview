---
paths:
  - "**/*"
---

# Verification Rules

**CRITICAL: Code is not done until it's verified running.**

## Verification Levels

### Level 1: Imports (Minimum)
Code must at least import without errors:
```bash
python -c "from my_project import *"
```

### Level 2: Unit Tests
Tests pass, but this is NECESSARY, NOT SUFFICIENT:
```bash
pytest
```

Unit tests can fake success. They test what you wrote, not what you intended.

### Level 3: Smoke Tests (Required for "done")
Actually run the code and verify output:
```bash
# CLI must execute
my-project info
my-project run --name test

# Scripts must run
python -m my_project.cli info
```

### Level 4: Integration Tests
Test real integrations (databases, APIs, external services):
```bash
# With real dependencies
docker compose up -d
pytest -m integration
```

### Level 5: Browser/E2E Tests
For anything with UI, use chrome-devtools MCP:
- Navigate to the page
- Take a screenshot
- Verify visual output
- Test user interactions

## Before Declaring "Done"

1. **Run it**: Execute the actual code path you changed
2. **Verify output**: Check the output matches expectations
3. **Test edge cases**: Try inputs that might break it
4. **Check logs**: Look for warnings or errors
5. **Screenshot if UI**: Visual verification for any interface

## Red Flags

NEVER say code is "done" or "working" if you only:
- Wrote tests (tests can be wrong)
- Checked syntax (doesn't mean it runs)
- Read the code (doesn't mean it works)
- Assumed it works (verify, don't assume)

## Verification Commands

Add to every task:
```bash
# After implementation, ALWAYS run:
python -c "from my_project import *; print('imports ok')"
pytest -x  # Stop on first failure
my-project info  # Actually run CLI
```

## MCP Server Verification

For MCP servers (chrome-devtools, pylsp), verify they're installed:
```bash
# Chrome DevTools
npx @anthropic/mcp-server-chrome-devtools --version 2>/dev/null || echo "NOT INSTALLED"

# Python LSP
which pylsp || echo "NOT INSTALLED"
pylsp --help 2>/dev/null | head -1 || echo "NOT WORKING"
```
