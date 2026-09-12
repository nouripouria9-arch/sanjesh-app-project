# Sanjesh App — Beta

A desktop management and analytics application for university entrance exam (Konkur) candidate data, built with Python and a modular PySide6 architecture.

> **Status: Beta** — This repository contains the current beta version of the project and is intended to evolve through continuous development, testing, refinement, and feature updates.

## Overview

Sanjesh App is designed as a structured desktop system for managing candidates, exam scores, exam years, analytics, reports, and data exchange. The project separates the user interface, business logic, data-access layer, analytics, reporting, and configuration so that the application can be expanded over time.

## Main Features

- Candidate registration and management
- Candidate search, filtering, sorting, and validation
- Subject score management
- Statistical analysis including mean, median, standard deviation, quartiles, and distributions
- Data visualization with Matplotlib
- Comparison between exam years
- CSV, Excel, and JSON import/export
- Report generation
- SQLite database management and backup/restore support
- Activity logging
- Light and dark application themes
- Automated tests with pytest

## Technology Stack

- **Python 3.10+**
- **PySide6 / Qt6** for the desktop graphical interface
- **SQLAlchemy 2.0** for database access
- **SQLite3** as the database engine
- **Pandas / NumPy** for data processing and analytics
- **Matplotlib** for charts and visualization
- **OpenPyXL** for Excel support
- **qrcode** for QR-code functionality
- **pytest** for testing

## Project Structure

```text
.
├── app/
│   ├── analytics/       # Statistical and analytical processing
│   ├── config/          # Settings and logging configuration
│   ├── database/        # Database engine and session management
│   ├── models/          # Application data models
│   ├── repositories/    # Data access and persistence operations
│   ├── reports/         # Report generation
│   ├── services/        # Business logic and import/export services
│   └── ui/              # PySide6 interface, pages, dialogs, and widgets
├── data/                # Local application settings/data files
├── tests/               # Automated tests
├── pyproject.toml
├── requirements.txt
└── ssanjesh-app.py      # Main application launcher
```

## Installation

Create a virtual environment and install the project dependencies:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

## Run

Start the application with:

```bash
python ssanjesh-app.py
```

## Testing

Run the test suite with:

```bash
pytest tests/ -v
```

## Beta Development Roadmap

The project is being developed iteratively. Planned work may include improving reliability, expanding analytics, refining the graphical interface, strengthening validation and testing, improving performance, and adding new capabilities based on future development needs.

## Versioning and Updates

This repository is intended to receive continuous updates. The codebase currently represents a **Beta** stage rather than a final release. Future commits may improve architecture, functionality, performance, usability, documentation, and test coverage.

## Important Note

The project source code from the submitted beta package is included without changing its program logic or implementation. The original launcher file `run.py` has only been renamed to `ssanjesh-app.py` as requested.

Generated runtime/cache artifacts such as Python bytecode caches, test caches, local database files, and application logs are not included in the repository because they are generated during execution rather than being source project files.

## Author

**Pouria Nouri**  
Bachelor's Degree Student in Computer Engineering  
Focus: Software Development, Artificial Intelligence, Computer Vision, and Application Development
