"""Tests for scheduler module."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scheduler import Scheduler
from models import ProjectStatus
from mocks import MockProject


def test_select_next_project_by_priority():
    """Test that scheduler selects lowest priority number."""
    scheduler = Scheduler()

    projects = [
        MockProject.create(name="Low Priority", priority=5),
        MockProject.create(name="High Priority", priority=1),
        MockProject.create(name="Medium Priority", priority=3),
    ]

    selected = scheduler.select_next_project(projects)

    assert selected is not None
    assert selected.name == "High Priority"
    assert selected.priority == 1


def test_select_next_project_skips_not_ready():
    """Test that scheduler skips projects that aren't ready."""
    scheduler = Scheduler()

    projects = [
        MockProject.create(name="Blocked", priority=1, status=ProjectStatus.BLOCKED),
        MockProject.create(name="In Progress", priority=2, status=ProjectStatus.IN_PROGRESS),
        MockProject.create(name="Ready", priority=3, status=ProjectStatus.PENDING),
    ]

    selected = scheduler.select_next_project(projects)

    assert selected is not None
    assert selected.name == "Ready"


def test_select_next_project_no_ready():
    """Test that scheduler returns None when no projects ready."""
    scheduler = Scheduler()

    projects = [
        MockProject.create(name="Blocked", priority=1, status=ProjectStatus.BLOCKED),
        MockProject.create(name="Complete", priority=2, status=ProjectStatus.COMPLETED),
    ]

    selected = scheduler.select_next_project(projects)

    assert selected is None


def test_should_switch_project():
    """Test that scheduler detects when to switch to higher priority."""
    scheduler = Scheduler()

    current = MockProject.create(name="Current", priority=5)
    higher_priority = MockProject.create(name="Higher", priority=2)

    projects = [current, higher_priority]

    should_switch = scheduler.should_switch_project(current, projects)

    assert should_switch is True


def test_should_not_switch_same_priority():
    """Test that scheduler doesn't switch for same priority."""
    scheduler = Scheduler()

    current = MockProject.create(name="Current", priority=3)
    same_priority = MockProject.create(name="Same", priority=3)

    projects = [current, same_priority]

    should_switch = scheduler.should_switch_project(current, projects)

    assert should_switch is False


if __name__ == "__main__":
    # Simple test runner
    import traceback

    tests = [
        test_select_next_project_by_priority,
        test_select_next_project_skips_not_ready,
        test_select_next_project_no_ready,
        test_should_switch_project,
        test_should_not_switch_same_priority,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
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
