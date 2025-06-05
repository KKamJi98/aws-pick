"""Tests for the CLI module."""

from unittest.mock import MagicMock, patch

import pytest

from aws_profile_switcher.cli import get_profile_selection, main


@patch("builtins.input")
def test_get_profile_selection_valid_number(mock_input):
    """Test selecting profile by number."""
    # Setup mock
    mock_input.return_value = "2"
    profiles = ["default", "dev", "prod"]
    
    # Call function
    result = get_profile_selection(profiles)
    
    # Assertions
    assert result == "dev"
    mock_input.assert_called_once()


@patch("builtins.input")
def test_get_profile_selection_valid_name(mock_input):
    """Test selecting profile by name."""
    # Setup mock
    mock_input.return_value = "prod"
    profiles = ["default", "dev", "prod"]
    
    # Call function
    result = get_profile_selection(profiles)
    
    # Assertions
    assert result == "prod"
    mock_input.assert_called_once()


@patch("builtins.input")
@patch("builtins.print")
def test_get_profile_selection_invalid_then_valid(mock_print, mock_input):
    """Test selecting invalid profile then valid."""
    # Setup mock
    mock_input.side_effect = ["invalid", "1"]
    profiles = ["default", "dev", "prod"]
    
    # Call function
    result = get_profile_selection(profiles)
    
    # Assertions
    assert result == "default"
    assert mock_input.call_count == 2
    assert mock_print.call_count >= 1  # At least one error message


@patch("builtins.input")
def test_get_profile_selection_quit(mock_input):
    """Test quitting profile selection."""
    # Setup mock
    mock_input.return_value = "q"
    profiles = ["default", "dev", "prod"]
    
    # Call function
    result = get_profile_selection(profiles)
    
    # Assertions
    assert result is None
    mock_input.assert_called_once()


@patch("builtins.input")
def test_get_profile_selection_keyboard_interrupt(mock_input):
    """Test keyboard interrupt during profile selection."""
    # Setup mock
    mock_input.side_effect = KeyboardInterrupt()
    profiles = ["default", "dev", "prod"]
    
    # Call function
    result = get_profile_selection(profiles)
    
    # Assertions
    assert result is None
    mock_input.assert_called_once()


@patch("aws_profile_switcher.cli.read_aws_profiles")
def test_main_no_profiles(mock_read_profiles):
    """Test main function with no profiles."""
    # Setup mock
    mock_read_profiles.return_value = []
    
    # Call function
    result = main()
    
    # Assertions
    assert result == 1
    mock_read_profiles.assert_called_once()


@patch("aws_profile_switcher.cli.read_aws_profiles")
@patch("aws_profile_switcher.cli.display_profiles")
@patch("aws_profile_switcher.cli.get_profile_selection")
def test_main_cancelled_selection(mock_get_selection, mock_display, mock_read_profiles):
    """Test main function with cancelled selection."""
    # Setup mock
    mock_read_profiles.return_value = ["default", "dev", "prod"]
    mock_get_selection.return_value = None
    
    # Call function
    result = main()
    
    # Assertions
    assert result == 1
    mock_read_profiles.assert_called_once()
    mock_display.assert_called_once()
    mock_get_selection.assert_called_once()


@patch("aws_profile_switcher.cli.read_aws_profiles")
@patch("aws_profile_switcher.cli.display_profiles")
@patch("aws_profile_switcher.cli.get_profile_selection")
@patch("aws_profile_switcher.cli.update_aws_profile")
@patch("builtins.print")
def test_main_successful_update(mock_print, mock_update, mock_get_selection, mock_display, mock_read_profiles):
    """Test main function with successful update."""
    # Setup mock
    mock_read_profiles.return_value = ["default", "dev", "prod"]
    mock_get_selection.return_value = "dev"
    mock_update.return_value = (True, "/home/user/.zshrc.bak-20250605060000")
    
    # Call function
    result = main()
    
    # Assertions
    assert result == 0
    mock_read_profiles.assert_called_once()
    mock_display.assert_called_once()
    mock_get_selection.assert_called_once()
    mock_update.assert_called_once_with("dev")
    assert mock_print.call_count >= 3  # At least 3 print calls


@patch("aws_profile_switcher.cli.read_aws_profiles")
@patch("aws_profile_switcher.cli.display_profiles")
@patch("aws_profile_switcher.cli.get_profile_selection")
@patch("aws_profile_switcher.cli.update_aws_profile")
def test_main_failed_update(mock_update, mock_get_selection, mock_display, mock_read_profiles):
    """Test main function with failed update."""
    # Setup mock
    mock_read_profiles.return_value = ["default", "dev", "prod"]
    mock_get_selection.return_value = "dev"
    mock_update.return_value = (False, None)
    
    # Call function
    result = main()
    
    # Assertions
    assert result == 1
    mock_read_profiles.assert_called_once()
    mock_display.assert_called_once()
    mock_get_selection.assert_called_once()
    mock_update.assert_called_once_with("dev")
