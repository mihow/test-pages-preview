"""Google Sheets integration for CTO Sidekick."""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging
from pathlib import Path

from src.models import Project, ProjectStatus


logger = logging.getLogger(__name__)


class SheetsClient:
    """Manages Google Sheets integration."""

    def __init__(self, credentials_file: Path, spreadsheet_name: str, worksheet_name: str = "Projects"):
        """Initialize Sheets client.

        Args:
            credentials_file: Path to service account credentials JSON
            spreadsheet_name: Name of the spreadsheet
            worksheet_name: Name of the worksheet (default: "Projects")
        """
        if not credentials_file.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {credentials_file}\n"
                "See README.md for instructions on setting up Google Sheets API."
            )

        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            str(credentials_file),
            scope
        )

        self.client = gspread.authorize(creds)
        self.spreadsheet_name = spreadsheet_name
        self.worksheet_name = worksheet_name
        self._sheet = None
        self._worksheet = None

    def _get_worksheet(self):
        """Get worksheet, opening if needed."""
        if self._worksheet is None:
            self._sheet = self.client.open(self.spreadsheet_name)
            self._worksheet = self._sheet.worksheet(self.worksheet_name)
        return self._worksheet

    def get_projects(self, project_dirs: dict[str, str]) -> list[Project]:
        """Fetch all projects from Google Sheets.

        Args:
            project_dirs: Mapping of project names to directories

        Returns:
            List of Project objects
        """
        try:
            worksheet = self._get_worksheet()
            records = worksheet.get_all_records()

            projects = []
            for row in records:
                try:
                    project = Project.from_sheet_row(row, project_dirs)
                    if project.name:  # Skip empty rows
                        projects.append(project)
                except Exception as e:
                    logger.warning(f"Failed to parse row {row}: {e}")

            logger.info(f"Loaded {len(projects)} projects from Google Sheets")
            return projects

        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet '{self.worksheet_name}' not found in '{self.spreadsheet_name}'")
            return []
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet '{self.spreadsheet_name}' not found")
            return []
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return []

    def update_project_status(self, project_name: str, status: ProjectStatus, agent: str | None = None):
        """Update project status in Google Sheets.

        Args:
            project_name: Name of the project
            status: New status
            agent: Agent name (optional)
        """
        try:
            worksheet = self._get_worksheet()

            # Find the project row
            cell = worksheet.find(project_name)
            if not cell:
                logger.warning(f"Project '{project_name}' not found in sheet")
                return

            row = cell.row

            # Update Status column (assuming column 3)
            worksheet.update_cell(row, 3, status.value)

            # Update Agent column (assuming column 4)
            if agent:
                worksheet.update_cell(row, 4, agent)

            # Update Last Update column (assuming column 5)
            now = datetime.now().isoformat(timespec='seconds')
            worksheet.update_cell(row, 5, now)

            logger.info(f"Updated '{project_name}' status to {status.value}")

        except Exception as e:
            logger.error(f"Error updating project status: {e}")

    def update_next_action(self, project_name: str, next_action: str):
        """Update the next action for a project.

        Args:
            project_name: Name of the project
            next_action: Description of next action
        """
        try:
            worksheet = self._get_worksheet()

            # Find the project row
            cell = worksheet.find(project_name)
            if not cell:
                logger.warning(f"Project '{project_name}' not found in sheet")
                return

            row = cell.row

            # Update Next Action column (assuming column 6)
            worksheet.update_cell(row, 6, next_action)

            logger.info(f"Updated '{project_name}' next action")

        except Exception as e:
            logger.error(f"Error updating next action: {e}")
