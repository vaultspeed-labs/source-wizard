#!/usr/bin/env python3
"""
VaultSpeed Source Wizard - Main Application Entry Point

Run this file to start the Streamlit application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vaultspeed_wizard.main import main

if __name__ == "__main__":
    main()
