# Claude Code Optimization Requirements
## Document Version: 2025-12-31

## Primary Objectives

### 1. Maximize Claude Code Credit Efficiency
- **Current Plan**: Pro plan ($20/month)
- **Credits**: 10-40 prompts every 5 hours (~44K tokens per period)
- **Weekly Limits**: 40-80 hours of Sonnet 4 per week
- **Goal**: Minimize wasted credits through intelligent task routing and automation

### 2. Auto-Continuation System
- **Requirement**: Automated work continuation when credits renew (every 5 hours)
- **Trigger**: Cron-based checking (hourly)
- **State Management**: Maintain context across renewal cycles
- **Constraint**: Must handle interruptions gracefully without losing progress

### 3. Remote Access & Monitoring
- **Primary Access**: Mobile (iPhone) via SSH/Tailscale
- **Current Stack**: Tailscale + tmux (basic setup working)
- **Needs**: 
  - Improved mobile UX
  - Status notifications when Claude needs input
  - Dashboard showing: credits remaining, current task, ETA
- **Future Enhancement**: Web-based monitoring interface

### 4. Multi-Model Integration
**Available Resources:**
- **Local GPU**: 48GB VRAM (dual RTX 3090)
- **Gemini API**: "Usually have a lot of credits" (need to verify current limits)
- **Claude Code**: Pro plan credits (primary coordination)

**Integration Goals:**
- Offload token-heavy tasks to local models (Qwen)
- Use Gemini for analysis/review tasks
- Reserve Claude credits for planning/coordination

### 5. Full E2E Testing Capability
- **Requirement**: Sandbox environment with GUI/browser access
- **Use Cases**: 
  - Browser automation testing
  - Full application testing
  - Web scraping validation
- **Constraint**: Must support session persistence for authenticated testing

## Technical Context

### Current Infrastructure
- **OS**: Debian Linux, macOS
- **Development Focus**: 
  - Biodiversity/conservation tech (Antenna, eButterfly)
  - Full-stack development (Django, PostgreSQL)
  - Radio frequency projects (APRS, SDR)
  - AI/ML integration

### Existing Workflows
- Uses CLAUDE.md for persistent context
- Familiar with Docker, tmux, SSH
- Prefers command-line tools
- Values efficiency over comprehensive features

### Development Preferences
- Pseudo-code first exploration
- Type annotations (Python 3.11/3.12)
- CLI interfaces (typer/click)
- Plugins/adapters to existing ecosystems
- Measured, factual documentation (avoid "comprehensive" claims)

## Specific Requirements by Component

### A. Credit Management System
**Must Have:**
- Automated credit availability checking
- State persistence across sessions (CONTINUATION.md, CLAUDE.md, COMPLETED.md)
- Intelligent task prioritization based on credit availability
- Logging with timestamps
- Prevention of duplicate work

**Nice to Have:**
- Predictive credit usage estimation
- Historical usage analytics
- Budget alerts

### B. Local Model Integration (Qwen)
**Hardware:**
- Qwen 2.5 Coder 32B (fits in 48GB VRAM)
- ~10-16 tokens/sec generation speed
- Comparable performance to GPT-4o/Claude Haiku on code tasks

**Integration Options to Evaluate:**
- MCP server wrapper (cleanest)
- Custom subagent definition
- Programmatic tool calling
- Direct Ollama integration
- Qwen agent framework/Cline integration

**Task Offloading Targets:**
- Boilerplate generation
- Code review/analysis
- Documentation generation
- Test generation
- Mechanical refactoring

### C. Gemini Integration
**Current Status (December 2025):**
- Free tier significantly reduced (~20-25 RPD for Flash)
- 2.5 Pro removed from free tier for most users
- **ACTION REQUIRED**: Verify actual quota availability
- 1M token context window (major advantage)

**MCP Integration Options:**
- RLabs-Inc/gemini-mcp (easiest, recommended)
- aliargun/mcp-server-gemini (most features)
- jamubc/gemini-mcp-tool (CLI-based)
- AndrewAltimit's consultation server (auto-trigger)

**Use Cases:**
- Long document analysis (1M context)
- Alternative perspectives on decisions
- Security/code review
- Brainstorming sessions
- Uncertainty resolution

### D. Sandbox Environment
**Requirements:**
- GUI access for browser automation
- Session persistence (authenticated workflows)
- Full environment isolation
- Snapshot/restore capability (optional)
- Local or cloud deployment options

**Options to Research:**
- agent-infra/sandbox (all-in-one Docker)
- Surfkit (Ubuntu desktop environments)
- Docker Sandboxes (new experimental feature)
- Proxmox/QEMU (heavyweight but full isolation)
- Browser-Use with Docker GUI
- E2B cloud sandboxes

**Critical Decision Points:**
- Container vs VM isolation
- Local vs cloud hosting
- VNC vs headless browser approaches
- Resource overhead vs capability tradeoff

### E. Subagent & Hook Utilization
**Recent Claude Code Features:**
- Subagent resumption via agentId
- Background tasks (long-running processes)
- Hooks (auto-trigger on events)
- Checkpoints (state verification)
- Explore subagent (read-only, prevents context bloat)

**Strategy Needs:**
- When to use main agent vs subagents
- How to leverage resumption for 5-hour cycles
- Hook configuration for automated testing
- Background task management

## Research Gaps & Outdated Information

### Critical Research Needed

**1. Gemini API Current Limits (HIGH PRIORITY)**
- Actual RPD/RPM limits for user's account
- Whether user has paid tier or enhanced student access
- Verification of "usually have a lot of credits" claim
- Comparison: free tier vs paid tier economics

**2. Claude Code Latest Features (MEDIUM PRIORITY)**
- Programmatic Tool Calling implementation details
- Tool Search Tool adoption timeline
- Latest subagent capabilities (post-December 2025)
- VSCode extension status (mentioned as beta)
- Docker Sandboxes experimental status

**3. Qwen Integration Methods (MEDIUM PRIORITY)**
- MCP server availability for Ollama/Qwen
- Performance comparison: MCP vs direct integration
- Qwen agent framework compatibility with Claude Code
- Latest Qwen 2.5 Coder benchmarks vs alternatives

**4. Sandbox Solutions (HIGH PRIORITY)**
- agent-infra/sandbox maturity/maintenance status
- Surfkit current state (last update, community)
- Docker Sandboxes experimental feature availability
- E2B pricing for non-free usage
- Playwright/Puppeteer in Docker best practices (2025)

**5. Remote Monitoring Solutions (LOW PRIORITY)**
- Webhook/notification services for credit renewal
- Dashboard frameworks (lightweight options)
- Blink Shell current pricing/features
- Mosh stability on current network configurations

### Information Known to be Outdated

**From Search Results:**
- Many articles reference Gemini 2.5 Pro free tier (removed Dec 2025)
- Some guides show 250 RPD for Flash (now ~20-25)
- Claude Code plugin architecture may have changed
- Rate limit enforcement stricter than older docs suggest
- Some MCP servers may be unmaintained

**From User's Previous Chat (Jan 1, 2025):**
- Core automation concepts remain valid
- Remote access recommendations (tmux, Blink, Mosh) still current
- CLAUDE.md strategy confirmed by recent best practices
- Multiple parallel instances approach validated

## Success Criteria

### Minimum Viable System
1. Automated credit checking runs hourly
2. CONTINUATION.md successfully maintains state across 5-hour cycles
3. At least one alternative model (Qwen OR Gemini) accessible via MCP
4. Basic remote monitoring (SSH + tmux improvements)
5. Task routing logic: high-value → Claude, token-heavy → alternatives

### Optimal System
1. All three models integrated (Claude + Qwen + Gemini)
2. Intelligent task routing based on:
   - Credit availability
   - Task characteristics (token count, complexity, type)
   - Model strengths
3. Subagent resumption working across credit cycles
4. Sandbox environment for E2E testing
5. Push notifications for human intervention needs
6. Web dashboard for status monitoring
7. Background tasks persist through credit renewal
8. Hooks trigger automated testing after code changes

## Constraints & Preferences

### Hard Constraints
- Must work within Pro plan limits (no budget for higher tiers)
- Local GPU limited to 48GB VRAM
- Mobile access must remain functional (iPhone primary)
- Cannot violate API terms of service (no quota circumvention)

### Soft Preferences
- Prefer open-source solutions
- Favor plugins/adapters over standalone tools
- Command-line first, GUI optional
- Documentation should be factual, not marketing-speak
- Start simple, iterate based on proven value
- Avoid premature "comprehensive" solutions

## Open Questions

1. What is the actual current Gemini quota for the user's account?
2. Which Qwen integration method offers best performance/reliability?
3. Is Docker Sandboxes feature available yet or still experimental?
4. What is the optimal credit threshold for triggering continuation?
5. Should continuation run automatically or require manual approval?
6. How to handle conflicts when multiple models disagree?
7. What's the backup strategy if Gemini quota runs out?
8. Is local Qwen performance sufficient for all offload tasks?
9. Should sandbox run locally (GPU machine) or cloud (E2B)?
10. What metrics should be tracked for optimization feedback?

## Next Steps for Requirements Validation

1. **Test Gemini API**: Make requests to verify actual quota
2. **Benchmark Qwen local**: Measure tokens/sec, quality on typical tasks
3. **Prototype credit checker**: Validate `claude /status` parsing
4. **Test subagent resume**: Verify agentId persistence works as documented
5. **Evaluate sandbox options**: Hands-on testing of 2-3 top candidates
6. **Map task types**: Categorize typical work for routing decisions
7. **Design state schema**: Define CONTINUATION.md structure
8. **Create monitoring prototype**: Basic status display before full dashboard
