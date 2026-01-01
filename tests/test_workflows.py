"""Test complete orchestrator workflows including status updates, task resumption, and transitions."""

import sys
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import ProjectStatus
from src.mocks import MockProject, MockSheetsClient, MockClaudeRunner
from src.scheduler import Scheduler
from src.state import StateTracker


def test_complete_workflow_pending_to_completed():
    """Test full workflow: Pending → In Progress → Completed → Next Task."""

    # Setup
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        state_file = Path(f.name)

    state = StateTracker(state_file)
    scheduler = Scheduler()
    sheets = MockSheetsClient()
    claude = MockClaudeRunner()

    # Create two projects
    project_a = MockProject.create(name="Project A", priority=1, directory="/tmp/a")
    project_b = MockProject.create(name="Project B", priority=2, directory="/tmp/b")

    sheets.set_mock_projects([project_a, project_b])

    # === ITERATION 1: Start Project A ===
    projects = sheets.get_projects({"Project A": "/tmp/a", "Project B": "/tmp/b"})
    next_project = scheduler.select_next_project(projects)

    assert next_project.name == "Project A"

    # Update status to In Progress
    sheets.update_project_status(next_project.name, ProjectStatus.IN_PROGRESS, "Claude")

    # Start Claude
    claude.start(next_project, "Work on A")
    state.set_active_project(next_project)

    # Verify status update
    updates = sheets.get_updates()
    assert len(updates) == 1
    assert updates[0]["status"] == ProjectStatus.IN_PROGRESS
    assert updates[0]["agent"] == "Claude"

    # === ITERATION 2: Project A completes ===
    claude.complete_current()

    # Update status to Completed
    sheets.update_project_status(next_project.name, ProjectStatus.COMPLETED)
    state.record_completion(next_project, success=True, details="All done")
    state.set_active_project(None)

    # Verify completion recorded
    updates = sheets.get_updates()
    assert len(updates) == 2
    assert updates[1]["status"] == ProjectStatus.COMPLETED

    history = state.get_recent_history()
    assert any(e["type"] == "completion" for e in history)

    # === ITERATION 3: Move to Project B ===
    # Update Project A status so it's not selected again
    project_a.status = ProjectStatus.COMPLETED
    sheets.set_mock_projects([project_a, project_b])

    projects = sheets.get_projects({"Project A": "/tmp/a", "Project B": "/tmp/b"})
    next_project = scheduler.select_next_project(projects)

    # Should pick Project B now
    assert next_project is not None
    assert next_project.name == "Project B"

    # Start Project B
    sheets.update_project_status(next_project.name, ProjectStatus.IN_PROGRESS, "Claude")
    claude.start(next_project, "Work on B")
    state.set_active_project(next_project)

    # Verify B is active
    active = state.get_active_project()
    assert active["name"] == "Project B"

    # Cleanup
    state_file.unlink()

    print("✅ Complete workflow test passed")


def test_task_stuck_blocked_status():
    """Test handling of blocked/stuck tasks."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        state_file = Path(f.name)

    state = StateTracker(state_file)
    scheduler = Scheduler()
    sheets = MockSheetsClient()
    claude = MockClaudeRunner()

    # Create three projects
    blocked = MockProject.create(name="Blocked", priority=1, status=ProjectStatus.BLOCKED)
    ready = MockProject.create(name="Ready", priority=2, directory="/tmp/ready")
    pending = MockProject.create(name="Pending", priority=3, directory="/tmp/pending")

    sheets.set_mock_projects([blocked, ready, pending])

    # === ITERATION 1: Should skip blocked and pick "Ready" ===
    projects = sheets.get_projects({
        "Blocked": "/tmp/blocked",
        "Ready": "/tmp/ready",
        "Pending": "/tmp/pending"
    })

    next_project = scheduler.select_next_project(projects)

    # Should skip priority 1 (blocked) and pick priority 2 (ready)
    assert next_project is not None
    assert next_project.name == "Ready"

    # Start work
    claude.start(next_project, "Work on Ready")
    sheets.update_project_status(next_project.name, ProjectStatus.IN_PROGRESS, "Claude")

    # === ITERATION 2: "Ready" gets stuck ===
    # Simulate agent hitting a blocker
    claude.stop()

    # Mark as blocked
    sheets.update_project_status(next_project.name, ProjectStatus.BLOCKED)
    state.record_completion(next_project, success=False, details="Missing API key")
    state.set_active_project(None)

    # Update status
    ready.status = ProjectStatus.BLOCKED
    sheets.set_mock_projects([blocked, ready, pending])

    # === ITERATION 3: Should move to "Pending" ===
    projects = sheets.get_projects({
        "Blocked": "/tmp/blocked",
        "Ready": "/tmp/ready",
        "Pending": "/tmp/pending"
    })

    next_project = scheduler.select_next_project(projects)

    # Should pick "Pending" (priority 3) since 1 and 2 are blocked
    assert next_project is not None
    assert next_project.name == "Pending"

    # Verify blocked tasks recorded
    history = state.get_recent_history()
    assert any("Missing API key" in e.get("details", "") for e in history)

    # Cleanup
    state_file.unlink()

    print("✅ Blocked task handling test passed")


def test_resume_after_high_priority_interruption():
    """Test pausing low priority work when high priority arrives, then resuming."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        state_file = Path(f.name)

    state = StateTracker(state_file)
    scheduler = Scheduler()
    sheets = MockSheetsClient()
    claude = MockClaudeRunner()

    # Start with only low priority project
    low_priority = MockProject.create(name="Low Priority", priority=5, directory="/tmp/low")

    sheets.set_mock_projects([low_priority])

    # === ITERATION 1: Start low priority work ===
    projects = sheets.get_projects({"Low Priority": "/tmp/low"})
    next_project = scheduler.select_next_project(projects)

    assert next_project.name == "Low Priority"

    claude.start(next_project, "Work on low priority")
    sheets.update_project_status(next_project.name, ProjectStatus.IN_PROGRESS, "Claude")
    state.set_active_project(next_project)

    # === ITERATION 2: High priority work arrives! ===
    high_priority = MockProject.create(name="URGENT", priority=1, directory="/tmp/urgent")

    sheets.set_mock_projects([low_priority, high_priority])
    projects = sheets.get_projects({
        "Low Priority": "/tmp/low",
        "URGENT": "/tmp/urgent"
    })

    # Check if should switch
    should_switch = scheduler.should_switch_project(low_priority, projects)
    assert should_switch is True

    # Pause current work
    claude.stop()
    sheets.update_project_status(low_priority.name, ProjectStatus.PAUSED)
    state.record_completion(low_priority, success=False, details="Paused for higher priority")

    # Start high priority
    next_project = scheduler.select_next_project(projects)
    assert next_project.name == "URGENT"

    claude.start(next_project, "Work on urgent")
    sheets.update_project_status(next_project.name, ProjectStatus.IN_PROGRESS, "Claude")
    state.set_active_project(next_project)

    # Verify status updates
    updates = sheets.get_updates()
    assert any(u["project"] == "Low Priority" and u["status"] == ProjectStatus.PAUSED for u in updates)
    assert any(u["project"] == "URGENT" and u["status"] == ProjectStatus.IN_PROGRESS for u in updates)

    # === ITERATION 3: Urgent work completes ===
    claude.complete_current()
    sheets.update_project_status(high_priority.name, ProjectStatus.COMPLETED)
    state.record_completion(high_priority, success=True)
    state.set_active_project(None)

    # === ITERATION 4: Resume paused work ===
    # Update statuses
    high_priority.status = ProjectStatus.COMPLETED
    low_priority.status = ProjectStatus.PENDING  # Change back to pending to resume

    sheets.set_mock_projects([low_priority, high_priority])
    projects = sheets.get_projects({
        "Low Priority": "/tmp/low",
        "URGENT": "/tmp/urgent"
    })

    next_project = scheduler.select_next_project(projects)

    # Should resume low priority work
    assert next_project is not None
    assert next_project.name == "Low Priority"

    # Resume work
    claude.start(next_project, "Resume low priority work")
    sheets.update_project_status(next_project.name, ProjectStatus.IN_PROGRESS, "Claude")

    # Verify history shows pause → resume flow
    history = state.get_recent_history()
    # We recorded: paused completion, urgent completion
    assert len(history) >= 2

    # Cleanup
    state_file.unlink()

    print("✅ Resume after interruption test passed")


def test_multiple_status_transitions():
    """Test that status updates are properly tracked through multiple transitions."""

    sheets = MockSheetsClient()

    project = MockProject.create(name="Test", priority=1)

    # Simulate lifecycle transitions
    transitions = [
        (ProjectStatus.PENDING, None),
        (ProjectStatus.IN_PROGRESS, "Claude"),
        (ProjectStatus.PAUSED, "Claude"),
        (ProjectStatus.IN_PROGRESS, "Claude"),
        (ProjectStatus.COMPLETED, None),
    ]

    for status, agent in transitions:
        sheets.update_project_status("Test", status, agent)

    # Verify all updates recorded
    updates = sheets.get_updates()
    assert len(updates) == 5

    # Verify status progression
    assert updates[0]["status"] == ProjectStatus.PENDING
    assert updates[1]["status"] == ProjectStatus.IN_PROGRESS
    assert updates[2]["status"] == ProjectStatus.PAUSED
    assert updates[3]["status"] == ProjectStatus.IN_PROGRESS
    assert updates[4]["status"] == ProjectStatus.COMPLETED

    # Verify agent tracking
    assert updates[1]["agent"] == "Claude"
    assert updates[2]["agent"] == "Claude"
    assert updates[4]["agent"] is None

    print("✅ Multiple status transitions test passed")


def test_no_ready_projects_idle_state():
    """Test that orchestrator handles having no ready projects gracefully."""

    scheduler = Scheduler()
    sheets = MockSheetsClient()

    # All projects blocked or completed
    projects = [
        MockProject.create(name="Blocked", priority=1, status=ProjectStatus.BLOCKED),
        MockProject.create(name="Done", priority=2, status=ProjectStatus.COMPLETED),
        MockProject.create(name="In Progress", priority=3, status=ProjectStatus.IN_PROGRESS),
    ]

    sheets.set_mock_projects(projects)

    fetched = sheets.get_projects({
        "Blocked": "/tmp/blocked",
        "Done": "/tmp/done",
        "In Progress": "/tmp/inprogress"
    })

    next_project = scheduler.select_next_project(fetched)

    # Should return None (nothing to do)
    assert next_project is None

    print("✅ No ready projects test passed")


def test_state_persistence_across_iterations():
    """Test that state is properly saved and loaded across multiple iterations."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        state_file = Path(f.name)

    # === First orchestrator instance ===
    state1 = StateTracker(state_file)

    project = MockProject.create(name="Test", priority=1)
    state1.set_active_project(project)
    state1.add_history_event("start", "Started work", "Initial task")

    # Verify state saved
    assert state_file.exists()

    # === Simulate restart - new instance ===
    state2 = StateTracker(state_file)

    # Should load previous state
    active = state2.get_active_project()
    assert active is not None
    assert active["name"] == "Test"

    history = state2.get_recent_history()
    assert len(history) >= 1
    assert any(e["message"] == "Started work" for e in history)

    # Add more events
    state2.add_history_event("completion", "Finished", "Done")

    # === Third instance to verify ===
    state3 = StateTracker(state_file)
    history = state3.get_recent_history()
    assert len(history) >= 2

    # Cleanup
    state_file.unlink()

    print("✅ State persistence test passed")


if __name__ == "__main__":
    import traceback

    tests = [
        test_complete_workflow_pending_to_completed,
        test_task_stuck_blocked_status,
        test_resume_after_high_priority_interruption,
        test_multiple_status_transitions,
        test_no_ready_projects_idle_state,
        test_state_persistence_across_iterations,
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
