"""Integration tests for orchestrator."""

import sys
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import ProjectStatus
from mocks import MockProject, MockSheetsClient, MockClaudeRunner
from scheduler import Scheduler
from state import StateTracker


def test_orchestrator_flow():
    """Test basic orchestrator flow without daemon."""

    # Setup components
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        state_file = Path(f.name)

    state = StateTracker(state_file)
    scheduler = Scheduler()
    sheets = MockSheetsClient()
    claude = MockClaudeRunner()

    # Setup mock projects
    projects = [
        MockProject.create(name="Project A", priority=2, directory="/tmp/a"),
        MockProject.create(name="Project B", priority=1, directory="/tmp/b"),
    ]
    sheets.set_mock_projects(projects)

    # Simulate one iteration
    # 1. Fetch projects
    fetched_projects = sheets.get_projects({
        "Project A": "/tmp/a",
        "Project B": "/tmp/b"
    })
    assert len(fetched_projects) == 2

    # 2. Select next project
    next_project = scheduler.select_next_project(fetched_projects)
    assert next_project is not None
    assert next_project.name == "Project B"  # Priority 1 is higher

    # 3. Start Claude
    success = claude.start(next_project, f"Work on: {next_project.next_action}")
    assert success is True
    assert claude.is_running() is True

    # 4. Update state
    state.set_active_project(next_project)
    active = state.get_active_project()
    assert active is not None
    assert active["name"] == "Project B"

    # 5. Update sheet status
    sheets.update_project_status(next_project.name, ProjectStatus.IN_PROGRESS, "Claude")
    updates = sheets.get_updates()
    assert len(updates) == 1
    assert updates[0]["project"] == "Project B"
    assert updates[0]["status"] == ProjectStatus.IN_PROGRESS

    # Simulate completion
    claude.complete_current()
    assert claude.is_running() is False

    state.record_completion(next_project, success=True, details="Completed successfully")
    sheets.update_project_status(next_project.name, ProjectStatus.COMPLETED)

    # Verify history
    history = state.get_recent_history()
    assert len(history) > 0

    # Cleanup
    state_file.unlink()

    print("✅ Orchestrator flow test passed")


def test_priority_switching():
    """Test that higher priority work preempts lower priority."""

    scheduler = Scheduler()
    claude = MockClaudeRunner()

    # Start with low priority project
    low_priority = MockProject.create(name="Low", priority=5)
    claude.start(low_priority, "Work on low priority")

    # Higher priority project arrives
    projects = [
        low_priority,
        MockProject.create(name="High", priority=1)
    ]

    # Should switch?
    should_switch = scheduler.should_switch_project(low_priority, projects)
    assert should_switch is True

    # Stop current work
    claude.stop()

    # Start high priority
    high_priority = scheduler.select_next_project(projects)
    assert high_priority.name == "High"

    print("✅ Priority switching test passed")


if __name__ == "__main__":
    import traceback

    tests = [
        test_orchestrator_flow,
        test_priority_switching,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
