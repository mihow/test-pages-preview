#!/usr/bin/env python3
"""Basic test to verify setup without Google Sheets."""

import sys
from pathlib import Path

print("CTO Sidekick - Basic Setup Test")
print("=" * 50)

# Test 1: Check Python version
print("\n1. Python Version:")
version = sys.version_info
if version >= (3, 10):
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
else:
    print(f"   ❌ Python {version.major}.{version.minor} (need 3.10+)")
    sys.exit(1)

# Test 2: Check dependencies
print("\n2. Dependencies:")
deps = {
    "gspread": "Google Sheets integration",
    "oauth2client": "Google OAuth",
    "yaml": "Config parsing",
    "psutil": "Process monitoring"
}

all_deps_ok = True
for module, desc in deps.items():
    try:
        __import__(module)
        print(f"   ✅ {module:15} ({desc})")
    except ImportError:
        print(f"   ❌ {module:15} ({desc}) - MISSING")
        all_deps_ok = False

if not all_deps_ok:
    print("\n   Install missing dependencies:")
    print("   uv pip install -e .")
    sys.exit(1)

# Test 3: Check config
print("\n3. Configuration:")
config_file = Path("config.yaml")
if config_file.exists():
    print(f"   ✅ config.yaml exists")

    # Try loading it
    try:
        from config import Config
        config = Config()
        print(f"   ✅ Config loads successfully")
        print(f"      Spreadsheet: {config.sheets_spreadsheet_name}")
        print(f"      Projects: {len(config.project_dirs)} configured")
    except Exception as e:
        print(f"   ⚠️  Config has errors: {e}")
else:
    print(f"   ⚠️  config.yaml not found")
    print(f"      Copy config.yaml.example to config.yaml")

# Test 4: Check credentials
print("\n4. Google Sheets Credentials:")
if config_file.exists():
    try:
        from config import Config
        config = Config()
        creds_file = config.sheets_credentials
        if creds_file.exists():
            print(f"   ✅ Credentials file exists: {creds_file}")
        else:
            print(f"   ⚠️  Credentials not found: {creds_file}")
            print(f"      See SETUP.md for instructions")
    except Exception as e:
        print(f"   ⚠️  Could not check credentials: {e}")
else:
    print("   ⚠️  Skipped (no config)")

# Test 5: Check Claude
print("\n5. Claude Code:")
import shutil
if shutil.which("claude"):
    print(f"   ✅ claude command found")
else:
    print(f"   ⚠️  claude command not found")
    print(f"      Install: npm install -g @anthropic/claude-code")

print("\n" + "=" * 50)
print("Basic setup test complete!")
print("\nNext steps:")
print("1. Copy config.yaml.example to config.yaml")
print("2. Set up Google Sheets (see SETUP.md)")
print("3. Run: python src/daemon.py")
