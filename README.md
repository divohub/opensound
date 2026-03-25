# OpenSound

OpenSound is a package manager for musicians, producers, and sound designers. It addresses fragmented plugin distribution and manual sample pack management on Linux.

Inspired by Homebrew and AUR, but built specifically for VSTs, LV2s, sound packs, and presets.

## Vision

The goal is to restore an entire audio production environment with a single command:
```bash
opensound install -r requirements.txt
```

## Tech Stack
- CLI: Typer, Rich
- Backend: FastAPI (Asynchronous Registry)
- Database: PostgreSQL (SQLAlchemy + Asyncpg)
- Data Format: YAML Recipes

## Project Structure
- `cli/`: Command-line interface logic.
- `backend/`: API service and database registry.
- `recipes/`: Local YAML definitions for packages.

## Installation

1. Install dependencies in editable mode:
   ```bash
   pip install -e .
   ```

2. Run the CLI (local test):
   ```bash
   python3 -m cli.main install --local recipes/vital.yaml
   ```

3. Start the Backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
