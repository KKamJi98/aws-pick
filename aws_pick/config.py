"""
AWS config file parsing module.

This module handles reading and parsing AWS configuration files,
displaying available profiles, and validating user selections.
"""

import configparser
import logging
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.table import Table

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


def get_grouped_profiles(profiles: List[str]) -> List[Tuple[str, str]]:
    """
    Group profiles by environment and return a list of (profile, group) tuples.

    Args:
        profiles (List[str]): List of profile names

    Returns:
        List[Tuple[str, str]]: List of (profile, group) tuples sorted by group
    """
    groups = {
        "prod": [],
        "preprod": [],
        "stg": [],
        "dev": [],
        "others": [],
    }
    for profile in profiles:
        if "prod" in profile:
            groups["prod"].append(profile)
        elif "preprod" in profile:
            groups["preprod"].append(profile)
        elif "stg" in profile:
            groups["stg"].append(profile)
        elif "dev" in profile:
            groups["dev"].append(profile)
        else:
            groups["others"].append(profile)

    grouped_profiles = []
    for group_name, profile_list in groups.items():
        for profile in sorted(profile_list):
            grouped_profiles.append((profile, group_name))
    return grouped_profiles


def display_profiles(grouped_profiles: List[Tuple[str, str]]) -> None:
    """
    Display available AWS profiles in a tabulated format using rich.

    Args:
        grouped_profiles (List[Tuple[str, str]]): List of (profile, group) tuples
    """
    console = Console(file=sys.stderr)

    if not grouped_profiles:
        console.print("[bold red]No AWS profiles found in ~/.aws/config[/bold red]")
        return

    group_colors = {
        "prod": "bold red",
        "preprod": "bold green",
        "stg": "bold orange3",
        "dev": "bold blue",
        "others": "bold white",
    }

    table = Table(title="AWS Profiles", style="bold blue")
    table.add_column("No.", style="cyan", justify="right")
    table.add_column("Profile", style="white")
    table.add_column("Group", style="white")

    for i, (profile, group_name) in enumerate(grouped_profiles):
        color = group_colors.get(group_name, "white")
        table.add_row(
            str(i + 1),
            profile,
            f"[{color}]{group_name}[/{color}]",
        )

    console.print(table)


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
