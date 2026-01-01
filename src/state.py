"""State tracking and persistence."""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any

from src.models import Project


logger = logging.getLogger(__name__)


class StateTracker:
    """Manages orchestrator state persistence."""

    def __init__(self, state_file: Path):
        """Initialize state tracker.

        Args:
            state_file: Path to state JSON file
        """
        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        """Load state from file."""
        if not self.state_file.exists():
            return {
                "version": "1.0",
                "last_update": None,
                "active_project": None,
                "completed_projects": [],
                "history": []
            }

        try:
            with open(self.state_file) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            # Return fresh state instead of recursing
            return {
                "version": "1.0",
                "last_update": None,
                "active_project": None,
                "completed_projects": [],
                "history": []
            }

    def _save_state(self):
        """Save state to file."""
        try:
            self.state["last_update"] = datetime.now().isoformat()

            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def set_active_project(self, project: Project | None):
        """Set the currently active project.

        Args:
            project: Active project, or None if idle
        """
        if project:
            self.state["active_project"] = {
                "name": project.name,
                "priority": project.priority,
                "started_at": datetime.now().isoformat()
            }
        else:
            self.state["active_project"] = None

        self._save_state()

    def get_active_project(self) -> dict[str, Any] | None:
        """Get currently active project info."""
        return self.state.get("active_project")

    def record_completion(self, project: Project, success: bool, details: str = ""):
        """Record project completion.

        Args:
            project: Completed project
            success: Whether it completed successfully
            details: Additional details
        """
        completion_record = {
            "name": project.name,
            "priority": project.priority,
            "completed_at": datetime.now().isoformat(),
            "success": success,
            "details": details
        }

        self.state["completed_projects"].append(completion_record)

        # Also add to history
        self.add_history_event(
            "completion",
            f"{'Completed' if success else 'Failed'}: {project.name}",
            details
        )

        self._save_state()

    def add_history_event(self, event_type: str, message: str, details: str = ""):
        """Add event to history.

        Args:
            event_type: Type of event (e.g., 'start', 'completion', 'error')
            message: Event message
            details: Additional details
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "details": details
        }

        if "history" not in self.state:
            self.state["history"] = []

        self.state["history"].append(event)

        # Keep only last 100 events
        self.state["history"] = self.state["history"][-100:]

        self._save_state()

    def get_recent_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent history events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        history = self.state.get("history", [])
        return history[-limit:]
