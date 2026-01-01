# Meta Agent Notes - Claude Project Description

## Quick Start (MVP is Ready!)

**Want to get the orchestrator running now?**

```bash
# Install dependencies
uv pip install -e .

# Copy and configure
cp config.yaml.example config.yaml
nano config.yaml  # Set up your projects and credentials

# Test setup
python src/test_basic.py

# Run orchestrator
python src/daemon.py
```

See **[SETUP.md](SETUP.md)** for detailed instructions including Google Sheets setup.

**What's Working:**
- ✅ Google Sheets integration for priorities
- ✅ Auto-start Claude Code on highest priority project
- ✅ **Runs Claude in tmux sessions** - attach to watch in real-time!
- ✅ Status updates back to Sheet
- ✅ Sequential project execution
- ✅ State tracking and history
- ✅ **Comprehensive test suite** (13 tests, all passing)

**What's Next:**
- Multi-model routing (Claude → Qwen → Gemini)
- VM isolation (per the plan below)
- Web dashboard
- Credit monitoring and auto-resume

---

## Purpose

This project is a knowledge base and active workspace for designing, implementing, and refining autonomous AI agent systems for real-world software development. It documents practical patterns, architectural decisions, and operational strategies for running multiple AI coding agents (Claude Code, local Qwen, Gemini) across diverse projects simultaneously.

## Context

Mike is a senior development manager working on multiple technology projects spanning biodiversity/conservation tech (Antenna, eButterfly), radio/SDR tools (APRS), voice assistants (Pipecat), and general software development. The goal is to build a "CTO Sidekick" - an orchestration system that manages autonomous development across these projects while optimizing for:

- **Multi-project context isolation** - Each project needs independent environments that can be paused/resumed
- **Intelligent resource allocation** - Route tasks to appropriate models (Claude for complex work, local Qwen for implementation, Gemini for review)
- **Credit optimization** - Maximize Claude Code Pro plan credits (10-40 prompts/5hrs, 40-80hrs Sonnet 4/week)
- **True autonomy** - Agents work unattended with minimal babysitting, auto-resume on 5-hour credit renewal
- **Remote monitoring** - Track progress via mobile/web dashboard accessible through Tailscale
- **Cost efficiency** - Leverage local hardware (2x RTX 3090, 48GB VRAM) for Qwen inference and other local models

## Technical Infrastructure

**Current Setup:**
- Development machines: Debian Linux, macOS
- GPU resources: 2x RTX 3090 (48GB VRAM total)
- Network: Tailscale for secure remote access
- Preferred stack: Python 3.11/3.12, PostgreSQL, Docker/VMs, Flask/FastAPI

**Hardware Capabilities:**
- Can run Qwen 2.5 Coder 32B locally (10-16 tokens/sec)
- Whisper for speech-to-text
- Potential for GPU passthrough to VMs

## Agent Infrastructure Approaches (All Under Consideration)

### Approach 1: VM Pool (Strong Preference)
- Each project gets dedicated VM (QEMU/KVM/Proxmox)
- Clone from Ubuntu dev template
- Dedicated Qwen GPU VM with passthrough (both RTX 3090s)
- Project VMs call Qwen via network (MCP server or API)
- Full isolation, snapshot/rollback capability
- Best for: Sensitive data (biodiversity work), complete separation

### Approach 2: Single Shared VM
- One larger VM running all projects in separate Docker containers
- GPU passthrough to single VM
- Simpler than VM pool, still good isolation
- Container orchestration via docker-compose or k3s
- Best for: Simpler management, less resource overhead

### Approach 3: Docker Sandboxes (Official or Community)
- Official Docker Sandboxes (recent Docker Desktop integration)
- Community solutions: textcortex/claude-code-sandbox (has web monitoring UI)
- Z7Lab/claude-code-sandbox (simpler script-based approach)
- Run directly on host or inside single VM
- Best for: Quick setup, official support, web monitoring interface

### Approach 4: Native Claude Code `/sandbox` Mode
- Built-in OS-level sandboxing (bubblewrap on Linux, seatbelt on macOS)
- Network allowlist for curl/npm/pip access
- 84% reduction in permission prompts
- Auto-allow mode for true autonomy
- Best for: Lightest weight, no containers/VMs needed, proven by Anthropic

### Approach 5: Hybrid Architecture
- Native sandbox for most work
- Docker containers for risky/experimental tasks
- Optional VM for highly sensitive projects
- Qwen runs wherever GPU is (bare metal, VM, or container)
- Best for: Flexibility, optimize per-project needs

**Current Stance:** Exploring all options. VM approach appeals for isolation and GPU management, but Docker sandboxes offer simplicity and the native sandbox mode is proving very capable. Decision will be based on practical testing and real-world performance.

## Core Projects & Priorities

Projects are tracked in Google Sheets with priorities, deadlines, and status. Current active projects include:

- **Antenna**: Django-based ML pipeline for insect image classification (biodiversity conservation)
- **eButterfly**: Species observation data export and analysis tools
- **APRS Tools**: Audio processing and decoding for amateur radio
- **Pipecat Voice Assistant**: Real-time voice interaction system
- Multiple other tools and utilities across different domains

Each project may require different compute resources (GPU/CPU), models (Claude/Qwen/Gemini), and isolation levels.

## Key Components Being Designed

### 1. CTO Sidekick Orchestration Service
**Purpose:** System daemon that manages agent lifecycle, resource allocation, and task prioritization

**Features:**
- Reads priorities from Google Sheets
- Spawns/manages agents in VMs or containers
- Routes tasks to optimal model based on complexity and available resources
- Monitors Claude credit status, auto-resumes on 5-hour renewal
- Updates project status back to Google Sheets
- Web dashboard for mobile monitoring
- Push notifications (ntfy.sh) for important events

**Tech Stack:** Python systemd daemon, PostgreSQL/SQLite, libvirt (for VMs) or Docker, Google Sheets API, Flask/FastAPI dashboard

### 2. Research Monitoring Agent
**Purpose:** Continuously track Claude Code ecosystem developments (new features, techniques, tools, best practices)

**Features:**
- Monitor 37+ sources: Anthropic blog, Reddit, GitHub, community blogs, thought leaders
- Daily checks for critical updates (security, new features)
- Weekly digests of new techniques and tools
- Monthly trend analysis
- Uses local Qwen for filtering/analysis (cheap), Claude for weekly synthesis
- Delivers actionable intelligence via Notion + notifications

**Tech Stack:** RSS aggregation, GitHub/Reddit APIs, web scraping, Qwen + instructor (structured extraction), Notion integration

### 3. Multi-Model Task Router
**Purpose:** Intelligently route work to the right model/infrastructure

**Routing Logic:**
- **Planning/Architecture** → Claude (if credits >5) or Gemini
- **Implementation/Testing** → Local Qwen (free, fast)
- **GPU-required tasks** → Qwen on GPU VM
- **Code Review** → Gemini (fresh eyes)
- **Documentation** → Qwen (good enough, free)
- **Critical bugs** → Claude (best quality)

### 4. State Management System
**Purpose:** Preserve context across credit cycles and project switches

**Implementation:**
- `CONTINUATION.md` per project (current task, progress, blockers, next action)
- PostgreSQL tracking: project status, agent assignments, resource usage
- Git checkpoints before/after agent runs
- Google Sheets integration for human-readable status

## Security & Permission Strategy

**The Reality:** Autonomous agents need network access (curl, npm, pip) and can't have manual permission prompts every 30 seconds - that defeats the purpose.

**Explored Solutions:**

1. **Native `/sandbox` mode** - OS-level isolation with network domain allowlist
   - Allow npm, pip, github, docs sites
   - Block random domains (prevents prompt injection exfiltration)
   - Auto-approve within boundaries, prompt for new domains
   
2. **Docker with `--dangerously-skip-permissions`** - Safe because containerized
   - Network isolation via Docker networking
   - Filesystem restricted to mounted project
   - Can run truly autonomous with YOLO mode
   
3. **VM isolation** - Maximum security for sensitive work
   - Separate kernel, complete isolation
   - Network firewall rules per VM
   - Snapshot before risky operations

4. **Granular `allowedTools` configuration** - Whitelist specific safe operations
   - Allow Read, Write (scoped), Edit, git commands, test runners
   - Deny rm, sudo, unchecked network commands
   - Still requires some prompts but far fewer

**Current approach:** Testing all methods, likely hybrid based on project sensitivity.

## Real-World Constraints & Lessons

**Key Insights from Research:**
- Babysitting agents defeats their purpose - autonomy is essential
- `--dangerously-skip-permissions` is genuinely dangerous BUT necessary for true autonomy (use with isolation)
- Claude Code's native sandbox mode (Nov 2025) reduces prompts by 84% while maintaining security
- Prompt injection is real - network isolation is critical even with domain allowlists
- Community consensus: Never use YOLO mode without containerization OR native sandbox with network controls
- Multi-model pipelines reduce costs - not everything needs expensive Claude Sonnet 4
- 5-hour credit cycles require automated continuation strategies
- GPU passthrough works well for local model inference in VMs

**Cost Optimization Findings:**
- Claude Code Pro: $20/month, 10-40 prompts/5hrs (varies by load)
- Gemini 2.5 Flash: Drastically reduced free tier (~20-25 requests/day, down from 250)
- Qwen 2.5 Coder 32B: Competitive with GPT-4o on benchmarks, runs locally (free)
- Strategy: Use Claude for planning/complex work, Qwen for implementation, Gemini for review

## Tools & Techniques Under Investigation

**Claude Code Features:**
- Sandbox mode (`/sandbox` command) - New Nov 2025
- Subagent API - Resume work across sessions with agentId
- Hooks - Auto-trigger tests/linting after code changes
- Skills - Modular capabilities vs full subagents
- Programmatic Tool Calling - Execute workflows in code sandbox
- Tool Search Tool - Load tools on-demand (saves 55K-134K tokens)
- Background tasks - Keep dev servers running between sessions
- Ultrathink keyword - 31,999 token thinking budget

**MCP (Model Context Protocol) Servers:**
- Gemini MCP (RLabs, aliargun, jamubc implementations)
- Ollama MCP (for local Qwen access from Claude)
- Filesystem, Puppeteer, GitHub, database connectors
- Custom MCP servers for project-specific APIs

**Sandbox Solutions:**
- Native Claude sandbox (bubblewrap/seatbelt)
- Docker Sandboxes (official Docker integration)
- textcortex/claude-code-sandbox (community, has web UI)
- Z7Lab/claude-code-sandbox (simpler script approach)
- E2B cloud sandboxes
- agent-infra/sandbox (Docker all-in-one)

**Development Patterns:**
- CONTINUATION.md pattern (state preservation)
- PIV Loop (Plan → Implement → Verify)
- Progressive Trust Model (start restrictive, expand gradually)
- Git worktrees for parallel agent instances
- Checkpointing before autonomous runs
- Dual agent review (one writes, one reviews)

## Documentation & Knowledge Resources

This project maintains comprehensive documentation on:
- **Security analysis** - `--dangerously-skip-permissions` risks, mitigations, community approaches
- **Sandbox comparisons** - Native sandbox vs Docker vs VMs vs QEMU, pros/cons for each
- **Implementation plans** - CTO Sidekick architecture, Research Agent design
- **Best practices** - From CLAUDE.md template, community wisdom, official Anthropic guidance
- **Resource monitoring lists** - 37+ sources to track for ecosystem developments
- **Configuration examples** - allowedTools, sandbox settings, hook configurations

**Key Reference Documents:**
- Research requirements analysis (10 open questions, success criteria)
- Three-tier implementation approaches (MVP, Balanced, Maximum)
- Critical unknowns requiring investigation
- Real-world incident reports and lessons learned
- Cost/benefit analysis of different architectures

## Communication Style & Preferences

**Writing Philosophy:**
- Measured, factual tone
- Avoid exaggeration ("comprehensive", "production-ready" unless objectively true)
- Describe actual changes rather than broad claims
- Minimize lists, emojis, em-dashes when they clutter
- Use sentences over lists when clearer
- Purpose pseudocode first before real code
- Start small, ask questions, avoid premature "comprehensiveness"

**Development Approach:**
- Research first (check docs, verify versions, look for deprecations)
- Think holistically (purpose, root cause, not symptoms)
- Cost optimization (minimize API calls, maximize efficiency)
- Prove it works (tests first when possible)
- Start simple (MVP first, iterate)
- Document decisions (maintain learnings in docs/claude/)

## Current Status & Next Steps

**In Progress:**
- Evaluating sandbox approaches through practical testing
- Designing CTO Sidekick architecture (VM vs Docker vs hybrid)
- Planning Research Monitoring Agent implementation
- Investigating Qwen MCP server options
- Testing Claude Code latest features (sandbox mode, subagents)

**Decision Points:**
- VM pool vs single VM vs Docker vs native sandbox (or hybrid)
- Google Sheets vs GitHub Projects for task tracking (leaning Sheets)
- Qwen deployment strategy (bare metal, VM with GPU passthrough, container)
- Research agent complexity (RSS-only vs full API integration)

**Immediate Actions:**
- Set up test environments for each sandbox approach
- Benchmark local Qwen performance
- Verify actual Gemini API quotas
- Parse `claude /status` output format
- Create Ubuntu dev VM template

## Project Goals

1. **Build working CTO Sidekick** that manages autonomous development across 3-5 active projects simultaneously
2. **Optimize Claude Code Pro credits** through intelligent multi-model routing and automated continuation
3. **Enable true autonomy** - work continues while you're away, minimal babysitting required
4. **Maintain security** - especially for biodiversity/conservation data
5. **Stay current** - automated research monitoring keeps techniques up-to-date
6. **Remote visibility** - check progress from anywhere (mobile-friendly)
7. **Document learnings** - build reusable patterns for the community

## Success Metrics

The system works when:
- Can manage 3+ projects simultaneously in isolation
- Agents resume automatically on credit renewal (5-hour cycles)
- <5 manual interventions per day required
- Claude credits last full week (40-80 hours Sonnet 4)
- Local Qwen handles 60%+ of implementation work
- Progress visible from iPhone via Tailscale
- New techniques applied within 1 week of discovery
- Total cost <$50/month (Claude $20 + minimal API usage)

## Why This Matters

This isn't just about automating development - it's about **amplifying a senior developer's leverage** across multiple important projects (biodiversity conservation, amateur radio tools, voice AI) that wouldn't get adequate attention otherwise. The autonomous agent orchestration system enables one person to maintain forward progress on diverse technical initiatives that would normally require a small team.

The learnings and patterns documented here contribute back to the broader community of developers exploring autonomous AI agents for real-world software development.

---

**Project Type:** Documentation, Architecture, Experimentation, Knowledge Base
**Maintainer:** Mike (with Claude as research and design partner)
**Status:** Active development and continuous learning
**Visibility:** Private (contains strategy and architecture decisions)
