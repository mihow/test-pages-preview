# Practical Autonomous Agent Strategies: Sandbox Comparison
## For Real-World Development with curl, npm, and Full Autonomy
## Created: 2025-12-31

## The Reality Check

You're absolutely right. Let me address the practical reality:

**Babysitting defeats the purpose of agents**. If you're clicking approve every 30 seconds, you might as well write the code yourself. For autonomous work that runs while you're doing other things, you need one of these approaches:

1. Native Claude Code `/sandbox` mode (NEW)
2. Docker Sandboxes (Official Docker + Claude integration)
3. Community Docker solutions
4. QEMU/Proxmox VMs
5. Cloud sandboxes (Claude Code on Web)

---

## Approach 1: Native Claude Code `/sandbox` Mode

### What It Is
**Built-in OS-level sandboxing** using:
- **Linux**: bubblewrap
- **macOS**: seatbelt
- **Windows**: Not yet supported

### How It Works
```bash
# In Claude Code session
claude
> /sandbox

# Configure boundaries
Filesystem: /home/user/project (working directory only)
Network: npm, github, pypi (allowlist)

# Now run with auto-allow
# Commands within boundaries = no prompts
# Commands outside boundaries = prompt
```

### Technical Implementation
- **Filesystem isolation**: Can only read/write working directory
- **Network proxy**: Unix socket to proxy server outside sandbox
- **Proxy enforces**: Domain allowlist/denylist
- **Process isolation**: All subprocesses inherit restrictions

### Configuration
```json
// .claude/settings.json
{
  "sandbox": {
    "enabled": true,
    "autoAllow": true,  // Auto-approve sandboxed commands
    "filesystem": {
      "allowedPaths": [
        "${workspaceFolder}",
        "${workspaceFolder}/**"
      ]
    },
    "network": {
      "allowedDomains": [
        "*.npmjs.org",
        "registry.npmjs.org",
        "*.pypi.org",
        "pypi.org",
        "github.com",
        "api.github.com",
        "*.githubusercontent.com",
        "api.anthropic.com"
      ],
      "requireConfirmation": false  // Auto-approve allowed domains
    }
  }
}
```

### Practical Allowlist for Development
```json
{
  "sandbox": {
    "network": {
      "allowedDomains": [
        // Package managers
        "*.npmjs.org",
        "registry.npmjs.org", 
        "*.npm.taobao.org",
        "*.pypi.org",
        "pypi.org",
        "files.pythonhosted.org",
        "*.pythonhosted.org",
        
        // Version control
        "github.com",
        "*.github.com",
        "api.github.com",
        "raw.githubusercontent.com",
        "gitlab.com",
        "*.gitlab.com",
        
        // CDNs
        "cdn.jsdelivr.net",
        "unpkg.com",
        "cdnjs.cloudflare.com",
        
        // Docker/containers
        "registry-1.docker.io",
        "*.docker.io",
        "gcr.io",
        "*.gcr.io",
        
        // Cloud providers (if needed)
        "*.amazonaws.com",
        "*.cloudfront.net",
        
        // AI services (for MCP)
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        
        // Documentation
        "docs.rs",
        "*.readthedocs.io",
        
        // Your internal services
        "*.yourdomain.com"
      ]
    }
  }
}
```

### Pros
✅ **84% reduction in permission prompts** (Anthropic's data)
✅ **Native integration** - no extra tools
✅ **OS-level security** - not just process isolation
✅ **Auto-allow mode** - truly autonomous within boundaries
✅ **Network proxy** - prevents exfiltration even with curl
✅ **Works on macOS + Linux** - your platforms
✅ **Persistent config** - set once, use everywhere
✅ **Allows curl/wget** - within domain allowlist

### Cons
❌ **Relatively new** - launched Nov 2025, patterns still emerging
❌ **macOS seatbelt** - less robust than Linux bubblewrap
❌ **No Windows support** (you don't use Windows)
❌ **Initial configuration** - need to build domain allowlist
❌ **Not VM-level isolation** - still on host OS

### Security Model
**What's Protected**:
- Filesystem: Can't touch anything outside working dir
- Network: Can only connect to allowlisted domains
- Prompt injection: Can't exfiltrate to random attacker.com

**What's NOT Protected**:
- Code within project can still be malicious
- Allowlisted domains could be compromised
- Host OS shares kernel with sandbox

### For Auto-Continuation
```bash
#!/bin/bash
# auto-continue-with-sandbox.sh

# Start Claude with sandbox enabled
claude <<EOF
/sandbox

# Read continuation task
$(cat CONTINUATION.md)
EOF
```

**Works because**: 
- Sandbox allows common dev tools automatically
- Network allowlist covers npm, pip, github
- No prompts for file operations in working dir
- Runs completely autonomous

---

## Approach 2: Docker Sandboxes (Official Docker + Claude)

### What It Is
**Docker's official Claude Code sandbox integration** (released Dec 2024).

### Setup
```bash
# Install Docker Desktop with AI features
# Enable Docker Sandboxes in settings

# Run Claude in sandbox
docker sandbox run claude

# Or with specific workspace
docker sandbox run claude --workspace /path/to/project
```

### How It Works
- Claude runs inside Docker container
- Project directory mounted as volume
- Credentials stored in persistent Docker volume
- Network controlled by Docker
- Container auto-cleaned after session

### Configuration
```yaml
# Docker Desktop AI settings
sandboxes:
  claude:
    image: docker/sandbox-templates:claude-code
    volumes:
      - ${workspace}:/workspace
    network_mode: bridge  # Or host, none
    environment:
      - DEBUG=0
```

### Network Control
```bash
# Allow specific domains via Docker network
docker network create claude-net \
  --opt com.docker.network.bridge.name=claude0

# Run with network restrictions
docker sandbox run claude \
  --network claude-net \
  --add-host "npmjs.org:0.0.0.0"  # Block
  --add-host "pypi.org:0.0.0.0"   # Block
```

**Better approach**: Use firewall rules in container

### Pros
✅ **Official Docker integration** - well-supported
✅ **Container isolation** - true process + filesystem boundary
✅ **Persistent credentials** - stored in Docker volume
✅ **Auto-cleanup** - containers deleted after use
✅ **Works everywhere** - Linux, macOS, Windows
✅ **Can use --dangerously-skip-permissions** - safely
✅ **Multiple parallel sandboxes** - different projects
✅ **Docker socket access** - can run docker commands inside

### Cons
❌ **Requires Docker Desktop** - resource overhead
❌ **Network control awkward** - not as clean as native sandbox
❌ **Volume mounts** - path mapping can be confusing
❌ **Docker learning curve** - need to understand images/volumes
❌ **Credential management** - slightly complex setup

### For Auto-Continuation
```bash
#!/bin/bash
# auto-continue-docker-sandbox.sh

# Run in Docker sandbox with YOLO mode
docker sandbox run claude -- \
  --dangerously-skip-permissions \
  -p "$(cat CONTINUATION.md)"

# Container auto-deleted after completion
```

---

## Approach 3: Community Docker Solutions

### Option A: textcortex/claude-code-sandbox

**Most mature community solution**

```bash
# Install
npm install -g claude-code-sandbox

# Run
claude-sandbox start

# Web UI for monitoring
# Opens browser at http://localhost:3377
```

**Features**:
- Browser-based terminal
- Auto port forwarding
- Multiple parallel sandboxes
- Persistent config
- Podman support

### Option B: Z7Lab/claude-code-sandbox

**Simpler, script-based**

```bash
# Clone
git clone https://github.com/Z7Lab/claude-code-sandbox
cd claude-code-sandbox

# Run
./run-claude-sandboxed.sh
```

**Features**:
- Single script
- Project-specific paths
- tmp/ directory for external files
- Clean separation from host
- No npm install needed

### Pros (Community Solutions)
✅ **Specifically designed for Claude Code**
✅ **Pre-configured** - works out of box
✅ **Web monitoring** (textcortex)
✅ **Simple scripts** (Z7Lab)
✅ **Full YOLO mode** - safe because containerized
✅ **Active development** - community-driven

### Cons
❌ **Third-party code** - not official
❌ **Maintenance risk** - could be abandoned
❌ **Varying quality** - not all equal

### For Auto-Continuation
```bash
#!/bin/bash
# With textcortex
claude-sandbox start --name auto-work --no-web
# Runs in background, no browser needed

# With Z7Lab
cd ~/project
~/claude-code-sandbox/run-claude-sandboxed.sh \
  --dangerously-skip-permissions \
  -p "$(cat CONTINUATION.md)"
```

---

## Approach 4: QEMU/Proxmox VMs

### What It Is
**Full virtual machine isolation** - complete OS running in VM.

### Setup (Proxmox Example)
```bash
# Create VM template
# - Ubuntu 24.04
# - Install Claude Code
# - Install dev tools
# - Configure networking

# Clone from template for each project
qm clone 9000 101 --name claude-work-1

# Start VM
qm start 101

# SSH in and run Claude
ssh vm101
claude --dangerously-skip-permissions
```

### Networking Options

**Option 1: Host-only network**
- VM can talk to host
- VM cannot reach internet
- Good for: Local-only work

**Option 2: NAT with firewall**
```bash
# Allow only specific destinations
iptables -A OUTPUT -d pypi.org -j ACCEPT
iptables -A OUTPUT -d npmjs.org -j ACCEPT
iptables -A OUTPUT -j DROP
```

**Option 3: Proxy through host**
```bash
# In VM, set proxy
export HTTP_PROXY=http://host:3128
export HTTPS_PROXY=http://host:3128

# On host, run filtering proxy (squid)
# Configure allowed domains
```

### Pros
✅ **Maximum isolation** - complete OS separation
✅ **Kernel-level separation** - VM can't affect host kernel
✅ **Snapshot/rollback** - instant recovery
✅ **Network control** - full firewall capability
✅ **Multiple VMs** - parallel isolated environments
✅ **Can run Docker inside** - VM + container layers
✅ **GPU passthrough** - can use your RTX 3090s

### Cons
❌ **Heavy resource usage** - full OS overhead
❌ **Slow startup** - VM boot time
❌ **Complex setup** - requires VM infrastructure
❌ **File sharing** - need to mount/sync project files
❌ **Overkill** - for most use cases

### For Auto-Continuation
```bash
#!/bin/bash
# auto-continue-vm.sh

# Ensure VM running
qm status 101 || qm start 101

# Wait for boot
sleep 10

# SSH and run Claude
ssh vm101 << 'EOF'
cd /workspace/project
claude --dangerously-skip-permissions \
  -p "$(cat CONTINUATION.md)"
EOF

# Optionally: snapshot after completion
qm snapshot 101 "post-work-$(date +%s)"
```

---

## Approach 5: Claude Code on the Web (Cloud Sandbox)

### What It Is
**Anthropic-managed cloud VMs** running Claude Code.

### How It Works
1. Connect GitHub repo in claude.ai
2. Describe task in web interface
3. Claude clones repo to Anthropic VM
4. Runs in isolated sandbox environment
5. Creates PR when done

### Network Configuration
```json
// In web UI settings
{
  "allowedDomains": [
    "npmjs.org",
    "pypi.org",
    "github.com"
  ],
  "requireApproval": false
}
```

### Pros
✅ **Zero local setup** - works immediately
✅ **Mobile access** - iOS app support
✅ **Anthropic-managed security** - they handle isolation
✅ **Parallel tasks** - multiple VMs simultaneously
✅ **No local resources** - doesn't use your CPU/RAM
✅ **Automatic cleanup** - VMs destroyed after task

### Cons
❌ **Requires internet** - can't work offline
❌ **Pro/Max/Team/Enterprise only** - not free
❌ **Code leaves local machine** - privacy concern
❌ **Less control** - can't customize VM environment
❌ **GitHub-centric** - requires GitHub repo

### For Auto-Continuation
**Not designed for this**. Web version is task-based, not continuous.

---

## PRACTICAL COMPARISON TABLE

| Feature | Native /sandbox | Docker Sandboxes | Community Docker | QEMU/Proxmox | Cloud (Web) |
|---------|----------------|------------------|------------------|--------------|-------------|
| **Setup complexity** | Low | Medium | Low | High | None |
| **Resource usage** | Low | Medium | Medium | High | None (remote) |
| **Isolation strength** | Medium | High | High | Maximum | High |
| **Network control** | Excellent | Good | Good | Excellent | Limited |
| **Allows curl** | ✅ (allowlist) | ✅ | ✅ | ✅ | ✅ (allowlist) |
| **Auto-continuation** | ✅ Perfect | ✅ Good | ✅ Good | ✅ Possible | ❌ Not designed |
| **Mobile monitoring** | ❌ | Via SSH | Via Web UI | Via SSH | ✅ Native |
| **Multi-platform** | macOS, Linux | All | All | All | All |
| **Free** | ✅ | ✅ | ✅ | ✅ | ❌ (Pro+) |
| **Offline capable** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **GPU access** | ✅ | ⚠️ Limited | ⚠️ Limited | ✅ Passthrough | ❌ |
| **Prompt injection defense** | Good | Good | Good | Excellent | Good |

---

## RECOMMENDED APPROACH FOR YOUR USE CASE

Given your requirements:
- Auto-continuation every 5 hours
- Remote monitoring (iPhone via Tailscale)
- Need curl, npm, pip access
- Already have local infrastructure (48GB GPU)
- Biodiversity/conservation work (can't risk data loss)

### Primary Recommendation: Native `/sandbox` Mode

**Why**:
1. ✅ **Allows curl with domain allowlist** - solves your "curl is required" problem
2. ✅ **Auto-allow mode** - no babysitting
3. ✅ **84% fewer prompts** - Anthropic's verified data
4. ✅ **Native to Claude Code** - no extra infrastructure
5. ✅ **Works on your platforms** - Debian + macOS
6. ✅ **Persistent config** - set allowlist once
7. ✅ **Perfect for auto-continuation** - designed for autonomous work

**Setup**:
```json
// ~/.claude/settings.json
{
  "sandbox": {
    "enabled": true,
    "autoAllow": true,
    "filesystem": {
      "allowedPaths": ["${workspaceFolder}/**"]
    },
    "network": {
      "allowedDomains": [
        // Your actual needs
        "*.npmjs.org",
        "registry.npmjs.org",
        "*.pypi.org",
        "pypi.org",
        "files.pythonhosted.org",
        "github.com",
        "*.github.com",
        "api.github.com",
        "raw.githubusercontent.com",
        "*.github.io",
        
        // AI APIs for multi-model
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        
        // Documentation
        "docs.python.org",
        "docs.djangoproject.com",
        "*.readthedocs.io",
        
        // Your biodiversity services
        "antenna.biodiversity.org",
        "ebutterfly.org",
        "*.insectarium.ca",
        
        // Add as needed, review quarterly
        "*.stackoverflow.com",
        "cdn.jsdelivr.net"
      ],
      "requireConfirmation": false
    }
  }
}
```

### Secondary Recommendation: Docker Sandboxes

**For tasks you don't trust yet** - use Docker with YOLO mode:

```bash
# auto-continue-hybrid.sh

# Classify task risk
TASK=$(cat CONTINUATION.md)

if echo "$TASK" | grep -q "experimental\|refactor\|migration"; then
    # High risk = Docker sandbox
    docker sandbox run claude -- \
      --dangerously-skip-permissions \
      -p "$TASK"
else
    # Low risk = Native sandbox
    claude -p "$TASK"  # /sandbox already enabled
fi
```

### Tertiary: QEMU for Sandbox + Qwen

**Your local Qwen GPU setup** could run in a VM:

```
Host (Debian):
├─ Proxmox/QEMU
│  ├─ VM1: Claude Code work (CPU only)
│  └─ VM2: Qwen inference (GPU passthrough)
```

**Why**:
- Isolate Claude work from GPU box
- VM2 gets both RTX 3090s
- Qwen MCP server runs in VM2
- Claude in VM1 calls Qwen via network

**But**: Probably overkill unless you're doing untrusted code experiments

---

## ADDRESSING YOUR SPECIFIC CONCERNS

### "Curl is a requirement"
**Solution**: Native `/sandbox` with domain allowlist

```json
{
  "sandbox": {
    "network": {
      "allowedDomains": [
        "*.npmjs.org",
        "*.pypi.org", 
        "github.com",
        // Add specific domains you need
      ]
    }
  }
}
```

- Curl works for allowlisted domains
- Curl **blocks** for non-allowlisted (attacker.com)
- No prompt needed if domain is allowlisted
- Prompt appears if Claude tries new domain
- You approve once, it's added to allowlist

### "Can't anticipate what Claude will need"
**Solution**: Start permissive, tighten over time

**Phase 1 (Week 1)**: Broad allowlist
```json
{
  "allowedDomains": [
    "*.npmjs.org",
    "*.pypi.org",
    "*.github.com",
    "*.githubusercontent.com",
    "cdn.jsdelivr.net",
    "unpkg.com",
    "cdnjs.cloudflare.com",
    "*.readthedocs.io",
    "*.stackoverflow.com"
  ]
}
```

**Phase 2**: Monitor what's actually used
```bash
# Check sandbox logs
grep "network request" ~/.claude/sandbox.log

# See what domains were allowed
jq '.network.requests' ~/.claude/sandbox.log
```

**Phase 3**: Tighten allowlist based on actual usage

### "Blocks a whole day's work"
**Solution**: Sandbox auto-allow mode prevents this

With native `/sandbox` in auto-allow mode:
- ✅ File operations: No prompts (within working dir)
- ✅ Common commands: No prompts (sandboxed)
- ✅ Allowed domains: No prompts
- ⚠️ New domain: Single prompt, then remembered
- ❌ Outside working dir: Prompt (as it should)

**You only get prompted for things that SHOULD require approval**.

### "Otherwise babysitting and blocking other work"
**Exactly**. That's why native sandbox was created.

From Anthropic's announcement:
> "Traditional permission-based security requires constant user approval... this can lead to approval fatigue... Sandboxing addresses these challenges by defining clear boundaries upfront..."

**The goal IS to let you walk away**.

---

## NETWORK ISOLATION STRATEGIES

### Strategy 1: Allowlist Domains (Recommended)
```json
{
  "sandbox": {
    "network": {
      "mode": "allowlist",
      "allowedDomains": [
        "registry.npmjs.org",
        "pypi.org"
        // Specific domains only
      ]
    }
  }
}
```

**Pros**: Precise control, prevents exfiltration
**Cons**: Need to maintain list

### Strategy 2: Category-Based
```json
{
  "sandbox": {
    "network": {
      "allowCategories": [
        "package-managers",
        "vcs",
        "documentation"
      ]
    }
  }
}
```

**If supported** (check docs). More maintainable.

### Strategy 3: Proxy with Logging
```bash
# Run filtering proxy on localhost:3128
# Configure to log all requests
# Review daily, add to allowlist

# In sandbox config
{
  "sandbox": {
    "network": {
      "proxy": "http://localhost:3128"
    }
  }
}
```

**Pros**: Audit trail, gradual learning
**Cons**: Requires proxy setup

### Strategy 4: Time-Based Allowlist
```json
{
  "sandbox": {
    "network": {
      "allowedDomains": ["*.npmjs.org"],
      "temporaryAllowlist": {
        "*.google.com": "2025-01-07T00:00:00Z"
      }
    }
  }
}
```

**If supported**. Temporary access that auto-expires.

---

## MONITORING REMOTE WORK

### Option 1: tmux + Blink Shell
```bash
# On dev machine
tmux new -s claude-work
claude  # /sandbox enabled
# Detach: Ctrl-b d

# From iPhone via Tailscale
ssh devbox
tmux attach -t claude-work
```

**Pros**: Simple, works now
**Cons**: Terminal-only

### Option 2: Web UI (textcortex solution)
```bash
# On dev machine
claude-sandbox start --web

# From iPhone
# Open https://devbox.tailscale:3377
```

**Pros**: Nice UI, easier on mobile
**Cons**: Requires community tool

### Option 3: Custom Dashboard
```python
# ~/scripts/claude-dashboard.py
from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def status():
    # Read Claude state
    with open('~/.claude/current-task.json') as f:
        task = json.load(f)
    
    return render_template('dashboard.html', 
        task=task['description'],
        progress=task['progress'],
        credits=task['credits_remaining']
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
```

Access via `http://devbox.tailscale:5050` on iPhone

### Option 4: Notifications
```bash
# In hooks configuration
{
  "hooks": {
    "Stop": [{
      "type": "command",
      "command": "curl https://ntfy.sh/your-topic -d 'Claude finished task'"
    }]
  }
}
```

Get push notification on iPhone when done.

---

## FINAL RECOMMENDATION

**Use Native `/sandbox` Mode** with this configuration:

```json
// ~/.claude/settings.json
{
  "sandbox": {
    "enabled": true,
    "autoAllow": true,
    "filesystem": {
      "allowedPaths": ["${workspaceFolder}/**"]
    },
    "network": {
      "allowedDomains": [
        // Package managers - required for installs
        "*.npmjs.org",
        "registry.npmjs.org",
        "*.pypi.org", 
        "pypi.org",
        "files.pythonhosted.org",
        
        // Version control - required for git ops
        "github.com",
        "*.github.com",
        "api.github.com",
        "raw.githubusercontent.com",
        
        // CDNs - common dependencies
        "cdn.jsdelivr.net",
        "unpkg.com",
        "cdnjs.cloudflare.com",
        
        // AI services - for multi-model
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        
        // Docs - likely to curl
        "*.readthedocs.io",
        "docs.python.org",
        "docs.djangoproject.com"
      ],
      "requireConfirmation": false
    }
  },
  "hooks": {
    "Stop": [{
      "type": "command",
      "command": "curl -d 'Task complete' ntfy.sh/claude-work"
    }]
  }
}
```

**Auto-continuation script**:
```bash
#!/bin/bash
# auto-continue.sh

LOG="$HOME/.claude-automation/continue.log"
TASK=$(cat CONTINUATION.md | grep -A 20 "## Next Action" | tail -n +2)

echo "[$(date -Iseconds)] Starting: $TASK" >> "$LOG"

# Run with sandbox (already configured)
claude -p "$TASK" 2>&1 | tee -a "$LOG"

echo "[$(date -Iseconds)] Completed" >> "$LOG"
```

**Cron**:
```cron
0 */5 * * * /home/user/scripts/auto-continue.sh
```

**Why this works**:
- ✅ Sandbox allows curl to approved domains
- ✅ Auto-allow means no prompts within boundaries
- ✅ Still protects against prompt injection (network restricted)
- ✅ Still protects filesystem (working dir only)
- ✅ No Docker overhead
- ✅ Works offline (once packages cached)
- ✅ Notification when done
- ✅ Full autonomy

**This is the approach Anthropic designed for exactly your use case.**

---

*Last Updated: 2025-12-31*
*Based on: Official Anthropic docs, Docker docs, community implementations*
