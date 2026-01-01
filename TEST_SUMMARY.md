# Test Suite Summary

## Overview

The CTO Sidekick has **comprehensive test coverage** including unit tests, integration tests, and workflow tests. All tests use **mocks** so they can run without external dependencies (no Google Sheets or Claude required).

## Test Files

### 1. `tests/test_scheduler.py` - Scheduler Unit Tests

**Coverage:**
- ✅ Priority-based project selection
- ✅ Skipping non-ready projects (blocked, in-progress, completed)
- ✅ Handling empty queue (no ready projects)
- ✅ Priority switching detection

**Tests:**
```
✅ test_select_next_project_by_priority
✅ test_select_next_project_skips_not_ready
✅ test_select_next_project_no_ready
✅ test_should_switch_project
✅ test_should_not_switch_same_priority

5 passed, 0 failed
```

### 2. `tests/test_orchestrator.py` - Integration Tests

**Coverage:**
- ✅ Full orchestrator flow (fetch → select → start → update)
- ✅ Priority-based preemption
- ✅ State tracking
- ✅ Sheet status updates

**Tests:**
```
✅ test_orchestrator_flow
✅ test_priority_switching

2 passed, 0 failed
```

### 3. `tests/test_workflows.py` - Workflow Tests ⭐ NEW

**Coverage:**
- ✅ **Complete lifecycle**: Pending → In Progress → Completed → Next Task
- ✅ **Blocked/stuck tasks**: Handling blocked projects, moving to next
- ✅ **High priority interruption**: Pausing work, switching, resuming
- ✅ **Status transitions**: Multiple status changes tracked properly
- ✅ **Idle state**: Graceful handling when no projects ready
- ✅ **State persistence**: State saved/loaded across restarts

**Tests:**
```
✅ test_complete_workflow_pending_to_completed
✅ test_task_stuck_blocked_status
✅ test_resume_after_high_priority_interruption
✅ test_multiple_status_transitions
✅ test_no_ready_projects_idle_state
✅ test_state_persistence_across_iterations

6 passed, 0 failed
```

## Running Tests

### All tests
```bash
./run_tests.sh
```

### Individual test files
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run specific test suite
python tests/test_scheduler.py
python tests/test_orchestrator.py
python tests/test_workflows.py
```

### CI/CD (GitHub Actions)
```bash
# Tests run automatically on push
# See: .github/workflows/test.yml
```

Tests run in CI without requiring:
- Google Sheets credentials
- Claude Code installed
- External API access

## Test Architecture

### Mocks (`src/mocks.py`)

**MockSheetsClient:**
- Simulates Google Sheets without API calls
- Records status updates for verification
- Allows setting mock project data

**MockAgentRunner / MockClaudeRunner:**
- Simulates agent execution without real processes
- Tracks run history
- Allows testing agent lifecycle

**MockProject:**
- Factory for creating test projects
- Configurable status, priority, directory

### Why Mocks?

1. **Speed**: Tests run in <1 second
2. **Reliability**: No external dependencies
3. **Isolation**: Test one component at a time
4. **CI/CD**: Run in GitHub Actions without setup

## What's Tested

### ✅ Scheduler Logic
- [x] Priority selection (lowest number wins)
- [x] Status filtering (skip blocked/completed)
- [x] Empty queue handling
- [x] Priority switching detection

### ✅ State Management
- [x] Active project tracking
- [x] Completion recording
- [x] History logging
- [x] Persistence (save/load from JSON)

### ✅ Google Sheets Integration
- [x] Status updates (Pending → In Progress → Completed)
- [x] Agent assignment tracking
- [x] Timestamp updates
- [x] Multiple transitions

### ✅ Workflow Scenarios
- [x] Normal flow: Start → Work → Complete → Next
- [x] Blocked tasks: Skip and move to next ready project
- [x] Interruption: Pause for higher priority, resume after
- [x] Idle state: Handle no ready projects gracefully

### ✅ Edge Cases
- [x] No projects available
- [x] All projects blocked
- [x] State file corruption (creates fresh state)
- [x] Session resumption after restart

## Test Metrics

| Test File | Tests | Lines | Coverage Focus |
|-----------|-------|-------|----------------|
| test_scheduler.py | 5 | 134 | Priority logic |
| test_orchestrator.py | 2 | 126 | Integration flow |
| test_workflows.py | 6 | 387 | Real-world scenarios |
| **Total** | **13** | **647** | **Full system** |

## Future Test Additions

Potential areas for expansion:

- [ ] Tmux session management tests
- [ ] Multi-model routing tests (when Qwen/Gemini added)
- [ ] Error recovery tests
- [ ] Credit monitoring tests
- [ ] VM lifecycle tests (when VM support added)
- [ ] Dashboard API tests
- [ ] Concurrent project tests (multi-agent)

## Adding New Tests

### 1. Unit Test Pattern
```python
def test_feature_name():
    """Test description."""
    # Setup
    component = SomeComponent()

    # Execute
    result = component.do_something()

    # Verify
    assert result == expected
    print("✅ Test passed")
```

### 2. Integration Test Pattern
```python
def test_integration_scenario():
    """Test multi-component interaction."""
    # Setup components
    scheduler = Scheduler()
    sheets = MockSheetsClient()
    state = StateTracker(temp_file)

    # Execute workflow
    projects = sheets.get_projects({...})
    next_proj = scheduler.select_next_project(projects)
    state.set_active_project(next_proj)

    # Verify integration
    assert state.get_active_project()["name"] == next_proj.name
```

### 3. Workflow Test Pattern
```python
def test_complete_workflow():
    """Test end-to-end scenario."""
    # Simulate multiple iterations
    for iteration in range(3):
        # Fetch state
        # Make decision
        # Execute action
        # Update state
        # Verify state transition

    # Verify final state
```

## Running Before Commit

Always run tests before committing:

```bash
./run_tests.sh && git add . && git commit -m "Your message"
```

Or set up a pre-commit hook:

```bash
# .git/hooks/pre-commit
#!/bin/bash
./run_tests.sh || exit 1
```

## CI/CD Integration

Tests run automatically in GitHub Actions on every push:

```yaml
# .github/workflows/test.yml
- name: Run scheduler tests
  run: python tests/test_scheduler.py

- name: Run orchestrator integration tests
  run: python tests/test_orchestrator.py

- name: Run workflow tests
  run: python tests/test_workflows.py
```

## Success Criteria

✅ All tests must pass before merge
✅ New features must include tests
✅ Tests must run in <5 seconds
✅ Tests must work offline (no external deps)
✅ CI must be green
