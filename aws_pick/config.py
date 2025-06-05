"""AWS config file parsing module."""

import configparser
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

def get_aws_config_path() -> Path:
    """Get the path to the AWS config file."""
    return Path.home() / ".aws" / "config"

def read_aws_profiles() -> List[str]:
    """
    Read AWS profiles from the config file.
    
    Returns:
        List[str]: List of profile names
    """
    config_path = get_aws_config_path()
    if not config_path.exists():
        logger.error(f"AWS config file not found at {config_path}")
        return []
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    profiles = []
    for section in config.sections():
        # AWS config uses "profile name" format for non-default profiles
        if section == "default":
            profiles.append("default")
        elif section.startswith("profile "):
            profile_name = section[len("profile "):]
            profiles.append(profile_name)
    
    logger.info(f"Found {len(profiles)} AWS profiles")
    return sorted(profiles)

def display_profiles(profiles: List[str]) -> None:
    """
    Display available AWS profiles in a tabulated format.
    
    Args:
        profiles (List[str]): List of profile names
    """
    from tabulate import tabulate
    
    if not profiles:
        print("No AWS profiles found in ~/.aws/config")
        return
    
    table_data = [(i+1, profile) for i, profile in enumerate(profiles)]
    headers = ["Num", "Profile"]
    
    print("Available AWS Profiles:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()

def validate_profile_selection(selection: str, profiles: List[str]) -> Optional[str]:
    """
    Validate the user's profile selection.
    
    Args:
        selection (str): User input (number or profile name)
        profiles (List[str]): List of available profiles
    
    Returns:
        Optional[str]: Selected profile name or None if invalid
    """
    if not selection:
        logger.error("Empty selection")
        return None
    
    # Check if selection is a number
    if selection.isdigit():
        index = int(selection) - 1
        if 0 <= index < len(profiles):
            return profiles[index]
        else:
            logger.error(f"Invalid profile number: {selection}")
            return None
    
    # Check if selection is a profile name
    if selection in profiles:
        return selection
    
    logger.error(f"Profile '{selection}' not found")
    return None
