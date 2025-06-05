#!/usr/bin/env python3
"""
AWS Pick - A simple CLI tool to easily switch between AWS profiles in your shell environment.
This is a launcher script that calls the main function from the aws_pick package.
"""

import sys
from aws_pick.cli import main

if __name__ == "__main__":
    sys.exit(main())
