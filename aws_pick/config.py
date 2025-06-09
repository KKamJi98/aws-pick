"""
AWS config file parsing module.

This module handles reading and parsing AWS configuration files,
displaying available profiles, and validating user selections.
"""

import configparser
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from tabulate import tabulate
except ImportError:  # pragma: no cover - optional dependency
    tabulate = None

logger = logging.getLogger(__name__)


def get_aws_config_path() -> Path:
    """
    Get the path to the AWS config file.

    Returns:
        Path: Path to the AWS config file (~/.aws/config)
    """
    return Path.home() / ".aws" / "config"


def read_aws_profiles() -> List[str]:
    """
    Read AWS profiles from the config file.

    Returns:
        List[str]: List of profile names sorted alphabetically

    Note:
        Returns an empty list if the config file doesn't exist or has no profiles.
        Handles both default profile and named profiles with "profile " prefix.
    """
    config_path = get_aws_config_path()
    if not config_path.exists():
        logger.error(f"AWS config file not found at {config_path}")
        return []

    try:
        config = configparser.ConfigParser()
        config.read(config_path)

        profiles = []
        for section in config.sections():
            # AWS config uses "profile name" format for non-default profiles
            if section == "default":
                profiles.append("default")
            elif section.startswith("profile "):
                profile_name = section[len("profile ") :]
                profiles.append(profile_name)

        logger.info(f"Found {len(profiles)} AWS profiles")
        return sorted(profiles)
    except configparser.Error as e:
        logger.error(f"Error parsing AWS config file: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error reading AWS profiles: {e}")
        return []


def display_profiles(profiles: List[str]) -> None:
    """
    Display available AWS profiles in a tabulated format.

    Args:
        profiles (List[str]): List of profile names

    Note:
        Uses the tabulate library to create a nicely formatted table
        with numbered options for easy selection.
    """
    if not profiles:
        print("No AWS profiles found in ~/.aws/config")
        return

    if tabulate:
        table_data = [(i + 1, profile) for i, profile in enumerate(profiles)]
        headers = ["Num", "Profile"]

        print("Available AWS Profiles:")
        print(tabulate(table_data, headers=headers, tablefmt="github"))
        print()
    else:  # pragma: no cover - exercised when tabulate isn't installed
        logger.warning("tabulate library not found, using simple format")
        print("Available AWS Profiles:")
        for i, profile in enumerate(profiles, 1):
            print(f"{i}. {profile}")
        print()


def validate_profile_selection(selection: str, profiles: List[str]) -> Optional[str]:
    """
    Validate the user's profile selection.

    Args:
        selection (str): User input (number or profile name)
        profiles (List[str]): List of available profiles

    Returns:
        Optional[str]: Selected profile name or None if invalid

    Note:
        Handles both numeric selection (by index) and direct profile name input.
        Returns None for any invalid input with appropriate error logging.
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
            logger.error(
                f"Invalid profile number: {selection}. Valid range is 1-{len(profiles)}"
            )
            return None

    # Check if selection is a profile name
    if selection in profiles:
        return selection

    # Check for case-insensitive match as a fallback
    for profile in profiles:
        if profile.lower() == selection.lower():
            logger.info(f"Found case-insensitive match for '{selection}': '{profile}'")
            return profile

    logger.error(f"Profile '{selection}' not found in available profiles")
    return None
