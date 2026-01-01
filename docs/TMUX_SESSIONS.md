# Using Tmux Sessions with CTO Sidekick

## Overview

By default, CTO Sidekick runs Claude Code in **named tmux sessions**. This provides:

- **Visibility**: Attach to see what Claude is doing in real-time
- **Persistence**: Sessions survive orchestrator restarts
- **Debugging**: Easy to monitor and intervene if needed
- **Multi-project**: Each project gets its own named session

## Session Naming

Sessions are automatically named based on project:
```
claude-{project-name}
```

Examples:
- Project "Antenna ML Pipeline" → `claude-antenna-ml-pipeline`
- Project "APRS Audio Tools" → `claude-aprs-audio-tools`

## Viewing Sessions

### List all Claude sessions
```bash
tmux list-sessions | grep claude
```

### Attach to a session
```bash
# Attach to specific project
tmux attach -t claude-antenna-ml-pipeline

# Detach: Press Ctrl+B, then D
```

### Monitor without attaching
```bash
# Watch session output (updates every 2 seconds)
watch -n 2 'tmux capture-pane -t claude-antenna-ml-pipeline -p | tail -20'
```

## Session Management

### Kill a specific session
```bash
tmux kill-session -t claude-antenna-ml-pipeline
```

### Kill all Claude sessions
```bash
tmux list-sessions | grep claude | cut -d: -f1 | xargs -I{} tmux kill-session -t {}
```

### Check if session is running
```bash
tmux has-session -t claude-antenna-ml-pipeline 2>/dev/null && echo "Running" || echo "Not running"
```

## Orchestrator Integration

The orchestrator automatically:
1. Creates new tmux session when starting work
2. Sends initial prompt to the session
3. Monitors session to detect when Claude finishes
4. Kills session when switching to higher priority work
5. Reuses session names (kills old session if exists)

## Configuration

Control tmux usage in `config.yaml`:

```yaml
agents:
  claude:
    use_tmux: true  # Set to false for direct subprocess (not recommended)
```

### Why use tmux?

**With tmux (default):**
- ✅ Can see what Claude is doing: `tmux attach -t claude-project`
- ✅ Session persists if orchestrator crashes
- ✅ Can manually intervene if needed
- ✅ Easy debugging

**Without tmux:**
- ❌ No visibility into Claude's output
- ❌ Process dies if orchestrator dies
- ❌ Harder to debug issues

## Typical Workflow

### 1. Orchestrator starts work
```
INFO: Starting Claude in tmux session 'claude-antenna-ml-pipeline'
INFO: Attach with: tmux attach -t claude-antenna-ml-pipeline
```

### 2. Check what's happening
```bash
# Quick peek at latest output
tmux capture-pane -t claude-antenna-ml-pipeline -p | tail -20

# Or attach to watch live
tmux attach -t claude-antenna-ml-pipeline
# (Press Ctrl+B D to detach)
```

### 3. Orchestrator completes or switches tasks
```
INFO: Stopping tmux session: claude-antenna-ml-pipeline
```

## Advanced Usage

### Send commands to running session
```bash
# Send additional input to Claude
tmux send-keys -t claude-antenna-ml-pipeline "also add unit tests" Enter
```

### Split session for monitoring
```bash
# Open orchestrator logs alongside Claude session
tmux new-session -s monitor \; \
  send-keys 'tail -f logs/orchestrator.log' C-m \; \
  split-window -h \; \
  send-keys 'tmux attach -t claude-antenna-ml-pipeline' C-m
```

### Save session output
```bash
# Capture full session history
tmux capture-pane -t claude-antenna-ml-pipeline -S -3000 -p > claude-output.log
```

## Troubleshooting

### "tmux not found"
```bash
# Install tmux
sudo apt install tmux  # Debian/Ubuntu
brew install tmux      # macOS
```

Orchestrator will fall back to direct subprocess mode if tmux isn't available.

### Session won't start
Check orchestrator logs:
```bash
tail -f logs/orchestrator.log | grep tmux
```

Common issues:
- Project directory doesn't exist
- Claude not in PATH
- Tmux server not responding (restart: `tmux kill-server`)

### Orphaned sessions
If orchestrator crashes, sessions may persist:
```bash
# List all Claude sessions
tmux list-sessions | grep claude

# Kill them
tmux kill-session -t claude-{project-name}
```

### Disable tmux temporarily
```yaml
# config.yaml
agents:
  claude:
    use_tmux: false
```

Or set environment variable:
```bash
# This doesn't exist yet but could be added if needed
CLAUDE_USE_TMUX=false python src/daemon.py
```

## Tips

1. **Keep terminal multiplexer open**: Have one terminal with tmux to monitor sessions
2. **Use tmux keybindings**: Learn basics (Ctrl+B prefix)
3. **Name your tmux server**: `tmux -L cto-sidekick` for isolated server
4. **Configure tmux**: Add `.tmux.conf` for better UX

Example `.tmux.conf`:
```
# Better mouse support
set -g mouse on

# Scrollback history
set -g history-limit 10000

# Vi mode
setw -g mode-keys vi
```

## Integration with Status Command

The status script shows tmux session names:

```bash
python src/status.py

# Output:
🔵 Active Project:
   Name: Antenna ML Pipeline
   Status: claude-antenna-ml-pipeline (tmux)
   Started: 15 minutes ago
```

## Future Enhancements

Potential additions:
- Dashboard showing all tmux sessions
- Web-based tmux viewer (via ttyd or similar)
- Automatic session recording
- Session snapshots before switching tasks
- Resume from last tmux buffer on restart
