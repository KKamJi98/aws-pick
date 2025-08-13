# AWS Pick

A simple CLI tool to easily switch between AWS profiles in your shell environment.

```
INFO: Found 4 AWS profiles
  AWS Profiles
┏━━━━━┳━━━━━━━━━━━┓
┃ No. ┃ Profile   ┃
┡━━━━━╇━━━━━━━━━━━┩
│   1 │ default   │
│   2 │ dev       │
│   3 │ stg       │
│   4 │ prod      │
└─────┴───────────┘
Enter profile number or name:
```

## Overview

AWS Pick (`awspick`) is a command-line utility that helps you quickly switch between different AWS profiles defined in your `~/.aws/config` file. It automatically updates your shell environment by modifying the `AWS_PROFILE` environment variable in your shell configuration file.



## Features

- Automatically groups and color-codes profiles by environment (dev, stg, prod, preprod).
- Lists all available AWS profiles from your `~/.aws/config` file with numbered options
- Allows selection by either number or profile name
- Validates input to ensure a valid profile is selected
- Supports multiple shells:
  - Bash (`~/.bashrc`)
  - Zsh (`~/.zshrc`)
  - Fish (`~/.config/fish/config.fish`)
- Updates your shell configuration file to set the selected profile as the default
- Creates backup files before modifying your configuration
- Ensures idempotency (no duplicate modifications if selecting the same profile)
- Prints a shell command for immediate application
- Provides clear logging of operations
- Handles errors gracefully with informative messages
- Supports case-insensitive profile name matching
- Filtering and grouping via CLI flags or env vars

## How It Works

- Read profiles: Parses `~/.aws/config` and collects `default` and sections named `profile <name>`.
- Filter list: Applies include/exclude patterns from CLI flags or env vars. Patterns can be substrings or regular expressions (`--regex`), with optional case sensitivity (`--case-sensitive`).
- Group profiles: Groups names using ordered rules. Default order among defined groups: `prod`, `stg`, `dev`, `preprod` (so `preprod` is second from bottom). `others` is always displayed last. First matching rule wins; unmatched profiles go to `others`.
- Display and select: Renders a numbered table via `rich`. Input accepts either the number (1-based, current display order) or the profile name (case-insensitive match supported).
- Apply to shell: Detects your shell (`bash`, `zsh`, `fish`) and writes or replaces a single `AWS_PROFILE="<name>"` line in the corresponding rc file. Creates a timestamped backup and avoids duplicate changes if the same profile is already set.
- Export command: Prints the exact shell command to stdout so you can run `eval "$(awspick)"` to apply immediately in the current session.

## Installation

### Prerequisites

- Python 3.9 or higher
- uv (for development)

### From source

```bash
git clone https://github.com/KKamJi98/aws-pick.git
cd aws-pick
uv venv .venv
uv pip install -e .[dev]
```

## Usage

Simply run the command:

```bash
awspick
```

Or invoke the launcher script directly:

```bash
python3 /path/to/aws_pick.py
```

To apply the profile immediately in your current shell, run:

```bash
eval "$(python3 /path/to/aws_pick.py)"
```

All prompts and logs are printed to **stderr**, while the final
`export AWS_PROFILE="..."` command is printed to **stdout**. This
ensures the menu is visible when using command substitution.

Add a wrapper function to your shell to avoid typing `eval` each time:

```bash
function awspick() {
    eval "$(python3 /your/path/to/aws_pick.py)"
}
```

Use this function to select and apply a profile in one step.

This will:
1. Display a list of available AWS profiles
2. Prompt you to select a profile by number or name
3. Update your shell configuration file to use the selected profile
4. Create a backup of your original configuration file

Example output:
```
Available AWS Profiles:
| Num | Profile       |
|-----|---------------|
|  1  | default       |
|  2  | development   |
|  3  | production    |
|  4  | staging       |

Enter profile number or name: 2
Selected profile: development
Updated ~/.zshrc with AWS_PROFILE=development
Backup created at ~/.zshrc.bak-20250605060000
Configuration reloaded automatically.
```

## Filtering and Grouping

You can control which profiles are shown and how they are grouped.

- `-f, --filter`: Only show profiles matching any given substring.
- `-x, --exclude`: Exclude profiles matching any given substring.
- `-g, --groups`: Only display specific groups (e.g., `prod,dev`).
- `--group-rules`: Customize grouping rules. Order matters.
- `--regex`: Treat `--filter`/`--exclude` as regular expressions.
- `--case-sensitive`: Make matches case-sensitive.

Examples:

```bash
# Show only prod and dev groups
awspick --groups prod,dev

# Show profiles containing "tooling" but not "legacy"
awspick -f tooling -x legacy

# Regex example: include profiles ending with -admin, exclude sandbox
awspick --regex -f '.*-admin$' -x sandbox

# Custom grouping: order ensures first match wins
awspick --group-rules 'preprod=preprod;prod=prod,production;stg=stg;dev=dev'
```

Environment variables (useful per-host/per-shell):

```bash
export AWSPICK_FILTER="tooling,admin"
export AWSPICK_EXCLUDE="legacy"
export AWSPICK_GROUPS_SHOW="prod,dev"
export AWSPICK_GROUP_RULES='preprod=preprod;prod=prod;stg=stg;dev=dev'
export AWSPICK_REGEX=0             # 1/true to enable regex
export AWSPICK_CASE_SENSITIVE=0    # 1/true for case-sensitive
```

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Setup development environment

```bash
# Clone the repository
git clone https://github.com/KKamJi98/aws-pick.git
cd aws-pick

# Install dependencies
uv venv .venv
uv pip install -e .[dev]

# Setup direnv (optional)
direnv allow
```

### Running tests

```bash
pytest
```

### Code formatting

```bash
black .
isort .
```

## Project Structure

```
aws-pick/
├── aws_pick.py       # Single-file launcher script
├── aws_pick/
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── config.py       # AWS config file parsing
│   └── shell.py        # Shell profile modification
├── pyproject.toml      # Project metadata and dependencies
├── README.md
└── LICENSE
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes following the commit convention
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Commit Convention

This project follows the Conventional Commits specification:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Example: `feat(cli): implement number and name selection logic`
