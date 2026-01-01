"""Base runner interface for agents."""

from abc import ABC, abstractmethod
from pathlib import Path
import logging

from src.models import Project


logger = logging.getLogger(__name__)


class AgentRunner(ABC):
    """Base class for agent runners."""

    def __init__(self, name: str):
        """Initialize runner.

        Args:
            name: Runner name (e.g., 'claude', 'qwen')
        """
        self.name = name
        self.current_project: Project | None = None
        self.process = None

    @abstractmethod
    def start(self, project: Project, prompt: str) -> bool:
        """Start agent for a project.

        Args:
            project: Project to work on
            prompt: Initial prompt/instruction for agent

        Returns:
            True if started successfully
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """Check if agent is currently running."""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """Stop the running agent.

        Returns:
            True if stopped successfully
        """
        pass

    def get_status(self) -> str:
        """Get current status string."""
        if self.is_running() and self.current_project:
            return f"Running: {self.current_project.name}"
        return "Idle"
