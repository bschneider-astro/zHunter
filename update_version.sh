#!/bin/bash

version=$1

# Replace in __init__.py
sed -i -e "s/\(__version__ = \).*/\1\"$1\"/" src/zhunter/__init__.py
rm src/zhunter/__init__.py-e

# Replace in pyproject.toml
sed -i -e "s/\(version = \).*/\1\"$1\"/" pyproject.toml
rm pyproject.toml-e
