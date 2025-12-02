#!/usr/bin/env python3
"""
Janusz GUI Launcher Script

Simple launcher for the Janusz GUI application.
Run with: python scripts/gui.py
"""

import sys
from pathlib import Path

# Add src to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from janusz.gui.main_app import main
    main()
except ImportError as e:
    print(f"❌ Error importing GUI: {e}")
    print("Make sure all dependencies are installed:")
    print("  uv sync --all-extras")
    print("  # or")
    print("  pip install -e .[gui]")
    sys.exit(1)
