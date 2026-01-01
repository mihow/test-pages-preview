# Credit Monitoring & Auto-Resume

**Status:** Planning
**Priority:** High
**Estimated Effort:** 4-6 hours

## Problem

Claude Code Pro has limited credits (10-40 prompts per 5-hour window). Currently:
- ❌ No visibility into credit usage
- ❌ No tracking of when credits renew
- ❌ Orchestrator doesn't know when to pause/resume
- ❌ Agent might fail mid-task when credits run out

**Goal:** Monitor credit usage, pause when exhausted, auto-resume on renewal.

## Claude CLI Output Format

Claude CLI provides JSON output that includes usage information:

```bash
# Get Claude status/usage
claude --json

# Expected output format (need to verify):
{
  "credits": {
    "remaining": 15,
    "total": 40,
    "renews_at": "2026-01-01T19:00:00Z"
  },
  "usage": {
    "this_window": 25,
    "tokens_input": 150000,
    "tokens_output": 50000
  }
}
```

**TODO:** Verify actual JSON structure by running `claude --json` or checking docs.

## Requirements

### Must Have
1. **Credit Tracking**
   - Query Claude credits before/after each task
   - Store credit history in state
   - Track renewal times

2. **Pause on Exhaustion**
   - Stop when credits < threshold (e.g., 5)
   - Mark current project as "Paused (Low Credits)"
   - Don't start new work

3. **Auto-Resume**
   - Check credits every hour (configurable)
   - When credits renewed, resume highest priority work
   - Update Sheet status

4. **Visibility**
   - Show credits in status command
   - Log credit usage per project
   - Warn when credits getting low

### Nice to Have
- Credit usage prediction (estimate remaining time)
- Per-project credit tracking
- Credit budget limits per project
- Dashboard credit meter
- Notifications when credits low/renewed

## Architecture

### New Module: `src/credits.py`

```python
class CreditMonitor:
    """Monitors Claude Code credit usage and renewal."""

    def __init__(self, config: Config, state: StateTracker):
        self.config = config
        self.state = state
        self.last_check = None
        self.credits_remaining = None
        self.renews_at = None

    def check_credits(self) -> dict:
        """Query current credit status from Claude CLI."""
        # Run: claude --json
        # Parse output
        # Update internal state
        # Return: {remaining, total, renews_at}

    def can_start_work(self) -> bool:
        """Check if enough credits to start work."""
        return self.credits_remaining > self.config.credit_threshold

    def should_check_renewal(self) -> bool:
        """Check if it's time to query credit renewal."""
        # Check every hour, or if renews_at is past

    def wait_for_renewal(self) -> datetime:
        """Calculate when to check credits again."""
        # If exhausted, return renews_at
        # Otherwise, return now + check_interval

    def record_usage(self, project: Project, credits_used: int):
        """Record credit usage for a project."""
        # Store in state
        # Update Sheet if configured
```

### Updated: `src/daemon.py`

```python
class CTOSidekick:
    def __init__(self, config: Config):
        # ... existing ...
        self.credits = CreditMonitor(config, self.state)

    def _iteration(self):
        """Main loop iteration."""

        # 1. Check if time to query credits
        if self.credits.should_check_renewal():
            credit_status = self.credits.check_credits()
            logger.info(f"Credits: {credit_status['remaining']}/{credit_status['total']}")

        # 2. Check if can start work
        if not self.credits.can_start_work():
            logger.info("Credits exhausted, waiting for renewal...")
            next_check = self.credits.wait_for_renewal()
            # Sleep until renewal time
            return

        # 3. Proceed with normal flow if credits available
        # ... existing selection and start logic ...
```

### Updated: `src/state.py`

Add credit tracking to state:

```python
def record_credit_usage(self, project: Project, credits_before: int, credits_after: int):
    """Record credit usage for a task."""
    usage = credits_before - credits_after

    if "credit_history" not in self.state:
        self.state["credit_history"] = []

    self.state["credit_history"].append({
        "project": project.name,
        "credits_used": usage,
        "timestamp": datetime.now().isoformat()
    })

    # Also add to project summary
    if "project_credits" not in self.state:
        self.state["project_credits"] = {}

    if project.name not in self.state["project_credits"]:
        self.state["project_credits"][project.name] = 0

    self.state["project_credits"][project.name] += usage

    self._save_state()
```

### Updated: `config.yaml`

```yaml
# Credit monitoring
credits:
  enabled: true
  threshold: 5           # Minimum credits before pausing
  check_interval: 3600   # Check every hour (seconds)
  auto_resume: true      # Resume when credits renew
```

## Implementation Plan

### Phase 1: Credit Querying (2 hours)
**Tasks:**
1. [ ] Research Claude CLI JSON output format
   - Run `claude --help` to find credit status command
   - Run command and capture actual JSON structure
   - Document format in this file

2. [ ] Create `src/credits.py` module
   - `CreditMonitor` class
   - `check_credits()` method
   - Parse JSON output
   - Handle errors (no output, invalid JSON)

3. [ ] Write tests
   - Mock subprocess output
   - Test JSON parsing
   - Test error handling

4. [ ] Integrate with daemon
   - Add credit check before starting work
   - Log credit status
   - Don't modify behavior yet (just monitoring)

### Phase 2: Pause on Exhaustion (1 hour)
**Tasks:**
1. [ ] Implement `can_start_work()` logic
   - Check threshold
   - Return boolean

2. [ ] Update daemon loop
   - Skip work if credits low
   - Log pause reason
   - Update project status

3. [ ] Add Sheet status update
   - New status: "Paused (Low Credits)"
   - Or just "Paused" with details

4. [ ] Test pause behavior
   - Mock low credits
   - Verify work stops
   - Verify status updates

### Phase 3: Auto-Resume (1-2 hours)
**Tasks:**
1. [ ] Implement renewal detection
   - Parse `renews_at` timestamp
   - Calculate when to check again
   - `should_check_renewal()` method

2. [ ] Update daemon sleep logic
   - Don't sleep full `sync_interval` if waiting for credits
   - Sleep until `renews_at` or next check time
   - Check credits on wake

3. [ ] Implement resume logic
   - Query credits after wake
   - If renewed, resume paused work
   - Or start new highest priority

4. [ ] Test auto-resume
   - Mock credit renewal
   - Verify work resumes
   - Verify timing logic

### Phase 4: Tracking & Visibility (1 hour)
**Tasks:**
1. [ ] Add credit tracking to state
   - `record_credit_usage()` method
   - Store per-project totals
   - Store history

2. [ ] Update status command
   - Show current credits
   - Show renewal time
   - Show per-project usage

3. [ ] Add config options
   - Threshold, check interval, auto-resume

4. [ ] Documentation
   - Update QUICKSTART.md
   - Add CREDITS.md guide
   - Update status.py help text

## Testing Strategy

### Unit Tests: `tests/test_credits.py`
```python
def test_parse_claude_json():
    """Test parsing Claude --json output."""
    # Mock JSON response
    # Verify parsing
    # Test various formats

def test_can_start_work():
    """Test threshold logic."""
    # Above threshold → True
    # Below threshold → False
    # Exactly at threshold → ?

def test_should_check_renewal():
    """Test renewal check timing."""
    # Last check >1 hour ago → True
    # Last check recent → False
    # renews_at passed → True
```

### Integration Tests: `tests/test_credit_integration.py`
```python
def test_pause_on_exhaustion():
    """Test that daemon pauses when credits low."""
    # Mock low credits
    # Run iteration
    # Verify no work started
    # Verify status updated

def test_resume_on_renewal():
    """Test auto-resume when credits renewed."""
    # Mock exhausted credits
    # Pause work
    # Mock credit renewal
    # Verify work resumes
```

### Mock Implementation: Update `src/mocks.py`
```python
class MockCreditMonitor(CreditMonitor):
    """Mock credit monitor for testing."""

    def __init__(self):
        self.mock_credits = 40
        self.mock_renews_at = None

    def check_credits(self):
        return {
            "remaining": self.mock_credits,
            "total": 40,
            "renews_at": self.mock_renews_at
        }

    def set_credits(self, remaining: int):
        """Set mock credit level for tests."""
        self.mock_credits = remaining
```

## Open Questions

### 1. Claude CLI JSON Format
**Question:** What's the actual format of `claude --json` output?

**Action:** Run these commands and document:
```bash
claude --help | grep -i json
claude --help | grep -i credit
claude --help | grep -i status

# Try these:
claude --json
claude status --json
claude credits --json
```

**Expected fields:**
- `credits.remaining` - How many credits left
- `credits.total` - Total for this window
- `credits.renews_at` - ISO timestamp when renews
- `usage.tokens_*` - Token usage (optional)

### 2. Credit Check Frequency
**Question:** How often should we query credits?

**Options:**
- Before each task (more accurate, more API calls)
- Every hour (less overhead, might miss renewal)
- Adaptive (check often when low, rarely when high)

**Recommendation:** Start with hourly, add adaptive later.

### 3. Pause vs Stop
**Question:** When credits run out, should we:
- A) Pause current work (mark as "Paused", resume later)
- B) Stop current work (mark as "Pending", restart from scratch)

**Recommendation:** Pause (A) - preserves progress, can resume.

### 4. Threshold Value
**Question:** What credit threshold to use?

**Options:**
- 5 credits (conservative, ensures completion)
- 10 credits (very safe)
- 0 credits (wait until exhausted)

**Recommendation:** 5 (configurable)

### 5. Multi-Window Tracking
**Question:** Track credits across multiple 5-hour windows?

**Implementation:**
- Store window ID (hash of renews_at?)
- Track usage per window
- Show daily/weekly stats

**Priority:** Nice to have, not MVP

## Dependencies

### Python Packages
None (use stdlib subprocess, json)

### External
- Claude CLI must be installed
- Claude must support JSON output (verify!)

### Configuration
Add to `config.yaml`:
```yaml
credits:
  enabled: true
  threshold: 5
  check_interval: 3600
  auto_resume: true
```

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Claude CLI doesn't have JSON output | High | Use text parsing, or API if available |
| Credit info not in output | High | Alternative: parse from UI, or manual config |
| Renewal time incorrect | Medium | Add manual override in config |
| Check too frequent (rate limit) | Low | Cache results, minimum 10min between checks |
| Clock skew on renews_at | Low | Add buffer time (check 5min before renewal) |

## Success Criteria

- [ ] Credit status displayed in `./run.sh status`
- [ ] Daemon pauses when credits < threshold
- [ ] Daemon auto-resumes when credits renew
- [ ] Credit usage tracked per project
- [ ] Tests cover all pause/resume scenarios
- [ ] Documentation explains credit monitoring
- [ ] Works both with and without credits available

## Future Enhancements

- Credit budget per project
- Predictive credit usage
- Cost tracking (if pricing known)
- Daily/weekly usage reports
- Credit alerts via notifications
- Dashboard credit meter
- Multi-model credit tracking (Gemini, etc.)

## References

- Claude Code Pro limits: 10-40 prompts/5hrs
- See: [../cto-sidekick-plan.md](../cto-sidekick-plan.md) for context
- Related: Multi-model routing (can fall back to Qwen when Claude credits low)

---

**Next Steps:**
1. Research Claude CLI JSON format
2. Create `src/credits.py`
3. Write tests
4. Integrate with daemon
