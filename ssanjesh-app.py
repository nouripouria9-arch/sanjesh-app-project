#!/usr/bin/env python3
"""
Sanjesh — University Entrance Exam Management System.

Launch this file to start the application.
"""

import sys
from pathlib import Path

# Ensure the project root is on the Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.main import main

if __name__ == "__main__":
    sys.exit(main())