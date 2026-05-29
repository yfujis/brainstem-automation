# BrainSTEM Automation

Standalone Python automation utilities for BrainSTEM logging and metadata updates.

## Files

- `brainstem_logging.py`: BrainSTEM client wrapper + CLI
- `BRAINSTEM_SETUP.md`: Setup and command examples

## Quick Start

1. Create and activate a virtual environment.
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

This folder is an independent Git repository.

For usage details, see [my blog post](https://yukifujishima.com/blog/2026/05/29/brainstem-automation-by-talking-to-an-llm).