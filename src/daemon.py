#!/usr/bin/env python3
"""
CTO Sidekick - Autonomous Development Orchestration Service

Main daemon that:
1. Reads priorities from Google Sheets
2. Selects highest priority project
3. Starts Claude Code agent
4. Updates status back to Sheet
5. Repeats when agent completes
"""

import logging
import time
import signal
import sys
from pathlib import Path

from src.config import Config
from src.sheets import SheetsClient
from src.scheduler import Scheduler
from src.runners.claude import ClaudeRunner
from src.state import StateTracker
from src.models import ProjectStatus


# Setup logging
def setup_logging(log_file: Path):
    """Configure logging."""
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


logger = logging.getLogger(__name__)


class CTOSidekick:
    """Main orchestrator daemon."""

    def __init__(self, config: Config):
        """Initialize CTO Sidekick.

        Args:
            config: Configuration object
        """
        self.config = config
        self.running = False

        # Initialize components
        logger.info("Initializing CTO Sidekick...")

        self.sheets = SheetsClient(
            config.sheets_credentials,
            config.sheets_spreadsheet_name,
            config.sheets_worksheet_name
        )

        self.scheduler = Scheduler()
        self.state = StateTracker(config.state_file)
        self.claude = ClaudeRunner(
            extra_args=config.claude_extra_args,
            use_tmux=config.claude_use_tmux
        )

        logger.info("CTO Sidekick initialized")

    def run(self):
        """Main daemon loop."""
        logger.info("Starting CTO Sidekick daemon")
        self.running = True

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        while self.running:
            try:
                self._iteration()
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                self.state.add_history_event("error", f"Main loop error: {e}")

            # Sleep before next check
            time.sleep(self.config.sync_interval)

        logger.info("CTO Sidekick daemon stopped")

    def _iteration(self):
        """Single iteration of the main loop."""

        # 1. Fetch current projects from Google Sheets
        projects = self.sheets.get_projects(self.config.project_dirs)

        if not projects:
            logger.debug("No projects found in sheet")
            return

        # 2. Check if Claude is currently running
        if self.claude.is_running():
            current = self.claude.current_project

            # Check if we should switch to higher priority
            if current and self.scheduler.should_switch_project(current, projects):
                logger.info("Switching to higher priority project")
                self.claude.stop()
                self.state.record_completion(
                    current,
                    success=False,
                    details="Paused for higher priority work"
                )
                self.sheets.update_project_status(current.name, ProjectStatus.PAUSED)
            else:
                # Still working on current project
                logger.debug(f"Claude still running on {current.name if current else 'unknown'}")
                return

        # 3. Select next project
        next_project = self.scheduler.select_next_project(projects)

        if not next_project:
            logger.debug("No ready projects to work on")
            return

        # 4. Start Claude on next project
        prompt = self._build_prompt(next_project)

        logger.info(f"Starting work on: {next_project.name}")

        # Update Sheet status to In Progress
        self.sheets.update_project_status(
            next_project.name,
            ProjectStatus.IN_PROGRESS,
            agent="Claude"
        )

        # Start Claude
        success = self.claude.start(next_project, prompt)

        if success:
            self.state.set_active_project(next_project)
            self.state.add_history_event(
                "start",
                f"Started work on {next_project.name}",
                f"Priority: {next_project.priority}, Action: {next_project.next_action}"
            )
        else:
            logger.error(f"Failed to start Claude for {next_project.name}")
            self.sheets.update_project_status(
                next_project.name,
                ProjectStatus.BLOCKED,
                agent=None
            )
            self.state.add_history_event(
                "error",
                f"Failed to start work on {next_project.name}"
            )

    def _build_prompt(self, project: Project) -> str:
        """Build initial prompt for Claude.

        Args:
            project: Project to work on

        Returns:
            Prompt string
        """
        prompt = f"""Project: {project.name}

Next Action: {project.next_action}
"""

        if project.deadline:
            prompt += f"Deadline: {project.deadline}\n"

        prompt += """
Please work on the next action. When complete, provide a summary of what was done and suggest the next action.
"""

        return prompt

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

        # Stop any running agents
        if self.claude.is_running():
            logger.info("Stopping Claude agent...")
            self.claude.stop()

    def status(self) -> dict:
        """Get current orchestrator status.

        Returns:
            Status dictionary
        """
        return {
            "running": self.running,
            "claude_status": self.claude.get_status(),
            "active_project": self.state.get_active_project(),
            "recent_history": self.state.get_recent_history(5)
        }


def main():
    """Main entry point."""
    # Load configuration
    try:
        config = Config("config.yaml")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Setup logging
    setup_logging(config.log_file)

    # Create and run daemon
    daemon = CTOSidekick(config)

    try:
        daemon.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
