"""Mock implementations for testing without external dependencies."""

from datetime import datetime
from pathlib import Path

from models import Project, ProjectStatus
from runners.base import AgentRunner
from sheets import SheetsClient


class MockProject:
    """Factory for creating test projects."""

    @staticmethod
    def create(
        name: str = "Test Project",
        priority: int = 1,
        status: ProjectStatus = ProjectStatus.PENDING,
        next_action: str = "Do something",
        directory: str = "/tmp/test"
    ) -> Project:
        """Create a mock project for testing."""
        return Project(
            name=name,
            priority=priority,
            status=status,
            next_action=next_action,
            directory=directory,
            deadline="2026-12-31",
            agent=None,
            last_update=datetime.now()
        )


class MockSheetsClient(SheetsClient):
    """Mock Google Sheets client for testing."""

    def __init__(self):
        """Initialize mock client without real credentials."""
        # Skip parent __init__ to avoid credential checks
        self.spreadsheet_name = "Mock Spreadsheet"
        self.worksheet_name = "Projects"
        self._mock_projects = []
        self._updates = []

    def set_mock_projects(self, projects: list[Project]):
        """Set projects to return from get_projects()."""
        self._mock_projects = projects

    def get_projects(self, project_dirs: dict[str, str]) -> list[Project]:
        """Return mock projects."""
        # Update directories from project_dirs
        for project in self._mock_projects:
            if project.name in project_dirs:
                project.directory = project_dirs[project.name]

        return self._mock_projects

    def update_project_status(self, project_name: str, status: ProjectStatus, agent: str | None = None):
        """Record status update instead of writing to sheet."""
        self._updates.append({
            "project": project_name,
            "status": status,
            "agent": agent,
            "timestamp": datetime.now()
        })

    def update_next_action(self, project_name: str, next_action: str):
        """Record next action update."""
        self._updates.append({
            "project": project_name,
            "next_action": next_action,
            "timestamp": datetime.now()
        })

    def get_updates(self) -> list[dict]:
        """Get all recorded updates."""
        return self._updates


class MockAgentRunner(AgentRunner):
    """Mock agent runner for testing."""

    def __init__(self, name: str = "mock"):
        """Initialize mock runner."""
        super().__init__(name)
        self._is_running = False
        self._run_history = []

    def start(self, project: Project, prompt: str) -> bool:
        """Pretend to start agent."""
        self._is_running = True
        self.current_project = project
        self._run_history.append({
            "project": project.name,
            "prompt": prompt,
            "started_at": datetime.now()
        })
        return True

    def is_running(self) -> bool:
        """Return mock running status."""
        return self._is_running

    def stop(self) -> bool:
        """Pretend to stop agent."""
        self._is_running = False
        self.current_project = None
        return True

    def complete_current(self):
        """Mark current job as complete (for testing)."""
        self._is_running = False
        self.current_project = None

    def get_run_history(self) -> list[dict]:
        """Get history of all runs."""
        return self._run_history


class MockClaudeRunner(MockAgentRunner):
    """Mock Claude runner specifically."""

    def __init__(self, extra_args: list[str] | None = None, use_tmux: bool = False):
        """Initialize mock Claude runner."""
        super().__init__("claude")
        self.extra_args = extra_args or []
        self.use_tmux = use_tmux
        self.tmux_session_name = None
