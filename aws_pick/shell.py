"""Shell profile modification module.

This module handles updating the user's shell configuration file to set the
``AWS_PROFILE`` environment variable for the selected profile.  Both ``bash``
and ``zsh`` shells are supported.
"""

import datetime
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def get_shell_rc_path(shell: Optional[str] = None) -> Path:
    """Return the path to the current shell configuration file.

    Parameters
    ----------
    shell:
        Optional shell name. If ``None`` the ``$SHELL`` environment variable is
        inspected. Only ``bash`` and ``zsh`` are recognised; any other value
        defaults to ``bash``.
    """

    if shell is None:
        shell = os.environ.get("SHELL", "")

    shell_name = Path(shell).name
    if shell_name.endswith("zsh"):
        return Path.home() / ".zshrc"
    return Path.home() / ".bashrc"


def get_zshrc_path() -> Path:
    """Compatibility wrapper returning ``~/.zshrc``."""

    return get_shell_rc_path("zsh")


def get_bashrc_path() -> Path:
    """Compatibility wrapper returning ``~/.bashrc``."""

    return get_shell_rc_path("bash")


def backup_rc_file(rc_path: Path) -> Path:
    """Create a backup of a shell configuration file."""

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = Path(f"{rc_path}.bak-{timestamp}")

        shutil.copy2(rc_path, backup_path)
        logger.info(f"Backup created at {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise


def backup_zshrc(zshrc_path: Path) -> Path:
    """Compatibility wrapper for older API."""

    return backup_rc_file(zshrc_path)


def update_aws_profile(profile_name: str) -> Tuple[bool, Optional[Path]]:
    """
    Update the ``AWS_PROFILE`` environment variable in the user's shell
    configuration file.

    Args:
        profile_name (str): AWS profile name to set

    Returns:
        Tuple[bool, Optional[Path]]: Success status and backup path if created

    Note:
        - Returns (True, None) if profile is already set (no changes made)
        - Returns (True, Path) if profile was updated successfully
        - Returns (False, None) if an error occurred

    This function ensures idempotency by checking if the profile is already set
    before making any changes to the rc file.
    """
    rc_path = get_shell_rc_path()

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
        backup_path = backup_rc_file(rc_path)

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
