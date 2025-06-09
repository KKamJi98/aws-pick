"""Tests for the shell module."""

import os
import re
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from aws_pick.shell import (
    backup_shell_rc,
    backup_zshrc,
    get_zshrc_path,
    update_aws_profile,
)


def test_get_zshrc_path():
    """Test getting the zshrc path."""
    expected_path = Path.home() / ".zshrc"
    assert get_zshrc_path() == expected_path


@patch("aws_pick.shell.shutil.copy2")
@patch("aws_pick.shell.datetime")
def test_backup_zshrc(mock_datetime, mock_copy):
    """Test backing up zshrc file."""
    # Setup mocks
    mock_datetime.datetime.now.return_value.strftime.return_value = "20250605060000"
    zshrc_path = Path("/home/user/.zshrc")

    # Call function
    result = backup_zshrc(zshrc_path)

    # Assertions
    expected_backup = Path("/home/user/.zshrc.bak-20250605060000")
    assert result == expected_backup
    mock_copy.assert_called_once_with(zshrc_path, expected_backup)


@patch("pathlib.Path.exists", return_value=True)
@patch("aws_pick.shell.get_zshrc_path")
@patch("aws_pick.shell.backup_shell_rc")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='# Some content\nexport AWS_PROFILE="old-profile"\n',
)
def test_update_aws_profile_existing(
    mock_file, mock_backup, mock_get_path, mock_exists
):
    """Test updating existing AWS_PROFILE."""
    # Setup mocks
    zshrc_path = Path("/home/user/.zshrc")
    mock_get_path.return_value = zshrc_path
    mock_backup.return_value = Path("/home/user/.zshrc.bak-20250605060000")

    # Call function
    success, backup_path = update_aws_profile("new-profile")

    # Assertions
    assert success is True
    assert backup_path == Path("/home/user/.zshrc.bak-20250605060000")
    mock_backup.assert_called_once_with(zshrc_path)

    # Check file write
    mock_file.assert_called_with(zshrc_path, "w")
    handle = mock_file()
    written_content = "".join(
        call_args[0][0] for call_args in handle.write.call_args_list
    )
    assert 'export AWS_PROFILE="new-profile"' in written_content


@patch("pathlib.Path.exists", return_value=True)
@patch("aws_pick.shell.get_zshrc_path")
@patch("aws_pick.shell.backup_shell_rc")
@patch("builtins.open", new_callable=mock_open, read_data="# Some content\n")
def test_update_aws_profile_new(mock_file, mock_backup, mock_get_path, mock_exists):
    """Test adding new AWS_PROFILE."""
    # Setup mocks
    zshrc_path = Path("/home/user/.zshrc")
    mock_get_path.return_value = zshrc_path
    mock_backup.return_value = Path("/home/user/.zshrc.bak-20250605060000")

    # Call function
    success, backup_path = update_aws_profile("new-profile")

    # Assertions
    assert success is True
    assert backup_path == Path("/home/user/.zshrc.bak-20250605060000")

    # Check file write
    mock_file.assert_called_with(zshrc_path, "w")
    handle = mock_file()
    written_content = "".join(
        call_args[0][0] for call_args in handle.write.call_args_list
    )
    assert 'export AWS_PROFILE="new-profile"' in written_content
    assert "# Added by AWS Pick" in written_content


@patch("pathlib.Path.exists", return_value=True)
@patch("aws_pick.shell.get_zshrc_path")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='export AWS_PROFILE="same-profile"\n',
)
def test_update_aws_profile_no_change(mock_file, mock_get_path, mock_exists):
    """Test when AWS_PROFILE is already set to the same value."""
    # Setup mocks
    zshrc_path = Path("/home/user/.zshrc")
    mock_get_path.return_value = zshrc_path

    # Call function
    success, backup_path = update_aws_profile("same-profile")

    # Assertions
    assert success is True
    assert backup_path is None

    # Check that file was not written
    mock_file.assert_called_with(zshrc_path, "r")
    handle = mock_file()
    handle.write.assert_not_called()


@patch("aws_pick.shell.get_zshrc_path")
def test_update_aws_profile_no_zshrc(mock_get_path):
    """Test when zshrc file doesn't exist."""
    # Setup mocks
    zshrc_path = Path("/home/user/.zshrc")
    mock_path = MagicMock()
    mock_path.exists.return_value = False
    mock_get_path.return_value = mock_path

    # Call function
    success, backup_path = update_aws_profile("new-profile")

    # Assertions
    assert success is False
    assert backup_path is None
