#!/usr/bin/env python3
"""
TOON CLI Validation Module for AI Agent Knowledge Bases

This module provides validation and safety checks for the external TOON CLI tool.
Ensures the TOON binary is available, functional, and meets minimum requirements.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ToonCliError(Exception):
    """Exception raised when TOON CLI validation or execution fails."""
    pass


def find_toon_executable() -> Optional[str]:
    """
    Find the TOON CLI executable in PATH.

    Returns:
        Path to toon executable if found, None otherwise.
    """
    # Check if JANUSZ_TOON_PATH environment variable is set
    custom_path = os.environ.get("JANUSZ_TOON_PATH")
    if custom_path:
        toon_path = Path(custom_path)
        if toon_path.exists() and toon_path.is_file():
            return str(toon_path)
        logger.warning(f"JANUSZ_TOON_PATH set but file not found: {custom_path}")

    # Use shutil.which to find in PATH
    import shutil
    toon_path = shutil.which("toon")
    return toon_path


def validate_toon_cli_version() -> str:
    """
    Validate TOON CLI version and functionality.

    Returns:
        Version string if validation successful.

    Raises:
        ToonCliError: If validation fails.
    """
    toon_path = find_toon_executable()
    if not toon_path:
        raise ToonCliError(
            "TOON CLI not found in PATH. "
            "Please install via 'cargo install toon' or use scripts/toon.sh"
        )

    try:
        # Test basic functionality with --version
        result = subprocess.run(
            [toon_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,  # 10 second timeout
            check=True
        )

        version = result.stdout.strip()
        if not version:
            raise ToonCliError("TOON CLI --version returned empty output")

        logger.debug(f"TOON CLI version: {version}")
        return version

    except subprocess.TimeoutExpired as e:
        raise ToonCliError("TOON CLI --version timed out (10s)") from e
    except subprocess.CalledProcessError as e:
        raise ToonCliError(f"TOON CLI --version failed: {e.stderr}") from e
    except FileNotFoundError as e:
        raise ToonCliError(f"TOON CLI not found at {toon_path}") from e
    except Exception as e:
        raise ToonCliError(f"Unexpected error validating TOON CLI: {e}") from e


def ensure_toon_available() -> str:
    """
    Ensure TOON CLI is available and functional.

    Returns:
        Path to validated TOON executable.

    Raises:
        ToonCliError: If TOON CLI is not available or invalid.
    """
    try:
        version = validate_toon_cli_version()
        toon_path = find_toon_executable()
        logger.info(f"✓ TOON CLI validated: {version}")
        return toon_path
    except ToonCliError:
        raise  # Re-raise ToonCliError as-is
