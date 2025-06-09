"""Command-line interface for AWS Pick.

This module provides the main CLI functionality for the AWS Pick tool,
including user interaction, profile selection, and command execution.
"""

import logging
import sys
from typing import List, Optional

from aws_pick.config import (
    display_profiles,
    read_aws_profiles,
    validate_profile_selection,
)
from aws_pick.shell import get_shell_rc_path, update_aws_profile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def get_profile_selection(profiles: List[str]) -> Optional[str]:
    """
    Prompt the user to select a profile and validate the input.

    Args:
        profiles (List[str]): List of available profiles

    Returns:
        Optional[str]: Selected profile name or None if cancelled

    Note:
        The function will continue to prompt until a valid selection is made
        or the user explicitly cancels the operation.
    """
    while True:
        try:
            selection = input("Enter profile number or name: ").strip()

            # Allow user to cancel
            if selection.lower() in ("q", "quit", "exit"):
                logger.info("User cancelled profile selection")
                return None

            profile = validate_profile_selection(selection, profiles)
            if profile:
                return profile

            print("Invalid selection. Please enter a valid profile number or name.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            logger.info("Profile selection cancelled via keyboard interrupt")
            return None


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        int: Exit code (0 for success, 1 for failure)

    This function orchestrates the entire AWS profile switching process:
    1. Reads available AWS profiles from config
    2. Displays profiles to the user
    3. Gets user selection
    4. Updates shell configuration with the selected profile
    """
    try:
        # Read AWS profiles
        profiles = read_aws_profiles()
        if not profiles:
            logger.error("No AWS profiles found. Please check your AWS configuration.")
            return 1

        # Display profiles
        display_profiles(profiles)

        # Get user selection
        profile = get_profile_selection(profiles)
        if not profile:
            logger.info("No profile selected, exiting")
            return 1

        print(f"Selected profile: {profile}")

        # Update shell configuration
        success, backup_path = update_aws_profile(profile)
        if not success:
            logger.error("Failed to update AWS profile.")
            return 1

        if backup_path:
            print(f"Backup created at {backup_path}")

        rc_path = get_shell_rc_path()
        print(f"Updated {rc_path} with AWS_PROFILE={profile}")
        print(f"Please restart your shell or run 'source {rc_path}' to apply changes.")

        return 0

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
