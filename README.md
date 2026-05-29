# BrainSTEM Automation

Standalone Python automation project for BrainSTEM logging and metadata updates.

## Files

- `brainstem_logging.py`: BrainSTEM client wrapper + CLI
- `BRAINSTEM_SETUP.md`: setup and command examples

## Quick Start

1. Create and activate a virtual environment
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Authenticate and run:

```powershell
$env:BRAINSTEM_TOKEN="YOUR_TOKEN"
python .\brainstem_logging.py list-projects
```

## Repository

This folder is an independent git repository.
