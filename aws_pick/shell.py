"""Shell profile modification module.

This module handles updating the shell configuration file (``~/.zshrc`` or
``~/.bashrc``) to set the ``AWS_PROFILE`` environment variable for the selected
profile. It also supports reloading the corresponding shell configuration so the
changes take effect immediately.
"""

import datetime
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def get_shell_type() -> str:
    """Return the current shell name (``bash`` or ``zsh``)."""
    shell = os.environ.get("SHELL", "")
    if shell.endswith("bash"):
        return "bash"
    return "zsh"


def get_shell_rc_path() -> Path:
    """Get the path to the active shell rc file."""
    shell_type = get_shell_type()
    return Path.home() / f".{shell_type}rc"


def get_zshrc_path() -> Path:
    """Backward compatible wrapper for :func:`get_shell_rc_path`."""
    return get_shell_rc_path()


def backup_zshrc(zshrc_path: Path) -> Path:
    """Backward compatible wrapper for :func:`backup_shell_rc`."""
    return backup_shell_rc(zshrc_path)


def backup_shell_rc(rc_path: Path) -> Path:
    """Create a timestamped backup of a shell rc file."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = Path(f"{rc_path}.bak-{timestamp}")

        shutil.copy2(rc_path, backup_path)
        logger.info(f"Backup created at {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise


def update_aws_profile(profile_name: str) -> Tuple[bool, Optional[Path]]:
    """
    Update the AWS_PROFILE environment variable in the zshrc file.

    Args:
        profile_name (str): AWS profile name to set

    Returns:
        Tuple[bool, Optional[Path]]: Success status and backup path if created

    Note:
        - Returns (True, None) if profile is already set (no changes made)
        - Returns (True, Path) if profile was updated successfully
        - Returns (False, None) if an error occurred

    This function ensures idempotency by checking if the profile is already set
    before making any changes to the zshrc file.
    """
    rc_path = get_zshrc_path()

    if not rc_path.exists():
        logger.error(f"shell rc file not found at {rc_path}")
        return False, None

    try:
        # Read the current content
        with open(rc_path, "r") as f:
            content = f.read()

        # Check if AWS_PROFILE is already set to the same value
        aws_profile_pattern = re.compile(r"^export\s+AWS_PROFILE=(.+)$", re.MULTILINE)
        match = aws_profile_pattern.search(content)

        # Extract current profile value if it exists
        current_profile = None
        if match:
            current_profile = match.group(1).strip("\"'")

        if current_profile == profile_name:
            logger.info(f"AWS_PROFILE already set to {profile_name}, no changes needed")
            return True, None

        # Create backup
        backup_path = backup_shell_rc(rc_path)

        # Update or add AWS_PROFILE
        if match:
            # Replace existing AWS_PROFILE
            new_content = aws_profile_pattern.sub(
                f'export AWS_PROFILE="{profile_name}"', content
            )
            logger.info(
                f"Replacing existing AWS_PROFILE={current_profile} with {profile_name}"
            )
        else:
            # Add AWS_PROFILE at the end
            new_content = (
                content.rstrip()
                + f'\n\n# Added by AWS Pick\nexport AWS_PROFILE="{profile_name}"\n'
            )
            logger.info(f"Adding new AWS_PROFILE={profile_name} entry")

        # Write the updated content
        with open(rc_path, "w") as f:
            f.write(new_content)

        logger.info(f"Successfully updated {rc_path} with AWS_PROFILE={profile_name}")
        return True, backup_path

    except Exception as e:
        logger.error(f"Failed to update AWS profile: {e}", exc_info=True)
        return False, None


def source_shell_rc(rc_path: Path) -> bool:
    """Source the given shell rc file using the current shell."""
    shell = get_shell_type()
    try:
        subprocess.run([shell, "-c", f"source {rc_path}"], check=True)
        logger.info(f"Sourced {rc_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to source rc file: {e}")
        return False
