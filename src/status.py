#!/usr/bin/env python3
"""Quick status check for CTO Sidekick."""

import json
import sys
from pathlib import Path
from datetime import datetime

from src.config import Config


def format_timestamp(ts_str: str | None) -> str:
    """Format ISO timestamp to human readable."""
    if not ts_str:
        return "Never"

    try:
        ts = datetime.fromisoformat(ts_str)
        now = datetime.now()
        delta = now - ts

        if delta.seconds < 60:
            return f"{delta.seconds}s ago"
        elif delta.seconds < 3600:
            return f"{delta.seconds // 60}m ago"
        elif delta.days == 0:
            return f"{delta.seconds // 3600}h ago"
        else:
            return f"{delta.days}d ago"
    except (ValueError, TypeError):
        return ts_str


def main():
    """Display current orchestrator status."""
    try:
        config = Config("config.yaml")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    state_file = config.state_file

    if not state_file.exists():
        print("❌ Orchestrator not yet started (no state file)")
        sys.exit(1)

    with open(state_file) as f:
        state = json.load(f)

    print("=" * 60)
    print("CTO Sidekick Status")
    print("=" * 60)

    # Last update
    last_update = state.get("last_update")
    print(f"\nLast Update: {format_timestamp(last_update)}")

    # Active project
    active = state.get("active_project")
    if active:
        print(f"\n🔵 Active Project:")
        print(f"   Name: {active.get('name')}")
        print(f"   Priority: {active.get('priority')}")
        print(f"   Started: {format_timestamp(active.get('started_at'))}")
    else:
        print(f"\n⚪ Status: Idle")

    # Recent history
    history = state.get("history", [])
    if history:
        print(f"\n📋 Recent Events:")
        for event in history[-5:]:
            ts = format_timestamp(event.get('timestamp'))
            msg = event.get('message', '')
            event_type = event.get('type', '')
            icon = {"start": "▶️ ", "completion": "✅", "error": "❌"}.get(event_type, "  ")
            print(f"   {icon} {ts}: {msg}")

    # Completed projects
    completed = state.get("completed_projects", [])
    if completed:
        print(f"\n✅ Recently Completed: {len(completed)} projects")
        for comp in completed[-3:]:
            name = comp.get('name')
            success = "✅" if comp.get('success') else "❌"
            print(f"   {success} {name}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
