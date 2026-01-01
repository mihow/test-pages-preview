"""Scheduler for prioritizing and routing tasks."""

import logging
from typing import Optional

from models import Project, ProjectStatus


logger = logging.getLogger(__name__)


class Scheduler:
    """Manages task prioritization and selection."""

    def __init__(self):
        """Initialize scheduler."""
        self.active_project: Project | None = None

    def select_next_project(self, projects: list[Project]) -> Project | None:
        """Select the next project to work on based on priority.

        Args:
            projects: List of all projects

        Returns:
            Next project to work on, or None if nothing ready
        """
        # Filter to ready projects
        ready_projects = [p for p in projects if p.is_ready()]

        if not ready_projects:
            logger.debug("No ready projects found")
            return None

        # Sort by priority (lower number = higher priority)
        ready_projects.sort(key=lambda p: p.priority)

        selected = ready_projects[0]
        logger.info(f"Selected project: {selected.name} (Priority {selected.priority})")

        return selected

    def should_switch_project(self, current: Project, projects: list[Project]) -> bool:
        """Check if we should switch from current project to a higher priority one.

        Args:
            current: Currently active project
            projects: List of all projects

        Returns:
            True if should switch to different project
        """
        next_project = self.select_next_project(projects)

        if next_project is None:
            return False

        # Switch if higher priority project is ready
        if next_project.priority < current.priority:
            logger.info(
                f"Higher priority project ready: {next_project.name} "
                f"(P{next_project.priority}) vs current {current.name} (P{current.priority})"
            )
            return True

        return False
