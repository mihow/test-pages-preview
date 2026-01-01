"""Data models for CTO Sidekick."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ProjectStatus(Enum):
    """Project status values."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    QUEUED = "Queued"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"
    PAUSED = "Paused"


@dataclass
class Project:
    """Represents a project from Google Sheets."""
    name: str
    priority: int
    status: ProjectStatus
    next_action: str
    deadline: str | None = None
    agent: str | None = None
    last_update: datetime | None = None
    directory: str | None = None

    @classmethod
    def from_sheet_row(cls, row: dict, project_dirs: dict[str, str]) -> "Project":
        """Create Project from Google Sheets row."""
        name = row.get('Project', '')

        # Parse status
        status_str = row.get('Status', 'Pending')
        try:
            status = ProjectStatus(status_str)
        except ValueError:
            status = ProjectStatus.PENDING

        # Parse priority (handle empty/invalid values)
        try:
            priority = int(row.get('Priority', 999))
        except (ValueError, TypeError):
            priority = 999

        # Parse last update
        last_update_str = row.get('Last Update', '')
        last_update = None
        if last_update_str:
            try:
                last_update = datetime.fromisoformat(last_update_str)
            except (ValueError, TypeError):
                pass

        return cls(
            name=name,
            priority=priority,
            status=status,
            next_action=row.get('Next Action', ''),
            deadline=row.get('Deadline'),
            agent=row.get('Agent'),
            last_update=last_update,
            directory=project_dirs.get(name)
        )

    def is_ready(self) -> bool:
        """Check if project is ready to run."""
        return (
            self.status in [ProjectStatus.PENDING, ProjectStatus.QUEUED]
            and self.directory is not None
            and self.next_action
        )

    def __str__(self) -> str:
        return f"{self.name} (P{self.priority}): {self.next_action}"
