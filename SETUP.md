# CTO Sidekick Setup Guide

Quick start guide to get the orchestrator running.

## Prerequisites

- Python 3.10 or newer
- `uv` package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Claude Code CLI installed (`npm install -g @anthropic/claude-code`)
- Google account (for Google Sheets)

## 1. Install Dependencies

```bash
# Install Python dependencies with uv
uv pip install -e .

# Or install dev dependencies too
uv pip install -e ".[dev]"
```

## 2. Set Up Google Sheets API

### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

### 2.2 Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Give it a name (e.g., "cto-sidekick")
4. Skip optional steps
5. Click on the created service account
6. Go to "Keys" tab
7. Click "Add Key" > "Create New Key" > "JSON"
8. Download the JSON file
9. Save it as `credentials/sheets-api.json` in this repo

### 2.3 Create Google Sheet

1. Create a new Google Sheet
2. Name it "CTO Sidekick - Projects"
3. Create a worksheet named "Projects" with these columns:

| Project | Priority | Status | Agent | Last Update | Next Action | Deadline | GPU? | Model |
|---------|----------|--------|-------|-------------|-------------|----------|------|-------|
| Antenna ML Pipeline | 1 | Queued | - | - | Set up batch processing | 2026-01-15 | Yes | Sonnet 4 |
| APRS Audio Tools | 2 | Pending | - | - | Create CLI wrapper | 2026-01-10 | No | Qwen |

4. Share the sheet with the service account email
   - Get the email from the JSON credentials file (looks like `xxx@xxx.iam.gserviceaccount.com`)
   - Share with "Editor" permissions

## 3. Configure

```bash
# Copy example config
cp config.yaml.example config.yaml

# Edit config
nano config.yaml
```

Update these key settings:
- `sheets.spreadsheet_name`: Name of your Google Sheet
- `projects`: Map your project names to local directories
- `sheets.credentials_file`: Path to your service account JSON

Example config:
```yaml
sheets:
  credentials_file: ./credentials/sheets-api.json
  spreadsheet_name: "CTO Sidekick - Projects"

projects:
  "Antenna ML Pipeline": /home/michael/Projects/antenna
  "APRS Audio Tools": /home/michael/Projects/aprs-tools
```

## 4. Test the Setup

```bash
# Test Google Sheets connection
python src/test_sheets.py

# Check configuration
python src/daemon.py --check
```

## 5. Run the Orchestrator

```bash
# Run in foreground (for testing)
python src/daemon.py

# Or run in background with logging
nohup python src/daemon.py > orchestrator.log 2>&1 &

# Check status
python src/status.py
```

## 6. Set Up as System Service (Optional)

For production use, run as a systemd service:

```bash
# Copy service file
sudo cp systemd/cto-sidekick.service /etc/systemd/system/

# Edit paths in service file
sudo nano /etc/systemd/system/cto-sidekick.service

# Enable and start
sudo systemctl enable cto-sidekick
sudo systemctl start cto-sidekick

# Check status
sudo systemctl status cto-sidekick

# View logs
journalctl -u cto-sidekick -f
```

## Directory Structure

After setup, you should have:

```
mikes-meta-agent/
├── src/
│   ├── daemon.py           # Main orchestrator
│   ├── config.py
│   ├── sheets.py
│   ├── scheduler.py
│   ├── state.py
│   ├── models.py
│   └── runners/
│       ├── base.py
│       └── claude.py
├── credentials/
│   └── sheets-api.json     # Your service account credentials (gitignored)
├── state/
│   └── orchestrator.json   # State file (auto-created)
├── logs/
│   └── orchestrator.log    # Logs (auto-created)
├── config.yaml             # Your configuration (gitignored)
├── config.yaml.example
└── pyproject.toml
```

## Troubleshooting

### "Credentials file not found"
- Make sure you've downloaded the service account JSON
- Check the path in `config.yaml` matches where you saved it

### "Spreadsheet not found"
- Verify the spreadsheet name in `config.yaml` matches exactly
- Make sure you shared the sheet with the service account email

### "claude command not found"
- Install Claude Code: `npm install -g @anthropic/claude-code`
- Or install locally: `npm install @anthropic/claude-code`

### Claude not starting
- Check project directories exist in `config.yaml`
- Verify Claude Code works manually: `cd /project/dir && claude`

## Next Steps

Once running:
1. Update priorities in Google Sheet
2. Orchestrator checks every 60 seconds (configurable)
3. Starts Claude on highest priority project
4. Updates status back to Sheet
5. When complete, moves to next project

Monitor via:
- `python src/status.py` - Quick status check
- `tail -f logs/orchestrator.log` - Live logs
- Google Sheet - See status updates
