# ADR 001: Use Tmux for Claude Sessions

**Date:** 2026-01-01
**Status:** Accepted
**Deciders:** Mike + Claude

## Context

Need a way to run Claude Code that provides:
- Visibility into what Claude is doing
- Persistence across orchestrator restarts
- Easy debugging and intervention
- Professional workflow

## Decision

Run Claude Code in named tmux sessions instead of direct subprocess.

## Rationale

### Considered Options

**Option 1: Direct subprocess (Popen)**
- ✅ Simple implementation
- ❌ No visibility into Claude's output
- ❌ Process dies if orchestrator crashes
- ❌ Hard to debug issues

**Option 2: Tmux sessions (chosen)**
- ✅ Can attach to watch Claude in real-time
- ✅ Sessions persist if orchestrator crashes
- ✅ Easy to intervene if needed
- ✅ Professional dev workflow
- ✅ Output capture available
- ❌ Requires tmux installed (graceful fallback)

**Option 3: Docker containers**
- ✅ Strong isolation
- ✅ Resource limits
- ❌ Much more complex
- ❌ Overhead for simple use case
- ❌ Harder to attach/debug

**Option 4: Screen**
- Similar to tmux but less common
- Worse UX than tmux
- Not as well maintained

## Implementation

```python
class ClaudeRunner:
    def __init__(self, use_tmux=True):
        self.use_tmux = use_tmux  # Default: True

    def _start_with_tmux(self, project, prompt, project_dir):
        session_name = f"claude-{project.name}"
        tmux_cmd = ["tmux", "new-session", "-d", "-s", session_name, ...]
        # ...
```

Session naming: `claude-{project-name-slugified}`

## Consequences

### Positive
- Users can see what Claude is doing: `tmux attach -t claude-project`
- Better debugging experience
- Professional workflow matches other dev tools
- Sessions outlive orchestrator crashes

### Negative
- Requires tmux installation (mitigated with fallback)
- Slightly more complex than direct subprocess
- Need to manage session lifecycle

### Neutral
- Need to document tmux usage for users
- Added configuration option to disable

## Alternatives Considered

Could add Docker support later for VM-based approach (Phase 3).

## References

- Implementation: `src/runners/claude.py`
- Documentation: `docs/TMUX_SESSIONS.md`
- Config: `config.yaml` `agents.claude.use_tmux`
