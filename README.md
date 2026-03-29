# OpenSound

OpenSound is an experimental and educational project. It's a attempt to build a
package manager specifically for audio software — plugins, sounds, and presets.

## Why this exists

Every music producer knows the pain: you open a project from 5 or 10 years ago,
and it's full of missing plugins and lost sample packs. You spend hours
searching the internet for that one specific version of a VST that was only
available on some obscure forum.

Audio software deserves its own package manager. OpenSound is not trying to
invent a "new standard" for plugins. Instead, it's a way to unify existing sound
resources into one place, making them easily discoverable and installable.

The goal is simple: restore your entire production environment with a single
command.

```bash
opensound install -r requirements.txt
```

## Current Status

This is a work in progress. Currently, we are focusing on the Backend and basic
CLI features.

- Supports binary installation (VST3, CLAP, etc.) from YAML recipes.
- No source building yet.
- Focus is strictly on Linux for now, but the architecture is open for
  contributions and future support for macOS and Windows.

## Tech Stack

- **CLI**: Typer + Rich
- **Backend**: FastAPI (Asynchronous Registry)
- **Database**: PostgreSQL (SQLAlchemy + Asyncpg)
- **Data Format**: YAML Recipes

## Project Structure

- `cli/`: Command-line interface logic.
- `backend/`: API registry service and database.
- `recipes/`: Local YAML definitions for packages.

## Development

1. Install dependencies in editable mode:

   ```bash
   pip install -e .
   ```

2. Run tests:

   ```bash
   pytest
   ```

3. Test with a local recipe:

   ```bash
   opensound install --local recipes/FireFlySynth2-clap-linux-bin.yaml
   ```

4. Start the Backend (Development):
   ```bash
   uvicorn backend.main:app --reload
   ```

## Contributing

Contributions and feedback are welcome. Check out `AGENTS.md` for coding
guidelines and style rules.
