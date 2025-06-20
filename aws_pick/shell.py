"""
Shell profile modification module.

This module handles updating the shell configuration files
(~/.bashrc, ~/.zshrc, ~/.config/fish/config.fish, etc.)
to set the AWS_PROFILE environment variable for the selected profile.
"""

import datetime
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ShellConfig:
    """Shell configuration class to handle different shell types."""

    def __init__(self, name: str, rc_path: Path, export_format: str):
        """
        Initialize a shell configuration.

        Args:
            name (str): Name of the shell (e.g., "bash", "zsh", "fish")
            rc_path (Path): Path to the shell's rc file
            export_format (str): Format string for exporting variables in this shell
        """
        self.name = name
        self.rc_path = rc_path
        self.export_format = export_format

    def get_profile_line(self, profile_name: str) -> str:
        """
        Get the line to add to the shell config file.

        Args:
            profile_name (str): AWS profile name to set

        Returns:
            str: Formatted line for setting AWS_PROFILE
        """
        return self.export_format.format(profile_name=profile_name)

    def get_profile_pattern(self) -> re.Pattern:
        """
        Get the regex pattern to match AWS_PROFILE in this shell's syntax.

        Returns:
            re.Pattern: Compiled regex pattern
        """
        if self.name == "fish":
            return re.compile(
                r'^set -[gx] AWS_PROFILE\s+["\']?(.+?)["\']?\s*$', re.MULTILINE
            )
        else:
            return re.compile(r"^export\s+AWS_PROFILE=(.+)$", re.MULTILINE)


def detect_shell() -> str:
    """
    Detect the current shell.

    Returns:
        str: Name of the current shell (e.g., "bash", "zsh", "fish")
    """
    # Try to get from SHELL environment variable
    shell_path = os.environ.get("SHELL", "")
    if shell_path:
        shell_name = os.path.basename(shell_path)
        logger.info(f"Detected shell from SHELL env var: {shell_name}")
        return shell_name

    # Fallback to process inspection
    try:
        # Get the parent process name
        result = subprocess.run(
            ["ps", "-p", str(os.getppid()), "-o", "comm="],
            capture_output=True,
            text=True,
            check=True,
        )
        shell_name = result.stdout.strip()
        if "/" in shell_name:
            shell_name = os.path.basename(shell_name)
        logger.info(f"Detected shell from parent process: {shell_name}")
        return shell_name
    except Exception as e:
        logger.warning(f"Failed to detect shell: {e}")
        # Default to bash as fallback
        return "bash"


def get_shell_configs() -> Dict[str, ShellConfig]:
    """
    Get configurations for supported shells.

    Returns:
        Dict[str, ShellConfig]: Dictionary of shell configurations
    """
    home = Path.home()
    return {
        "bash": ShellConfig(
            "bash", home / ".bashrc", 'export AWS_PROFILE="{profile_name}"'
        ),
        "zsh": ShellConfig(
            "zsh", home / ".zshrc", 'export AWS_PROFILE="{profile_name}"'
        ),
        "fish": ShellConfig(
            "fish",
            home / ".config" / "fish" / "config.fish",
            'set -gx AWS_PROFILE "{profile_name}"',
        ),
        # Add more shells as needed
    }


def get_rc_path(shell_name: str = None) -> Tuple[Path, ShellConfig]:
    """
    Get the path to the shell's rc file.

    Args:
        shell_name (str, optional): Shell name. If None, auto-detect.

    Returns:
        Tuple[Path, ShellConfig]: Path to the rc file and shell config
    """
    if shell_name is None:
        shell_name = detect_shell()

    shell_configs = get_shell_configs()

    # Normalize shell name (remove version numbers, etc.)
    normalized_name = shell_name.lower()
    for name in shell_configs:
        if normalized_name.startswith(name):
            shell_config = shell_configs[name]
            logger.info(f"Using {name} configuration at {shell_config.rc_path}")
            return shell_config.rc_path, shell_config

    # Fallback to bash if shell not recognized
    logger.warning(f"Shell '{shell_name}' not recognized, falling back to bash")
    return shell_configs["bash"].rc_path, shell_configs["bash"]


def backup_rc_file(rc_path: Path) -> Path:
    """
    Create a backup of the shell rc file.

    Args:
        rc_path (Path): Path to the rc file

    Returns:
        Path: Path to the backup file

    Note:
        Creates a timestamped backup with format ~/.rcfile.bak-YYYYMMDDHHMMSS
        Preserves file permissions and metadata using shutil.copy2
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = Path(f"{rc_path}.bak-{timestamp}")

        shutil.copy2(rc_path, backup_path)
        logger.info(f"Backup created at {backup_path}")

        # Rotate old backups, keep only the 5 most recent
        backups = sorted(rc_path.parent.glob(f"{rc_path.name}.bak-*"))
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                try:
                    old_backup.unlink()
                    logger.info(f"Removed old backup {old_backup}")
                except OSError as e:
                    logger.warning(f"Failed to remove old backup {old_backup}: {e}")

        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise


def update_aws_profile(
    profile_name: str, shell_name: str = None
) -> Tuple[bool, Optional[Path]]:
    """
    Update the AWS_PROFILE environment variable in the shell rc file.

    Args:
        profile_name (str): AWS profile name to set
        shell_name (str, optional): Shell name. If None, auto-detect.

    Returns:
        Tuple[bool, Optional[Path]]: Success status and backup path if created

    Note:
        - Returns (True, None) if profile is already set (no changes made)
        - Returns (True, Path) if profile was updated successfully
        - Returns (False, None) if an error occurred

    This function ensures idempotency by checking if the profile is already set
    before making any changes to the rc file.
    """
    rc_path, shell_config = get_rc_path(shell_name)

    if not rc_path.exists():
        # Create parent directories if they don't exist (especially for fish)
        if shell_config.name == "fish":
            rc_path.parent.mkdir(parents=True, exist_ok=True)
            with open(rc_path, "w") as f:
                f.write(f"# Created by AWS Pick\n\n")
            logger.info(f"Created new config file at {rc_path}")
        else:
            logger.error(f"Shell config file not found at {rc_path}")
            return False, None

    try:
        # Read the current content
        with open(rc_path, "r") as f:
            content = f.read()

        # Check if AWS_PROFILE is already set to the same value
        aws_profile_pattern = shell_config.get_profile_pattern()
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
                shell_config.get_profile_line(profile_name), content
            )
            logger.info(
                f"Replacing existing AWS_PROFILE={current_profile} with {profile_name}"
            )
        else:
            # Add AWS_PROFILE at the end
            new_content = (
                content.rstrip()
                + f"\n\n# Added by AWS Pick\n{shell_config.get_profile_line(profile_name)}\n"
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


def source_rc_file(shell_config: ShellConfig) -> bool:
    """Source the rc file for the detected shell."""

    try:
        subprocess.run(
            [shell_config.name, "-c", f"source {shell_config.rc_path}"],
            check=True,
        )
        logger.info(f"Sourced {shell_config.rc_path} using {shell_config.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to source rc file: {e}")
        return False
