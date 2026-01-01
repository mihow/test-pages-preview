# Meta Agent Planning

This directory contains planning docs and task tracking for the CTO Sidekick meta agent implementation.

## Structure

```
meta-agent/
├── README.md              # This file
├── TODO.md                # Active todo list (priority ordered)
├── DONE.md                # Completed tasks archive
├── features/              # Feature planning docs
│   ├── credit-monitoring.md
│   ├── multi-model-routing.md
│   ├── vm-isolation.md
│   └── dashboard.md
└── decisions/             # Architecture decision records
    └── 001-tmux-sessions.md
```

## Quick Links

- **Active Work:** [TODO.md](TODO.md)
- **Next Feature:** [Credit Monitoring](features/credit-monitoring.md)
- **Completed:** [DONE.md](DONE.md)

## Process

1. **New Feature:** Create planning doc in `features/`
2. **Add Tasks:** Break down into tasks in `TODO.md`
3. **Implement:** Work through tasks
4. **Archive:** Move completed tasks to `DONE.md`
5. **Document:** Record decisions in `decisions/`

## Current Status

**Phase:** MVP Complete ✅

**Active Feature:** Credit Monitoring

**Next Up:**
- Credit/usage monitoring
- Auto-resume on credit renewal
- Multi-model routing (Qwen, Gemini)
