"""
Shell profile modification module.

This module handles updating the shell configuration file (~/.zshrc)
to set the AWS_PROFILE environment variable for the selected profile.
"""

import datetime
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def get_zshrc_path() -> Path:
    """
    Get the path to the zshrc file.
    
    Returns:
        Path: Path to the user's ~/.zshrc file
    """
    return Path.home() / ".zshrc"

def backup_zshrc(zshrc_path: Path) -> Path:
    """
    Create a backup of the zshrc file.
    
    Args:
        zshrc_path (Path): Path to the zshrc file
    
    Returns:
        Path: Path to the backup file
        
    Note:
        Creates a timestamped backup with format ~/.zshrc.bak-YYYYMMDDHHMMSS
        Preserves file permissions and metadata using shutil.copy2
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = Path(f"{zshrc_path}.bak-{timestamp}")
        
        shutil.copy2(zshrc_path, backup_path)
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
    zshrc_path = get_zshrc_path()
    
    if not zshrc_path.exists():
        logger.error(f"zshrc file not found at {zshrc_path}")
        return False, None
    
    try:
        # Read the current content
        with open(zshrc_path, "r") as f:
            content = f.read()
        
        # Check if AWS_PROFILE is already set to the same value
        aws_profile_pattern = re.compile(r'^export\s+AWS_PROFILE=(.+)$', re.MULTILINE)
        match = aws_profile_pattern.search(content)
        
        # Extract current profile value if it exists
        current_profile = None
        if match:
            current_profile = match.group(1).strip('"\'')
            
        if current_profile == profile_name:
            logger.info(f"AWS_PROFILE already set to {profile_name}, no changes needed")
            return True, None
        
        # Create backup
        backup_path = backup_zshrc(zshrc_path)
        
        # Update or add AWS_PROFILE
        if match:
            # Replace existing AWS_PROFILE
            new_content = aws_profile_pattern.sub(f'export AWS_PROFILE="{profile_name}"', content)
            logger.info(f"Replacing existing AWS_PROFILE={current_profile} with {profile_name}")
        else:
            # Add AWS_PROFILE at the end
            new_content = content.rstrip() + f'\n\n# Added by AWS Pick\nexport AWS_PROFILE="{profile_name}"\n'
            logger.info(f"Adding new AWS_PROFILE={profile_name} entry")
        
        # Write the updated content
        with open(zshrc_path, "w") as f:
            f.write(new_content)
        
        logger.info(f"Successfully updated {zshrc_path} with AWS_PROFILE={profile_name}")
        return True, backup_path
        
    except Exception as e:
        logger.error(f"Failed to update AWS profile: {e}", exc_info=True)
        return False, None
