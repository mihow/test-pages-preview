"""Claude Code runner implementation."""

import subprocess
import logging
import shutil
from pathlib import Path
import psutil
import time

from src.models import Project
from src.runners.base import AgentRunner


logger = logging.getLogger(__name__)


class ClaudeRunner(AgentRunner):
    """Runs Claude Code CLI for projects in tmux sessions."""

    def __init__(self, extra_args: list[str] | None = None, use_tmux: bool = True):
        """Initialize Claude runner.

        Args:
            extra_args: Additional arguments to pass to claude command
            use_tmux: Whether to run Claude in a tmux session (default: True)
        """
        super().__init__("claude")
        self.extra_args = extra_args or []
        self.use_tmux = use_tmux
        self.tmux_session_name = None

        # Check if claude is installed
        if not shutil.which("claude"):
            logger.warning("claude command not found in PATH")

        # Check if tmux is installed
        if self.use_tmux and not shutil.which("tmux"):
            logger.warning("tmux not found, falling back to direct subprocess")
            self.use_tmux = False

    def _get_session_name(self, project: Project) -> str:
        """Generate tmux session name for a project."""
        # Sanitize project name for tmux session
        safe_name = project.name.lower().replace(" ", "-").replace("/", "-")
        return f"claude-{safe_name}"

    def _tmux_session_exists(self, session_name: str) -> bool:
        """Check if a tmux session exists."""
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", session_name],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def start(self, project: Project, prompt: str) -> bool:
        """Start Claude Code for a project in a tmux session.

        Args:
            project: Project to work on
            prompt: Initial prompt for Claude

        Returns:
            True if started successfully
        """
        if self.is_running():
            logger.warning(f"Claude already running on {self.current_project.name}")
            return False

        if not project.directory:
            logger.error(f"No directory configured for project: {project.name}")
            return False

        project_dir = Path(project.directory).expanduser()
        if not project_dir.exists():
            logger.error(f"Project directory does not exist: {project_dir}")
            return False

        try:
            if self.use_tmux:
                return self._start_with_tmux(project, prompt, project_dir)
            else:
                return self._start_direct(project, prompt, project_dir)

        except Exception as e:
            logger.error(f"Failed to start Claude: {e}")
            self.process = None
            self.current_project = None
            self.tmux_session_name = None
            return False

    def _start_with_tmux(self, project: Project, prompt: str, project_dir: Path) -> bool:
        """Start Claude in a tmux session."""
        session_name = self._get_session_name(project)

        # Kill existing session if it exists
        if self._tmux_session_exists(session_name):
            logger.info(f"Killing existing tmux session: {session_name}")
            subprocess.run(["tmux", "kill-session", "-t", session_name], timeout=5)
            time.sleep(0.5)

        # Build Claude command
        claude_cmd = ["claude"]
        claude_cmd.extend(self.extra_args)

        # Create new tmux session
        logger.info(f"Starting Claude in tmux session '{session_name}' for {project.name}")
        logger.info(f"Directory: {project_dir}")
        logger.info(f"Prompt: {prompt}")

        # Start tmux session with Claude
        tmux_cmd = [
            "tmux", "new-session",
            "-d",  # Detached
            "-s", session_name,  # Session name
            "-c", str(project_dir),  # Working directory
            " ".join(claude_cmd)  # Command to run
        ]

        result = subprocess.run(tmux_cmd, capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            logger.error(f"Failed to create tmux session: {result.stderr}")
            return False

        # Give tmux a moment to start
        time.sleep(0.5)

        # Verify session exists
        if not self._tmux_session_exists(session_name):
            logger.error(f"tmux session '{session_name}' did not start")
            return False

        # Send initial prompt to the session
        send_cmd = ["tmux", "send-keys", "-t", session_name, prompt, "Enter"]
        subprocess.run(send_cmd, timeout=5)

        self.current_project = project
        self.tmux_session_name = session_name
        self.process = None  # Not using process object with tmux

        logger.info(f"Claude started in tmux session: {session_name}")
        logger.info(f"Attach with: tmux attach -t {session_name}")

        return True

    def _start_direct(self, project: Project, prompt: str, project_dir: Path) -> bool:
        """Start Claude directly without tmux."""
        # Build command
        cmd = ["claude"]
        cmd.extend(self.extra_args)

        # Start Claude Code in project directory
        logger.info(f"Starting Claude Code for {project.name} in {project_dir}")
        logger.info(f"Prompt: {prompt}")

        self.process = subprocess.Popen(
            cmd,
            cwd=project_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )

        # Send initial prompt
        if self.process.stdin:
            self.process.stdin.write(prompt + "\n")
            self.process.stdin.flush()

        self.current_project = project
        logger.info(f"Claude started with PID {self.process.pid}")
        return True

    def is_running(self) -> bool:
        """Check if Claude is currently running."""
        if self.use_tmux and self.tmux_session_name:
            # Check if tmux session exists
            is_alive = self._tmux_session_exists(self.tmux_session_name)
            if not is_alive:
                logger.info(f"tmux session {self.tmux_session_name} has terminated")
                self.tmux_session_name = None
                self.current_project = None
            return is_alive

        elif self.process is not None:
            # Check if process is still alive
            poll = self.process.poll()
            if poll is not None:
                # Process has terminated
                logger.info(f"Claude process terminated with code {poll}")
                self.process = None
                self.current_project = None
                return False
            return True

        return False

    def stop(self) -> bool:
        """Stop the running Claude process or tmux session.

        Returns:
            True if stopped successfully
        """
        if not self.is_running():
            return True

        try:
            if self.use_tmux and self.tmux_session_name:
                logger.info(f"Stopping tmux session: {self.tmux_session_name}")
                subprocess.run(
                    ["tmux", "kill-session", "-t", self.tmux_session_name],
                    timeout=10
                )
                logger.info("Claude tmux session stopped")
                self.tmux_session_name = None
                self.current_project = None
                return True

            elif self.process is not None:
                logger.info(f"Stopping Claude (PID {self.process.pid})")

                # Try graceful shutdown first
                self.process.terminate()

                # Wait up to 10 seconds for graceful shutdown
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning("Claude did not terminate gracefully, killing")
                    self.process.kill()
                    self.process.wait()

                logger.info("Claude stopped")
                self.process = None
                self.current_project = None
                return True

            return False

        except Exception as e:
            logger.error(f"Error stopping Claude: {e}")
            return False

    def get_output(self, max_lines: int = 50) -> str:
        """Get recent output from Claude.

        Args:
            max_lines: Maximum number of lines to return

        Returns:
            Recent output as string
        """
        if not self.is_running():
            return ""

        if self.use_tmux and self.tmux_session_name:
            try:
                # Capture pane content from tmux
                result = subprocess.run(
                    ["tmux", "capture-pane", "-t", self.tmux_session_name, "-p"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    return '\n'.join(lines[-max_lines:])
            except Exception as e:
                logger.error(f"Error capturing tmux output: {e}")

        return "(Output monitoring not implemented for direct mode)"

    def get_status(self) -> str:
        """Get current status string with tmux session info."""
        if self.is_running() and self.current_project:
            if self.tmux_session_name:
                return f"Running: {self.current_project.name} (tmux: {self.tmux_session_name})"
            else:
                return f"Running: {self.current_project.name}"
        return "Idle"
