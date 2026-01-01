"""Configuration management for CTO Sidekick."""

import yaml
import os
from pathlib import Path
from typing import Any


class Config:
    """Loads and provides access to configuration."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                "Copy config.yaml.example to config.yaml and customize it."
            )

        with open(self.config_path) as f:
            self._config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-separated key (e.g., 'sheets.spreadsheet_name')."""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    @property
    def sheets_credentials(self) -> Path:
        """Path to Google Sheets credentials file."""
        path = self.get('sheets.credentials_file')
        return Path(path).expanduser()

    @property
    def sheets_spreadsheet_name(self) -> str:
        """Name of the Google Sheets spreadsheet."""
        return self.get('sheets.spreadsheet_name')

    @property
    def sheets_worksheet_name(self) -> str:
        """Name of the worksheet within the spreadsheet."""
        return self.get('sheets.worksheet_name', 'Projects')

    @property
    def sync_interval(self) -> int:
        """How often to check Google Sheets (seconds)."""
        return self.get('sheets.sync_interval', 60)

    @property
    def project_dirs(self) -> dict[str, str]:
        """Mapping of project names to directories."""
        return self.get('projects', {})

    @property
    def max_concurrent_agents(self) -> int:
        """Maximum number of concurrent Claude sessions."""
        return self.get('agents.claude.max_concurrent', 1)

    @property
    def claude_extra_args(self) -> list[str]:
        """Extra arguments to pass to Claude Code."""
        return self.get('agents.claude.extra_args', [])

    @property
    def claude_use_tmux(self) -> bool:
        """Whether to run Claude in tmux sessions."""
        return self.get('agents.claude.use_tmux', True)

    @property
    def state_file(self) -> Path:
        """Path to state file."""
        path = self.get('state.state_file', './state/orchestrator.json')
        return Path(path).expanduser()

    @property
    def log_file(self) -> Path:
        """Path to log file."""
        path = self.get('state.log_file', './logs/orchestrator.log')
        return Path(path).expanduser()
