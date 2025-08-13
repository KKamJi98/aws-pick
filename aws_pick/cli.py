"""Command-line interface for AWS Pick.

This module provides the main CLI functionality for the AWS Pick tool,
including user interaction, profile selection, and command execution.
"""

import argparse
import logging
import sys
from typing import List, Optional

from aws_pick.config import (
    display_profiles,
    get_grouped_profiles,
    read_aws_profiles,
    validate_profile_selection,
)
from aws_pick.shell import (
    detect_shell,
    generate_export_command,
    get_rc_path,
    update_aws_profile,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="AWS profile picker")
    # Deprecated option kept for backward compatibility but ignored
    parser.add_argument(
        "--export-command",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


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
            print("Enter profile number or name: ", end="", file=sys.stderr, flush=True)
            selection = input().strip()

            if not selection:
                print("No selection made.", file=sys.stderr)
                logger.info("Empty selection")
                return None

            # Allow user to cancel
            if selection.lower() in ("q", "quit", "exit"):
                logger.info("User cancelled profile selection")
                return None

            profile = validate_profile_selection(selection, profiles)
            if profile:
                return profile

            print(
                "Invalid selection. Please enter a valid profile number or name.",
                file=sys.stderr,
            )
        except KeyboardInterrupt:
            print("\nOperation cancelled.", file=sys.stderr)
            logger.info("Profile selection cancelled via keyboard interrupt")
            return None


def main(argv: Optional[List[str]] = None) -> int:
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

        # Group and sort profiles for display
        grouped_profiles = get_grouped_profiles(profiles)
        display_profiles(grouped_profiles)

        # The list of profiles for selection must match the display order
        selection_profiles = [p[0] for p in grouped_profiles]

        # Get user selection
        profile = get_profile_selection(selection_profiles)
        if not profile:
            logger.info("No profile selected, exiting")
            return 1

        print(f"Selected profile: {profile}", file=sys.stderr)

        # Detect shell and get RC path
        shell_name = detect_shell()
        rc_path, shell_config = get_rc_path(shell_name)

        # Update shell configuration
        success, backup_path = update_aws_profile(profile, shell_name)
        if not success:
            logger.error("Failed to update AWS profile.")
            return 1

        if backup_path:
            print(f"Backup created at {backup_path}", file=sys.stderr)

        print(f"Updated {rc_path} with AWS_PROFILE={profile}", file=sys.stderr)

        export_cmd = generate_export_command(profile, shell_name)

        # Always print the export command so the user can eval the output
        print(export_cmd)
        print(
            "Run 'eval \"$(awspick)\"' to apply in the current shell",
            file=sys.stderr,
        )

        return 0

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
