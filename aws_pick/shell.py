"""Shell profile modification module."""

import datetime
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def get_zshrc_path() -> Path:
    """Get the path to the zshrc file."""
    return Path.home() / ".zshrc"

def backup_zshrc(zshrc_path: Path) -> Path:
    """
    Create a backup of the zshrc file.
    
    Args:
        zshrc_path (Path): Path to the zshrc file
    
    Returns:
        Path: Path to the backup file
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = Path(f"{zshrc_path}.bak-{timestamp}")
    
    shutil.copy2(zshrc_path, backup_path)
    logger.info(f"Backup created at {backup_path}")
    return backup_path

def update_aws_profile(profile_name: str) -> Tuple[bool, Optional[Path]]:
    """
    Update the AWS_PROFILE environment variable in the zshrc file.
    
    Args:
        profile_name (str): AWS profile name to set
    
    Returns:
        Tuple[bool, Optional[Path]]: Success status and backup path if created
    """
    zshrc_path = get_zshrc_path()
    
    if not zshrc_path.exists():
        logger.error(f"zshrc file not found at {zshrc_path}")
        return False, None
    
    # Read the current content
    with open(zshrc_path, "r") as f:
        content = f.read()
    
    # Check if AWS_PROFILE is already set to the same value
    aws_profile_pattern = re.compile(r'^export\s+AWS_PROFILE=(.+)$', re.MULTILINE)
    match = aws_profile_pattern.search(content)
    
    if match and match.group(1).strip('"\'') == profile_name:
        logger.info(f"AWS_PROFILE already set to {profile_name}")
        return True, None
    
    # Create backup
    backup_path = backup_zshrc(zshrc_path)
    
    # Update or add AWS_PROFILE
    if match:
        # Replace existing AWS_PROFILE
        new_content = aws_profile_pattern.sub(f'export AWS_PROFILE="{profile_name}"', content)
    else:
        # Add AWS_PROFILE at the end
        new_content = content.rstrip() + f'\n\n# Added by AWS Profile Switcher\nexport AWS_PROFILE="{profile_name}"\n'
    
    # Write the updated content
    with open(zshrc_path, "w") as f:
        f.write(new_content)
    
    logger.info(f"Updated {zshrc_path} with AWS_PROFILE={profile_name}")
    return True, backup_path
