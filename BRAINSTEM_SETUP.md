# BrainSTEM Python Integration

This repository now includes a BrainSTEM integration script:

- `brainstem_logging.py`

It uses the official BrainSTEM Python API tool (`brainstem_python_api_tools`) so you can create and edit records from Python/terminal instead of the web UI.

## 1) Install dependency

```bash
pip install brainstem_python_api_tools
```

In this environment, Python is available as:

```powershell
python
```

## 2) Authenticate

You have three options:

1. Browser login flow (2FA-safe, token cached by official tool):

```bash
python brainstem_logging.py list-projects
```

2. Headless login flow (prints code and URL):

```bash
python brainstem_logging.py --headless list-projects
```

3. Personal Access Token (recommended for automation):

```bash
$env:BRAINSTEM_TOKEN="YOUR_TOKEN"
python .\brainstem_logging.py list-projects
```

Optional custom server URL:

```bash
$env:BRAINSTEM_URL="https://www.brainstem.org/"
```

If you prefer `python` command instead of full path, replace the command prefix accordingly.

## 3) Common commands

List records:

```bash
python brainstem_logging.py list-projects
python brainstem_logging.py list-sessions --project-id <project-uuid>
python brainstem_logging.py load --model subject --filters-json "{\"name.icontains\": \"SUBJECT_PREFIX\"}" --load-all
```

Create and edit sessions:

```bash
python brainstem_logging.py create-session --name ExampleSession_YYYYMMDD_HHMMSS --project-id <project-uuid> --description "Example session created via API"
python brainstem_logging.py update-session --session-id <session-uuid> --description "Re-annotated after QC"
```

Create and update subject logs:

```bash
python brainstem_logging.py create-subject-log --subject-id <subject-uuid> --type Weighing --description "Daily weights"
python brainstem_logging.py add-subject-log-entry --log-id <subjectlog-uuid> --date-time 2026-05-29T10:00:00Z --details-json "{\"weight\": 24.6}" --notes "pre-task"
```

For interval style log types:

```bash
python brainstem_logging.py add-subject-log-entry --log-id <subjectlog-uuid> --start-date-time 2026-05-29T09:00:00Z --end-date-time 2026-05-29T10:00:00Z --details-json "{\"waterAmount\": 1.2}"
```

## 4) Use from Python code

```python
from brainstem_logging import BrainstemLoggingSystem

bs = BrainstemLoggingSystem.from_env()

# Load sessions
sessions = bs.load_records("session", filters={"name.icontains": "PA2"}, load_all=True)

# Create one session
created = bs.create_session(
    name="ExampleSession_YYYYMMDD_HHMMSS",
    project_ids=["<project-uuid>"],
    description="Created from analysis pipeline",
)

# Add one subject log entry
bs.add_subject_log_entry(
    log_id="<subjectlog-uuid>",
    date_time="2026-05-29T10:00:00Z",
    details={"weight": 24.6},
    notes="auto-imported",
)
```

## Notes

- Keep `BRAINSTEM_TOKEN` out of git.
- BrainSTEM permissions still apply (403 if your user cannot edit the project/subject).
- Datetimes should be ISO 8601.
