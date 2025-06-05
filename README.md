# AWS Profile Switcher

A simple CLI tool to easily switch between AWS profiles in your shell environment.

## Overview

AWS Profile Switcher (`awswitch`) is a command-line utility that helps you quickly switch between different AWS profiles defined in your `~/.aws/config` file. It automatically updates your shell environment by modifying the `AWS_PROFILE` environment variable in your `~/.zshrc` file.

## Features

- Lists all available AWS profiles from your `~/.aws/config` file with numbered options
- Allows selection by either number or profile name
- Validates input to ensure a valid profile is selected
- Updates your `~/.zshrc` file to set the selected profile as the default
- Creates backup files before modifying your `~/.zshrc`
- Ensures idempotency (no duplicate modifications if selecting the same profile)
- Provides clear logging of operations

## Installation

### Prerequisites

- Python 3.9 or higher
- Poetry (for development)

### Using pip

```bash
pip install aws-profile-switcher
```

### From source

```bash
git clone https://github.com/kkamji/aws-profile-switcher.git
cd aws-profile-switcher
poetry install
```

## Usage

Simply run the command:

```bash
awswitch
```

This will:
1. Display a list of available AWS profiles
2. Prompt you to select a profile by number or name
3. Update your `~/.zshrc` file to use the selected profile
4. Create a backup of your original `~/.zshrc` file

Example output:
```
Available AWS Profiles:
+-----+---------------+
| Num | Profile       |
+-----+---------------+
|  1  | default       |
|  2  | development   |
|  3  | production    |
|  4  | staging       |
+-----+---------------+

Enter profile number or name: 2
Selected profile: development
Updated ~/.zshrc with AWS_PROFILE=development
Backup created at ~/.zshrc.bak-20250605060000
```

## Development

This project uses Poetry for dependency management and packaging.

### Setup development environment

```bash
# Clone the repository
git clone https://github.com/kkamji/aws-profile-switcher.git
cd aws-profile-switcher

# Install dependencies
poetry install

# Setup direnv (optional)
echo "layout poetry" > .envrc
direnv allow
```

### Running tests

```bash
poetry run pytest
```

### Code formatting

```bash
poetry run black .
poetry run isort .
```

## Project Structure

```
aws-profile-switcher/
├── aws_profile_switcher/
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── config.py       # AWS config file parsing
│   └── shell.py        # Shell profile modification
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_shell.py
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
