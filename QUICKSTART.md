# CTO Sidekick - Quick Start Guide

## What You Have Now

A **working MVP orchestrator** that:
- ✅ Reads project priorities from Google Sheets
- ✅ Automatically starts Claude Code on highest priority project
- ✅ Updates status back to Sheet
- ✅ Moves to next project when complete
- ✅ Tracks state and history
- ✅ **Tested with GitHub Actions CI/CD**

## File Structure

```
mikes-meta-agent/
├── src/
│   ├── daemon.py           # Main orchestrator loop
│   ├── scheduler.py        # Priority selection logic
│   ├── sheets.py          # Google Sheets integration
│   ├── state.py           # State persistence
│   ├── models.py          # Data models
│   ├── config.py          # Configuration management
│   ├── mocks.py           # Test mocks (no Google Sheets needed!)
│   ├── status.py          # Status checker script
│   ├── test_basic.py      # Setup verification
│   └── runners/
│       ├── base.py        # Agent runner interface
│       └── claude.py      # Claude Code runner
├── tests/
│   ├── test_scheduler.py     # Unit tests
│   └── test_orchestrator.py  # Integration tests
├── .github/workflows/
│   └── test.yml           # CI/CD testing
├── config.yaml.example    # Example configuration
├── pyproject.toml         # Python package config (uv)
├── run.sh                 # Simple runner script
├── SETUP.md               # Detailed setup guide
└── GOOGLE_SHEET_TEMPLATE.md  # Sheet format guide
```

## Quick Start (3 steps)

### 1. Install Dependencies

```bash
# Create virtual environment and install
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -e .
```

### 2. Configure

```bash
# Copy and edit config
cp config.yaml.example config.yaml
nano config.yaml  # Set your project directories
```

### 3. Test Without Google Sheets

```bash
# Run tests (works offline!)
python tests/test_scheduler.py
python tests/test_orchestrator.py

# All tests should pass
```

## With Google Sheets (Optional but Recommended)

Follow **[SETUP.md](SETUP.md)** to:
1. Create Google Cloud project
2. Enable Sheets API
3. Create service account
4. Download credentials
5. Create and share spreadsheet

Then:

```bash
# Test connection
python src/test_basic.py

# Run orchestrator
./run.sh

# Or run in background
./run.sh bg
```

## Usage

### Check Status

```bash
./run.sh status

# List active tmux sessions
tmux list-sessions | grep claude
```

### Watch Claude in Action

Claude runs in **named tmux sessions** by default:

```bash
# Attach to see what Claude is doing
tmux attach -t claude-{project-name}

# Example for "Antenna ML Pipeline"
tmux attach -t claude-antenna-ml-pipeline

# Detach: Press Ctrl+B, then D
```

See [docs/TMUX_SESSIONS.md](docs/TMUX_SESSIONS.md) for more tmux tips.

### Add a Project

In Google Sheet, add row:
| Project | Priority | Status | Next Action |
|---------|----------|--------|-------------|
| My Project | 1 | Pending | Implement feature X |

Orchestrator checks every 60 seconds and starts highest priority.

### Monitor

```bash
# Live logs
tail -f logs/orchestrator.log

# Recent history
python src/status.py
```

## What's Next

Based on your [planning doc](.claude/planning/cto-sidekick-plan.md), you can add:

### Phase 2: Multi-Model Routing
- Add Qwen runner (local inference)
- Add Gemini runner (API)
- Implement task classification
- Route by complexity:
  - Planning → Claude (if credits available)
  - Implementation → Qwen (local, free)
  - Review → Gemini

### Phase 3: VM Isolation
- Create Ubuntu dev template VM
- Per-project VM cloning
- GPU passthrough for Qwen VM
- Network isolation

### Phase 4: Monitoring
- Web dashboard (Flask/React)
- Mobile access (Tailscale)
- Push notifications (ntfy.sh)
- Credit tracking

## Testing

```bash
# Run all tests
python tests/test_scheduler.py
python tests/test_orchestrator.py

# Tests work in CI/CD without Google Sheets!
# See: .github/workflows/test.yml
```

## Troubleshooting

### "claude command not found"
```bash
npm install -g @anthropic/claude-code
```

### "No module named 'gspread'"
```bash
uv pip install -e .
```

### "Credentials file not found"
- See [SETUP.md](SETUP.md) section 2
- Create Google Cloud service account
- Download JSON to `credentials/sheets-api.json`

### "Spreadsheet not found"
- Check sheet name in `config.yaml` matches exactly
- Verify you shared sheet with service account email

## Architecture Decisions

Based on your goals (from README.md):

**Current (MVP):**
- ✅ Single host, Docker would work but not required yet
- ✅ Sequential execution (one project at a time)
- ✅ Claude only (Qwen/Gemini not integrated yet)
- ✅ Google Sheets for task tracking
- ✅ JSON file for state

**Recommended Next (from your plan):**
- Option 2: VM Pool + Docker Agents
- Dedicated Qwen GPU VM
- Multi-model routing
- FastAPI dashboard

**Why Start Simple:**
- Get value TODAY (orchestration working)
- Test core logic without VM complexity
- Validate Google Sheets integration
- Prove scheduler priority logic works
- Then layer on isolation, multi-model, etc.

## Contributing

Run tests before committing:

```bash
python tests/test_scheduler.py && python tests/test_orchestrator.py
```

GitHub Actions will run these automatically on push.

## License

Private project (as per README.md)

## Questions?

- Setup questions: See [SETUP.md](SETUP.md)
- Google Sheets format: See [GOOGLE_SHEET_TEMPLATE.md](GOOGLE_SHEET_TEMPLATE.md)
- Architecture decisions: See [.claude/planning/cto-sidekick-plan.md](.claude/planning/cto-sidekick-plan.md)
