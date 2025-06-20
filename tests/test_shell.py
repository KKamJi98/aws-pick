"""Tests for the shell module."""

import os
import re
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from aws_pick.shell import (
    ShellConfig,
    backup_rc_file,
    detect_shell,
    generate_export_command,
    get_rc_path,
    get_shell_configs,
    update_aws_profile,
)


def test_shell_config():
    """Test ShellConfig class."""
    config = ShellConfig(
        "bash", Path("/home/user/.bashrc"), 'export AWS_PROFILE="{profile_name}"'
    )

    # Test get_profile_line
    assert (
        config.get_profile_line("test-profile") == 'export AWS_PROFILE="test-profile"'
    )

    # Test get_profile_pattern
    pattern = config.get_profile_pattern()
    assert pattern.search('export AWS_PROFILE="old-profile"')
    assert not pattern.search('# export AWS_PROFILE="old-profile"')


@patch("aws_pick.shell.os.environ")
@patch("aws_pick.shell.subprocess.run")
def test_detect_shell_from_env(mock_run, mock_environ):
    """Test detecting shell from SHELL environment variable."""
    # Setup mock
    mock_environ.get.return_value = "/bin/zsh"

    # Call function
    result = detect_shell()

    # Assertions
    assert result == "zsh"
    mock_environ.get.assert_called_with("SHELL", "")
    mock_run.assert_not_called()


@patch("aws_pick.shell.os.environ")
@patch("aws_pick.shell.subprocess.run")
@patch("aws_pick.shell.os.getppid")
def test_detect_shell_from_process(mock_getppid, mock_run, mock_environ):
    """Test detecting shell from parent process."""
    # Setup mocks
    mock_environ.get.return_value = ""
    mock_getppid.return_value = 12345
    mock_process = MagicMock()
    mock_process.stdout = "bash\n"
    mock_run.return_value = mock_process

    # Call function
    result = detect_shell()

    # Assertions
    assert result == "bash"
    mock_environ.get.assert_called_with("SHELL", "")
    mock_run.assert_called_with(
        ["ps", "-p", "12345", "-o", "comm="], capture_output=True, text=True, check=True
    )


def test_get_shell_configs():
    """Test getting shell configurations."""
    configs = get_shell_configs()

    # Check that we have configs for common shells
    assert "bash" in configs
    assert "zsh" in configs
    assert "fish" in configs

    # Check bash config
    bash_config = configs["bash"]
    assert bash_config.name == "bash"
    assert bash_config.rc_path == Path.home() / ".bashrc"
    assert 'export AWS_PROFILE="test"' == bash_config.get_profile_line("test")

    # Check fish config
    fish_config = configs["fish"]
    assert fish_config.name == "fish"
    assert fish_config.rc_path == Path.home() / ".config" / "fish" / "config.fish"
    assert 'set -gx AWS_PROFILE "test"' == fish_config.get_profile_line("test")


@patch("aws_pick.shell.detect_shell")
def test_get_rc_path(mock_detect_shell):
    """Test getting RC path for different shells."""
    # Test with explicit shell name
    rc_path, shell_config = get_rc_path("zsh")
    assert rc_path == Path.home() / ".zshrc"
    assert shell_config.name == "zsh"
    mock_detect_shell.assert_not_called()

    # Test with auto-detection
    mock_detect_shell.return_value = "bash"
    rc_path, shell_config = get_rc_path()
    assert rc_path == Path.home() / ".bashrc"
    assert shell_config.name == "bash"
    mock_detect_shell.assert_called_once()

    # Test with unknown shell (should fall back to bash)
    rc_path, shell_config = get_rc_path("unknown-shell")
    assert rc_path == Path.home() / ".bashrc"
    assert shell_config.name == "bash"


@patch("aws_pick.shell.shutil.copy2")
@patch("aws_pick.shell.datetime")
def test_backup_rc_file(mock_datetime, mock_copy):
    """Test backing up RC file."""
    # Setup mocks
    mock_datetime.datetime.now.return_value.strftime.return_value = "20250605060000"
    rc_path = Path("/home/user/.bashrc")

    # Call function
    result = backup_rc_file(rc_path)

    # Assertions
    expected_backup = Path("/home/user/.bashrc.bak-20250605060000")
    assert result == expected_backup
    mock_copy.assert_called_once_with(rc_path, expected_backup)


@patch("aws_pick.shell.get_rc_path")
@patch("aws_pick.shell.backup_rc_file")
@patch("pathlib.Path.exists", return_value=True)
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='# Some content\nexport AWS_PROFILE="old-profile"\n',
)
def test_update_aws_profile_bash(mock_file, mock_exists, mock_backup, mock_get_rc_path):
    """Test updating AWS_PROFILE in bash."""
    # Setup mocks
    rc_path = Path("/home/user/.bashrc")
    shell_config = ShellConfig("bash", rc_path, 'export AWS_PROFILE="{profile_name}"')
    mock_get_rc_path.return_value = (rc_path, shell_config)
    mock_backup.return_value = Path("/home/user/.bashrc.bak-20250605060000")

    # Call function
    success, backup_path = update_aws_profile("new-profile", "bash")

    # Assertions
    assert success is True
    assert backup_path == Path("/home/user/.bashrc.bak-20250605060000")
    mock_backup.assert_called_once_with(rc_path)

    # Check file write
    mock_file.assert_called_with(rc_path, "w")
    handle = mock_file()
    written_content = "".join(
        call_args[0][0] for call_args in handle.write.call_args_list
    )
    assert 'export AWS_PROFILE="new-profile"' in written_content


@patch("aws_pick.shell.get_rc_path")
@patch("aws_pick.shell.backup_rc_file")
@patch("pathlib.Path.exists", return_value=True)
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='# Some content\nset -gx AWS_PROFILE "old-profile"\n',
)
def test_update_aws_profile_fish(mock_file, mock_exists, mock_backup, mock_get_rc_path):
    """Test updating AWS_PROFILE in fish."""
    # Setup mocks
    rc_path = Path("/home/user/.config/fish/config.fish")
    shell_config = ShellConfig("fish", rc_path, 'set -gx AWS_PROFILE "{profile_name}"')
    mock_get_rc_path.return_value = (rc_path, shell_config)
    mock_backup.return_value = Path(
        "/home/user/.config/fish/config.fish.bak-20250605060000"
    )

    # Call function
    success, backup_path = update_aws_profile("new-profile", "fish")

    # Assertions
    assert success is True
    assert backup_path == Path("/home/user/.config/fish/config.fish.bak-20250605060000")
    mock_backup.assert_called_once_with(rc_path)

    # Check file write
    mock_file.assert_called_with(rc_path, "w")
    handle = mock_file()
    written_content = "".join(
        call_args[0][0] for call_args in handle.write.call_args_list
    )
    assert 'set -gx AWS_PROFILE "new-profile"' in written_content


@patch("aws_pick.shell.get_rc_path")
@patch("pathlib.Path.exists", return_value=True)
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='export AWS_PROFILE="same-profile"\n',
)
def test_update_aws_profile_no_change(mock_file, mock_exists, mock_get_rc_path):
    """Test when AWS_PROFILE is already set to the same value."""
    # Setup mocks
    rc_path = Path("/home/user/.bashrc")
    shell_config = ShellConfig("bash", rc_path, 'export AWS_PROFILE="{profile_name}"')
    mock_get_rc_path.return_value = (rc_path, shell_config)

    # Call function
    success, backup_path = update_aws_profile("same-profile", "bash")

    # Assertions
    assert success is True
    assert backup_path is None

    # Check that file was not written
    mock_file.assert_called_with(rc_path, "r")
    handle = mock_file()
    handle.write.assert_not_called()


@patch("aws_pick.shell.get_rc_path")
def test_update_aws_profile_no_rc_file_bash(mock_get_rc_path):
    """Test when RC file doesn't exist for bash."""
    # Setup mocks
    rc_path = Path("/home/user/.bashrc")
    shell_config = ShellConfig("bash", rc_path, 'export AWS_PROFILE="{profile_name}"')
    mock_get_rc_path.return_value = (rc_path, shell_config)

    # Mock the path's exists method
    mock_path = MagicMock()
    mock_path.exists.return_value = False
    mock_get_rc_path.return_value = (mock_path, shell_config)

    # Call function
    success, backup_path = update_aws_profile("new-profile", "bash")

    # Assertions
    assert success is False
    assert backup_path is None


@patch("aws_pick.shell.get_rc_path")
@patch("aws_pick.shell.backup_rc_file")
@patch("pathlib.Path.exists")
@patch("pathlib.Path.mkdir")
@patch("builtins.open", new_callable=mock_open)
def test_update_aws_profile_no_rc_file_fish(
    mock_file, mock_mkdir, mock_exists, mock_backup, mock_get_rc_path
):
    """Test when RC file doesn't exist for fish."""
    # Setup mocks
    rc_path = Path("/home/user/.config/fish/config.fish")
    shell_config = ShellConfig("fish", rc_path, 'set -gx AWS_PROFILE "{profile_name}"')
    mock_get_rc_path.return_value = (rc_path, shell_config)

    # Mock path operations
    mock_exists.return_value = False
    mock_mkdir.return_value = None
    mock_backup.return_value = Path(
        "/home/user/.config/fish/config.fish.bak-20250605060000"
    )

    # Call function
    success, backup_path = update_aws_profile("new-profile", "fish")

    # Assertions
    assert success is True
    mock_mkdir.assert_called_with(parents=True, exist_ok=True)
    mock_file.assert_called_with(rc_path, "w")
    handle = mock_file()
    handle.write.assert_called()
    written_content = "".join(
        call_args[0][0] for call_args in handle.write.call_args_list
    )
    assert "# Created by AWS Pick" in written_content


def test_generate_export_command():
    """Test generating export command for different shells."""

    bash_cmd = generate_export_command("dev", "bash")
    zsh_cmd = generate_export_command("dev", "zsh")
    fish_cmd = generate_export_command("dev", "fish")

    assert bash_cmd == 'export AWS_PROFILE="dev"'
    assert zsh_cmd == 'export AWS_PROFILE="dev"'
    assert fish_cmd == 'set -gx AWS_PROFILE "dev"'
