"""Command-line interface for AWS Profile Switcher."""

import logging
import sys
from typing import List, Optional

from aws_pick.config import (
    display_profiles,
    read_aws_profiles,
    validate_profile_selection,
)
from aws_pick.shell import update_aws_profile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

def get_profile_selection(profiles: List[str]) -> Optional[str]:
    """
    Prompt the user to select a profile.
    
    Args:
        profiles (List[str]): List of available profiles
    
    Returns:
        Optional[str]: Selected profile name or None if cancelled
    """
    while True:
        try:
            selection = input("Enter profile number or name: ").strip()
            
            # Allow user to cancel
            if selection.lower() in ("q", "quit", "exit"):
                return None
            
            profile = validate_profile_selection(selection, profiles)
            if profile:
                return profile
            
            print("Invalid selection. Please enter a valid profile number or name.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None

def main() -> int:
    """Main entry point for the CLI."""
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
            return 1
        
        print(f"Selected profile: {profile}")
        
        # Update shell configuration
        success, backup_path = update_aws_profile(profile)
        if not success:
            logger.error("Failed to update AWS profile.")
            return 1
        
        if backup_path:
            print(f"Backup created at {backup_path}")
        
        print(f"Updated ~/.zshrc with AWS_PROFILE={profile}")
        print("Please restart your shell or run 'source ~/.zshrc' to apply changes.")
        
        return 0
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
