"""Tests for the config module."""

import configparser
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aws_pick.config import (
    display_profiles,
    get_aws_config_path,
    read_aws_profiles,
    validate_profile_selection,
)


def test_get_aws_config_path():
    """Test getting the AWS config path."""
    expected_path = Path.home() / ".aws" / "config"
    assert get_aws_config_path() == expected_path


@patch("aws_pick.config.get_aws_config_path")
@patch("configparser.ConfigParser")
def test_read_aws_profiles(mock_configparser, mock_get_path):
    """Test reading AWS profiles from config."""
    # Setup mock
    mock_config = MagicMock()
    mock_config.sections.return_value = ["default", "profile dev", "profile prod"]
    mock_configparser.return_value = mock_config

    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_get_path.return_value = mock_path

    # Call function
    profiles = read_aws_profiles()

    # Assertions
    assert profiles == ["default", "dev", "prod"]
    mock_config.read.assert_called_once_with(mock_path)


@patch("aws_pick.config.get_aws_config_path")
def test_read_aws_profiles_no_config(mock_get_path):
    """Test reading AWS profiles when config doesn't exist."""
    # Setup mock
    mock_path = MagicMock()
    mock_path.exists.return_value = False
    mock_get_path.return_value = mock_path

    # Call function
    profiles = read_aws_profiles()

    # Assertions
    assert profiles == []


@patch("builtins.print")
@patch.dict(
    "sys.modules",
    {"tabulate": MagicMock(tabulate=MagicMock(return_value="MOCK_TABLE"))},
)
def test_display_profiles(mock_print):
    """Test displaying profiles."""
    # Setup mock
    profiles = ["default", "dev", "prod"]
    display_profiles(profiles)

    # Assertions
    assert mock_print.call_count >= 3  # At least 3 print calls


@patch("builtins.print")
@patch.dict(
    "sys.modules",
    {"tabulate": MagicMock(tabulate=MagicMock(return_value="MOCK_TABLE"))},
)
def test_display_profiles_empty(mock_print):
    """Test displaying empty profiles list."""
    # Call function
    display_profiles([])

    # Assertions
    mock_print.assert_called_once_with("No AWS profiles found in ~/.aws/config")


def test_validate_profile_selection():
    """Test validating profile selection."""
    profiles = ["default", "dev", "prod"]

    # Test valid number
    assert validate_profile_selection("1", profiles) == "default"
    assert validate_profile_selection("2", profiles) == "dev"
    assert validate_profile_selection("3", profiles) == "prod"

    # Test valid name
    assert validate_profile_selection("default", profiles) == "default"
    assert validate_profile_selection("dev", profiles) == "dev"
    assert validate_profile_selection("prod", profiles) == "prod"

    # Test invalid number
    assert validate_profile_selection("0", profiles) is None
    assert validate_profile_selection("4", profiles) is None
    assert validate_profile_selection("999", profiles) is None

    # Test invalid name
    assert validate_profile_selection("staging", profiles) is None

    # Test empty input
    assert validate_profile_selection("", profiles) is None
