# Claude Code Optimization: Proposed Approaches
## Document Version: 2025-12-31

## Overview

This document presents three implementation approaches (Minimal, Balanced, Maximum) plus alternatives for each component. Each approach builds on the previous one, allowing incremental adoption based on validation results.

---

## APPROACH 1: MINIMAL VIABLE SYSTEM (MVP)
**Timeline**: 1-2 days | **Complexity**: Low | **Risk**: Low

### Philosophy
Get automated continuation working with single fallback model. Prove core concept before expanding.

### Architecture

```
┌─────────────────────────────────┐
│ Cron Job (hourly)               │
│  └─ check-credits.sh            │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│ Claude Code (main)              │
│  ├─ CLAUDE.md (learnings)       │
│  ├─ CONTINUATION.md (state)     │
│  └─ COMPLETED.md (done tasks)   │
└─────────────────────────────────┘
            ↓ (when credits low)
┌─────────────────────────────────┐
│ Gemini MCP (fallback only)      │
│  └─ RLabs gemini-mcp server     │
└─────────────────────────────────┘
```

### Implementation Steps

**1. State Management Files**
```bash
# Initialize project structure
mkdir -p .claude/commands
touch CLAUDE.md CONTINUATION.md COMPLETED.md

# CONTINUATION.md schema
cat > CONTINUATION.md << 'EOF'
# Continuation State
Last Updated: [timestamp]
Credits at Pause: [count]

## Current Task
[Description of what was being worked on]

## Progress
- [x] Completed items
- [ ] Next immediate step
- [ ] Following steps

## Context
[Any important decisions or blockers]

## Next Action
[Specific instruction for resumption]
EOF
```

**2. Credit Checker Script**
```bash
#!/bin/bash
# check-credits.sh - Simple version

LOG_FILE="$HOME/.claude-automation/credit-check.log"
STATE_FILE="$HOME/.claude-automation/state.json"
THRESHOLD=5  # Minimum credits before switching strategies

# Get current credits (parse claude /status output)
# NOTE: Actual parsing needs validation - claude /status format unknown
CREDITS=$(claude /status 2>/dev/null | grep -oP 'remaining: \K\d+' || echo "0")

echo "[$(date -Iseconds)] Credits: $CREDITS" >> "$LOG_FILE"

# Decision logic
if [ "$CREDITS" -ge "$THRESHOLD" ]; then
    echo "status=claude,credits=$CREDITS" > "$STATE_FILE"
else
    echo "status=low,credits=$CREDITS" > "$STATE_FILE"
    # Don't auto-continue if credits too low - just log it
    echo "[$(date -Iseconds)] Credits low ($CREDITS), waiting for renewal" >> "$LOG_FILE"
fi
```

**3. Gemini MCP Setup**
```bash
#!/bin/bash
# setup-gemini-mcp.sh

# Install Gemini MCP server (easiest option)
claude mcp add gemini -s user -- env \
  GEMINI_API_KEY="${GEMINI_API_KEY}" \
  npx -y https://github.com/rlabs-inc/gemini-mcp.git

# Create fallback command
mkdir -p .claude/commands
cat > .claude/commands/gemini-analyze.md << 'EOF'
/gemini-analyze-code general

$ARGUMENTS
EOF

echo "Gemini MCP installed. Test with: claude 'use gemini to analyze this file'"
```

**4. Cron Configuration**
```cron
# Run every hour
0 * * * * /home/user/scripts/check-credits.sh

# Check after each 5-hour renewal (adjust times based on first renewal observed)
5 0,5,10,15,20 * * * /home/user/scripts/check-credits.sh
```

### Validation Tests

1. **Credit checker works**: `./check-credits.sh` logs correctly
2. **Gemini MCP responds**: `claude "use gemini to explain recursion"`
3. **State files persist**: CONTINUATION.md survives shell restarts
4. **Cron executes**: Check logs after 1 hour
5. **Manual continuation**: Read CONTINUATION.md and resume work successfully

### Limitations & Risks

- **No automatic continuation** (manual resume from CONTINUATION.md)
- **Simple credit threshold** (no predictive logic)
- **Single fallback model** (Gemini only)
- **Unknown**: Actual `claude /status` output format (needs verification)
- **Unknown**: Gemini quota adequacy (may hit limits quickly)
- **No remote monitoring** (must SSH to check status)

### Success Metrics
- Credit checks run reliably every hour
- CONTINUATION.md provides sufficient context for resume
- Gemini usable for at least basic queries
- No credit waste during overnight/idle periods

---

## APPROACH 2: BALANCED PRODUCTION SYSTEM
**Timeline**: 3-5 days | **Complexity**: Medium | **Risk**: Medium

### Philosophy
Add local Qwen for heavy lifting, basic remote monitoring, and intelligent task routing.

### Architecture

```
┌──────────────────────────────────────────┐
│ Monitoring Dashboard (tmux status bar)   │
│  └─ Shows: credits, current task, model  │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│ Task Router (route-task.sh)              │
│  ├─ Classifies work type                 │
│  └─ Routes to appropriate model          │
└──────────────────────────────────────────┘
       ↓              ↓              ↓
┌──────────┐  ┌──────────────┐  ┌──────────┐
│ Claude   │  │ Qwen (local) │  │ Gemini   │
│ (coord)  │  │ (boilerplate)│  │ (review) │
└──────────┘  └──────────────┘  └──────────┘
```

### Additional Components

**1. Qwen Local Setup**
```bash
#!/bin/bash
# setup-qwen-local.sh

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Pull Qwen 2.5 Coder 32B
ollama pull qwen2.5-coder:32b

# Create MCP wrapper (pseudo-code, actual implementation TBD)
# RESEARCH NEEDED: Find or create MCP server for Ollama
# Options:
#   - Use existing ollama-mcp server if available
#   - Create custom MCP wrapper
#   - Use programmatic tool calling approach

# Verify model works
ollama run qwen2.5-coder:32b "Write a Python function to check if a number is prime"
```

**2. Task Router**
```python
#!/usr/bin/env python3
# route-task.py - Intelligent task routing

import json
import sys
import subprocess
from enum import Enum
from pathlib import Path

class TaskType(Enum):
    PLANNING = "planning"          # Use Claude
    BOILERPLATE = "boilerplate"    # Use Qwen
    REVIEW = "review"              # Use Gemini
    COMPLEX = "complex"            # Use Claude
    DOCUMENTATION = "documentation" # Use Qwen

class Model(Enum):
    CLAUDE = "claude"
    QWEN = "qwen"
    GEMINI = "gemini"

def classify_task(description: str) -> TaskType:
    """Classify task based on keywords and context."""
    desc_lower = description.lower()
    
    # Simple keyword-based classification (improve with ML later)
    boilerplate_keywords = ["generate", "scaffold", "boilerplate", "template", "create tests"]
    review_keywords = ["review", "analyze", "check", "audit", "security"]
    planning_keywords = ["design", "architecture", "plan", "strategy", "decide"]
    
    if any(kw in desc_lower for kw in boilerplate_keywords):
        return TaskType.BOILERPLATE
    elif any(kw in desc_lower for kw in review_keywords):
        return TaskType.REVIEW
    elif any(kw in desc_lower for kw in planning_keywords):
        return TaskType.PLANNING
    else:
        return TaskType.COMPLEX

def get_credits() -> int:
    """Parse Claude Code credits from status."""
    # RESEARCH NEEDED: Actual parsing logic
    # Placeholder implementation
    try:
        result = subprocess.run(
            ["claude", "/status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Parse output (format unknown, needs verification)
        # return parsed_credits
        return 20  # Placeholder
    except Exception:
        return 0

def route_task(task_description: str) -> Model:
    """Route task to appropriate model based on type and availability."""
    task_type = classify_task(task_description)
    credits = get_credits()
    
    # Routing logic
    if task_type == TaskType.PLANNING or task_type == TaskType.COMPLEX:
        return Model.CLAUDE if credits > 5 else Model.GEMINI
    elif task_type == TaskType.BOILERPLATE or task_type == TaskType.DOCUMENTATION:
        return Model.QWEN
    elif task_type == TaskType.REVIEW:
        return Model.GEMINI
    else:
        return Model.CLAUDE if credits > 10 else Model.QWEN

def main():
    if len(sys.argv) < 2:
        print("Usage: route-task.py 'task description'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    model = route_task(task)
    
    # Output routing decision
    result = {
        "task": task,
        "model": model.value,
        "credits": get_credits(),
        "type": classify_task(task).value
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

**3. tmux Status Bar Integration**
```bash
# .tmux.conf additions
set -g status-right-length 100
set -g status-right '#(bash ~/.claude-automation/tmux-status.sh)'

# tmux-status.sh
#!/bin/bash
STATE_FILE="$HOME/.claude-automation/state.json"

if [ -f "$STATE_FILE" ]; then
    CREDITS=$(jq -r '.credits // "?"' "$STATE_FILE")
    STATUS=$(jq -r '.status // "unknown"' "$STATE_FILE")
    echo "Claude: $CREDITS | $STATUS"
else
    echo "Claude: ?"
fi
```

**4. Enhanced Continuation Script**
```bash
#!/bin/bash
# auto-continue.sh - Enhanced with routing

CONTINUATION="./CONTINUATION.md"
CLAUDE_MD="./CLAUDE.md"
STATE_FILE="$HOME/.claude-automation/state.json"

if [ ! -f "$CONTINUATION" ]; then
    echo "No continuation file found"
    exit 0
fi

# Read continuation state
NEXT_ACTION=$(grep -A 10 "## Next Action" "$CONTINUATION" | tail -n +2)

if [ -z "$NEXT_ACTION" ]; then
    echo "No next action defined in continuation file"
    exit 0
fi

# Route the task
ROUTING=$(python3 ~/scripts/route-task.py "$NEXT_ACTION")
MODEL=$(echo "$ROUTING" | jq -r '.model')

echo "Routing to: $MODEL"
echo "Task: $NEXT_ACTION"

# Execute based on routing (pseudo-code - actual implementation TBD)
case "$MODEL" in
    "claude")
        claude "$NEXT_ACTION"
        ;;
    "qwen")
        # Use Qwen via MCP or direct
        ollama run qwen2.5-coder:32b "$NEXT_ACTION"
        ;;
    "gemini")
        # Use Gemini via MCP
        claude "use gemini to: $NEXT_ACTION"
        ;;
esac
```

### Validation Tests

1. **Task classification accuracy**: Test with 20 diverse task descriptions
2. **Qwen performance**: Benchmark on boilerplate generation task
3. **Model switching**: Verify routing works when credits low
4. **tmux status**: Status bar updates correctly
5. **End-to-end**: Full cycle from credit check → route → execute → update state

### Limitations & Risks

- **Classification logic simplistic** (keyword-based, not ML)
- **No sandbox yet** (E2E testing still manual)
- **Qwen MCP uncertain** (may need custom implementation)
- **Mobile monitoring basic** (tmux only, no dashboard)
- **RESEARCH NEEDED**: 
  - Ollama MCP server existence/quality
  - Qwen vs GPT-4o actual performance gap
  - Gemini quota sufficiency for review tasks

### Success Metrics
- Task routing >80% accuracy (manual validation)
- Qwen handles 50%+ of boilerplate tasks successfully
- Credit waste <10% (unused credits at renewal)
- Remote status visible via tmux

---

## APPROACH 3: MAXIMUM AUTOMATION SYSTEM
**Timeline**: 1-2 weeks | **Complexity**: High | **Risk**: High

### Philosophy
Full automation with subagents, hooks, background tasks, sandbox testing, and web dashboard.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│ Web Dashboard (Flask/FastAPI)                       │
│  ├─ Real-time credit monitoring                     │
│  ├─ Task queue visualization                        │
│  ├─ Model performance metrics                       │
│  └─ Manual intervention controls                    │
└─────────────────────────────────────────────────────┘
                    ↓ (webhooks)
┌─────────────────────────────────────────────────────┐
│ Orchestration Layer (Python daemon)                 │
│  ├─ Task queue management                          │
│  ├─ Subagent lifecycle (create/resume/cleanup)     │
│  ├─ Hook management (test triggers)                │
│  └─ Background task monitoring                     │
└─────────────────────────────────────────────────────┘
       ↓                    ↓                    ↓
┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
│ Claude Code  │  │ Qwen (local)     │  │ Gemini API   │
│  └─Subagents │  │  └─MCP/Direct    │  │  └─MCP       │
└──────────────┘  └──────────────────┘  └──────────────┘
       ↓                                        ↓
┌──────────────────────────────────────────────────────┐
│ Docker Sandbox (agent-infra/sandbox)                 │
│  ├─ Browser (VNC accessible)                        │
│  ├─ Full dev environment                            │
│  └─ Playwright/Selenium for E2E                     │
└──────────────────────────────────────────────────────┐
```

### Additional Components

**1. Subagent Management**
```python
# subagent-manager.py
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class SubagentState:
    agent_id: str
    task: str
    model: str
    created_at: str
    status: str  # active, paused, completed
    
class SubagentManager:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_file = state_dir / "subagents.json"
        self.load_state()
    
    def load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)
                self.agents = [SubagentState(**a) for a in data]
        else:
            self.agents = []
    
    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump([vars(a) for a in self.agents], f, indent=2)
    
    def create_subagent(self, task: str, model: str) -> str:
        """Create new subagent and return agent_id."""
        # RESEARCH NEEDED: Actual Claude Code subagent creation API
        # Placeholder implementation
        agent_id = f"agent_{len(self.agents)}"
        
        state = SubagentState(
            agent_id=agent_id,
            task=task,
            model=model,
            created_at=datetime.now().isoformat(),
            status="active"
        )
        
        self.agents.append(state)
        self.save_state()
        return agent_id
    
    def resume_subagent(self, agent_id: str, continuation: str):
        """Resume existing subagent with new prompt."""
        # RESEARCH NEEDED: Actual resume API
        # Reference from docs: pass resume parameter with agent_id
        pass
    
    def get_active_agents(self) -> list[SubagentState]:
        return [a for a in self.agents if a.status == "active"]
```

**2. Hook Configuration**
```yaml
# .claude/hooks.yml
# RESEARCH NEEDED: Actual hook configuration format

hooks:
  post_code_change:
    trigger: "file_write"
    pattern: "*.py"
    actions:
      - run: "pytest tests/"
      - run: "ruff check ."
      - notify: "code_quality_check"
  
  post_commit:
    trigger: "git_commit"
    actions:
      - run: "update CLAUDE.md with changes"
      - update_continuation: true
  
  low_credits:
    trigger: "credits < 5"
    actions:
      - pause_subagents: true
      - notify: "webhook"
      - update_state: "low_credits"
```

**3. Web Dashboard**
```python
# dashboard.py - Minimal Flask dashboard
from flask import Flask, render_template, jsonify
import json
from pathlib import Path

app = Flask(__name__)
STATE_DIR = Path.home() / ".claude-automation"

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/status')
def status():
    """Return current system status."""
    state_file = STATE_DIR / "state.json"
    
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
    else:
        state = {"status": "unknown"}
    
    # Add subagent info
    subagent_file = STATE_DIR / "subagents.json"
    if subagent_file.exists():
        with open(subagent_file) as f:
            state['subagents'] = json.load(f)
    
    return jsonify(state)

@app.route('/api/metrics')
def metrics():
    """Return usage metrics."""
    # RESEARCH NEEDED: What metrics to track
    return jsonify({
        'credits_used_today': 0,
        'tasks_completed': 0,
        'model_usage': {
            'claude': 0,
            'qwen': 0,
            'gemini': 0
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
```

**4. Sandbox Integration**
```bash
#!/bin/bash
# setup-sandbox.sh

# Option A: agent-infra/sandbox (Docker)
docker pull ghcr.io/agent-infra/sandbox:latest
docker run -d \
  --name claude-sandbox \
  -p 5900:5900 \  # VNC
  -p 6080:6080 \  # noVNC web interface
  -v $(pwd):/workspace \
  ghcr.io/agent-infra/sandbox:latest

# Option B: Custom Playwright container
# RESEARCH NEEDED: Best approach for browser automation sandbox

# Test VNC access
echo "VNC accessible at: vnc://localhost:5900"
echo "Web interface: http://localhost:6080"
```

**5. Background Task Monitor**
```python
# background-monitor.py
import subprocess
import time
from typing import Dict

class BackgroundTaskMonitor:
    def __init__(self):
        self.tasks: Dict[str, dict] = {}
    
    def start_task(self, name: str, command: list):
        """Start background task and track it."""
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.tasks[name] = {
            'pid': proc.pid,
            'started': time.time(),
            'process': proc,
            'status': 'running'
        }
    
    def check_tasks(self):
        """Check status of all background tasks."""
        for name, task in self.tasks.items():
            proc = task['process']
            if proc.poll() is not None:
                task['status'] = 'completed'
                task['exit_code'] = proc.returncode
    
    def get_status(self) -> dict:
        self.check_tasks()
        return {
            name: {
                'status': task['status'],
                'uptime': time.time() - task['started']
            }
            for name, task in self.tasks.items()
        }

# Example usage with dev server
monitor = BackgroundTaskMonitor()
monitor.start_task('dev_server', ['python', 'manage.py', 'runserver'])
```

### Validation Tests

1. **Subagent resume**: Create agent, pause, resume with new context
2. **Hook execution**: Code change triggers tests automatically
3. **Dashboard functionality**: All endpoints return correct data
4. **Sandbox E2E**: Run Playwright test in container
5. **Full integration**: End-to-end workflow with all components
6. **Credit renewal**: System handles 5-hour renewal automatically
7. **Model fallback**: Graceful degradation when model unavailable

### Limitations & Risks

- **HIGH COMPLEXITY**: Many moving parts, harder to debug
- **Maintenance burden**: More code to maintain
- **Unknown factors**:
  - Subagent API stability
  - Hook configuration format
  - Docker Sandboxes availability
  - Dashboard hosting (Tailscale accessibility)
- **Performance overhead**: Dashboard + monitoring + multiple models
- **Single point of failure**: Orchestration daemon crash breaks system

### Success Metrics
- 90%+ automation (minimal human intervention)
- <5 minute recovery from credit renewal
- All three models utilized effectively
- E2E tests running automatically
- Mobile dashboard accessible via Tailscale

---

## ALTERNATIVE APPROACHES

### Alternative A: Cloud-First Strategy
**When to consider**: Local GPU unreliable or want zero local maintenance

```
Everything runs on cloud infrastructure:
- Claude Code (existing)
- Gemini API (existing)
- Qwen → Replace with Groq Cloud (free tier: 1000 RPD)
  OR Together.ai (some free models)
  OR Replicate (pay-per-use)
- Sandbox → E2B cloud sandboxes
- Dashboard → Deploy on Railway/Render/Fly.io
```

**Pros**: No local infrastructure, easier remote access, automatic scaling
**Cons**: Ongoing costs, dependency on multiple services, privacy concerns
**RESEARCH NEEDED**: Groq Cloud stability, Together.ai free tier limits

### Alternative B: Qwen-Primary Strategy
**When to consider**: Qwen proves excellent quality + want cost minimization

```
Reverse the hierarchy:
- Qwen (local): Primary for all coding tasks
- Claude Code: Only for planning and when Qwen stuck
- Gemini: Validation/second opinion only
```

**Pros**: Maximum credit conservation, full local control
**Cons**: Quality ceiling limited by Qwen, no Claude features (artifacts, etc)
**VALIDATION NEEDED**: Qwen vs Claude on complex architecture decisions

### Alternative C: Human-in-Loop Approach
**When to consider**: Automation proves unreliable or complex tasks need oversight

```
Keep system semi-automated:
- Automation checks credits and prepares continuation
- Sends notification requiring manual approval
- Human reviews, approves, or redirects
- System executes approved plan
```

**Pros**: Safer, catches errors before execution, maintains control
**Cons**: Not truly automated, defeats 5-hour renewal benefit
**GOOD FOR**: Initial rollout phase before trusting full automation

### Alternative D: Hybrid Local/Cloud Qwen
**When to consider**: Local GPU sometimes unavailable (laptop unplugged, etc)

```
Implement Qwen redundancy:
- Primary: Local Ollama (fastest, free)
- Fallback: Groq Cloud with Llama 4 (fast, free tier)
- Emergency: Gemini (when both unavailable)
```

**Pros**: Resilient to single point of failure, still mostly free
**Cons**: More complex routing logic, API management
**IMPLEMENTATION**: Modify router to check local Ollama health first

---

## COMPONENT-SPECIFIC ALTERNATIVES

### Sandbox Alternatives

**Option 1: agent-infra/sandbox (Docker)**
- Pro: All-in-one, actively maintained
- Con: Resource overhead
- Research: GitHub stars, last update, community health

**Option 2: Surfkit (Desktop VMs)**
- Pro: Full desktop environment, Ubuntu-based
- Con: Heavier than Docker, more complex
- Research: Current maintenance status, examples

**Option 3: Custom Playwright Container**
- Pro: Lightweight, exactly what's needed
- Con: Custom maintenance, no GUI
- Research: Best base image, VNC setup

**Option 4: E2B Cloud Sandboxes**
- Pro: Zero local resources, MCP integration
- Con: Costs money after free tier, data leaves local
- Research: Pricing, free tier limits

**Option 5: Docker Sandboxes (experimental)**
- Pro: Official Docker support, tight Claude integration
- Con: Experimental status unknown, may not be released
- Research: Actual availability, beta access

**Recommendation**: Start with Option 3 (custom Playwright), migrate to Option 1 if need GUI, or Option 4 if cloud preferred.

### Gemini MCP Alternatives

**Option 1: RLabs-Inc/gemini-mcp**
- Easiest installation, community-maintained
- Unknown: Maintenance status, bug reports

**Option 2: aliargun/mcp-server-gemini**
- Most features, TypeScript-based
- Unknown: Performance, memory usage

**Option 3: jamubc/gemini-mcp-tool (CLI-based)**
- Uses Gemini CLI underneath (sandbox mode bonus)
- Unknown: CLI reliability, Docker dependency

**Option 4: Custom Python wrapper**
- Full control, minimal dependencies
- Effort: Must implement from scratch
- Research: google-generativeai SDK latest changes

**Recommendation**: Start with Option 1 (RLabs), switch to Option 4 if issues arise.

### Qwen Integration Alternatives

**Option 1: MCP Server for Ollama**
- Clean integration with Claude Code
- RESEARCH CRITICAL: Does this exist? Quality?

**Option 2: Programmatic Tool Calling**
- Claude writes Python scripts that call Ollama
- Pro: Flexible, reduces context overhead
- Research: Performance characteristics

**Option 3: Custom Subagent**
- Define Qwen as subagent type
- Pro: Leverages subagent resume capability
- Research: Subagent API for custom models

**Option 4: Direct API calls (no MCP)**
- Simplest, just curl to Ollama
- Con: Loses MCP benefits, manual routing
- Good for: Quick prototyping

**Recommendation**: Pursue Option 1 research first, fall back to Option 4 if nonexistent.

### Monitoring Alternatives

**Option 1: tmux status bar**
- Simplest, already using tmux
- Con: Not visible when not connected

**Option 2: Web dashboard (Flask/FastAPI)**
- Full features, nice interface
- Con: Deployment complexity, Tailscale routing

**Option 3: Telegram/Slack bot**
- Push notifications, mobile-friendly
- Con: External dependency, privacy

**Option 4: Simple webhook + IFTTT/Zapier**
- Minimal code, leverage existing services
- Con: Latency, rate limits

**Option 5: Blink Shell + custom script**
- Built into SSH client, always visible
- Con: Requires Blink Shell purchase ($20)

**Recommendation**: Start with Option 1 (tmux), add Option 4 (webhooks) for critical alerts.

---

## IMPLEMENTATION ROADMAP

### Phase 1: Validation (Days 1-2)
**Goal**: Prove core concepts before building

1. Test Gemini quota (make API calls, measure limits)
2. Benchmark local Qwen (quality, speed, VRAM usage)
3. Parse `claude /status` (verify output format)
4. Test subagent resume (create, pause, resume with agentId)
5. Research MCP servers (Ollama, Gemini, others)

**Decision Point**: If any core assumption fails, revise approach before proceeding.

### Phase 2: MVP (Days 3-4)
**Goal**: Working automation with single fallback

1. Implement Approach 1 (Minimal Viable System)
2. Deploy cron job
3. Install Gemini MCP
4. Create state management files
5. Test end-to-end once

**Success Criteria**: Can resume work after credit renewal with CONTINUATION.md

### Phase 3: Enhancement (Days 5-7)
**Goal**: Multi-model routing and better UX

1. Set up local Qwen
2. Implement task router
3. Add tmux status integration
4. Create custom slash commands
5. Monitor for one week

**Success Criteria**: >50% of boilerplate tasks handled by Qwen

### Phase 4: Automation (Days 8-14)
**Goal**: Full automation with monitoring

1. Implement subagent management
2. Set up hooks (if API available)
3. Deploy web dashboard
4. Sandbox integration
5. Background task monitoring

**Success Criteria**: System runs 24 hours without intervention

---

## CRITICAL UNKNOWNS REQUIRING RESEARCH

### Priority 1 (Blocking)
1. **Claude Code status API**: What does `claude /status` actually output?
2. **Gemini actual quota**: User's real limits (not generic docs)
3. **Subagent API format**: How to create/resume programmatically
4. **Ollama MCP existence**: Is there a ready-made solution?

### Priority 2 (Important)
5. **Docker Sandboxes status**: Available yet or still experimental?
6. **Hook configuration**: Actual format for .claude/hooks.yml
7. **Qwen vs Claude quality**: Benchmark on real tasks
8. **agent-infra/sandbox status**: Maintained? Issues?

### Priority 3 (Nice to have)
9. **Programmatic Tool Calling**: Implementation details
10. **Tool Search Tool**: Adoption timeline for Claude Code
11. **Background tasks**: Persistence across sessions
12. **Blink Shell features**: Worth the $20?

---

## RECOMMENDED STARTING POINT

**For immediate action**: Start with **Approach 1 (MVP)**

**Rationale**:
- Lowest risk, fastest validation
- Tests core assumptions (credit renewal, state persistence)
- Single dependency (Gemini) with known API
- Reversible if approach fails
- Builds foundation for Approach 2/3

**First steps**:
1. Create state management files
2. Write credit checker script (even with placeholder parsing)
3. Install Gemini MCP (RLabs version)
4. Set up cron job
5. Manually test continuation flow once

**Then validate unknowns**:
- Does credit checker work?
- Is Gemini quota sufficient?
- Does CONTINUATION.md provide enough context?

**Decision point after 48 hours**:
- If MVP works: Proceed to Approach 2
- If blockers found: Revisit alternatives
- If Gemini quota insufficient: Switch to cloud alternatives
