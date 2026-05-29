"""BrainSTEM integration helpers for experiment logging.

This module wraps the official BrainSTEM Python API tool so scripts in this
repository can create, query, and edit BrainSTEM records without opening the
web interface.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from typing import Any, Optional

try:
    from brainstem_api_tools import BrainstemClient
except ImportError:  # pragma: no cover - import guidance at runtime
    BrainstemClient = None


logger = logging.getLogger(__name__)


class BrainstemUnavailableError(RuntimeError):
    """Raised when the BrainSTEM Python API tool is not installed."""


class BrainstemLoggingSystem:
    """High-level wrapper around the official BrainSTEM Python client."""

    def __init__(
        self,
        token: Optional[str] = None,
        url: str = "https://www.brainstem.org/",
        headless: bool = False,
    ) -> None:
        if BrainstemClient is None:
            raise BrainstemUnavailableError(
                "brainstem_python_api_tools is not installed. "
                "Install it with: pip install brainstem_python_api_tools"
            )

        kwargs: dict[str, Any] = {"url": url}
        if token:
            kwargs["token"] = token
        else:
            kwargs["headless"] = headless

        self.client = BrainstemClient(**kwargs)
        self.url = url

    @classmethod
    def from_env(cls) -> "BrainstemLoggingSystem":
        token = os.getenv("BRAINSTEM_TOKEN")
        url = os.getenv("BRAINSTEM_URL", "https://www.brainstem.org/")
        headless = os.getenv("BRAINSTEM_HEADLESS", "0").strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
        }
        return cls(token=token, url=url, headless=headless)

    def load_records(
        self,
        model: str,
        *,
        portal: str = "private",
        record_id: Optional[str] = None,
        filters: Optional[dict[str, Any]] = None,
        include: Optional[list[str]] = None,
        sort: Optional[list[str]] = None,
        load_all: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> dict[str, Any]:
        response = self.client.load(
            model,
            portal=portal,
            id=record_id,
            filters=filters,
            include=include,
            sort=sort,
            load_all=load_all,
            limit=limit,
            offset=offset,
        )
        return self._json_payload(response)

    def create_record(self, model: str, data: dict[str, Any]) -> dict[str, Any]:
        response = self.client.save(model, data=data)
        return self._json_payload(response)

    def update_record(self, model: str, record_id: str, data: dict[str, Any]) -> dict[str, Any]:
        response = self.client.save(model, id=record_id, data=data)
        return self._json_payload(response)

    def delete_record(self, model: str, record_id: str) -> int:
        response = self.client.delete(model, id=record_id)
        return int(response.status_code)

    def create_session(
        self,
        *,
        name: str,
        project_ids: list[str],
        description: Optional[str] = None,
        date_time: Optional[str] = None,
        tags: Optional[list[str]] = None,
        extra_fields: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": name,
            "projects": project_ids,
        }
        if description is not None:
            payload["description"] = description
        if date_time is not None:
            payload["date_time"] = date_time
        if tags is not None:
            payload["tags"] = tags
        if extra_fields is not None:
            payload["extra_fields"] = extra_fields

        return self.create_record("session", payload)

    def update_session(self, session_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self.update_record("session", session_id, data)

    def create_subject_log(
        self,
        *,
        subject_id: str,
        log_type: str,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "subject": subject_id,
            "type": log_type,
        }
        if description is not None:
            payload["description"] = description
        return self.create_record("subjectlog", payload)

    def add_subject_log_entry(
        self,
        *,
        log_id: str,
        details: dict[str, Any],
        date_time: Optional[str] = None,
        notes: Optional[str] = None,
        start_date_time: Optional[str] = None,
        end_date_time: Optional[str] = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"details": details}

        if date_time:
            payload["date_time"] = date_time
        if start_date_time:
            payload["start_date_time"] = start_date_time
        if end_date_time:
            payload["end_date_time"] = end_date_time
        if notes is not None:
            payload["notes"] = notes

        response = self.client.save("subjectlog", id=log_id, options="add_entry", data=payload)
        return self._json_payload(response)

    @staticmethod
    def _json_payload(response: Any) -> dict[str, Any]:
        if isinstance(response, dict):
            return response
        if hasattr(response, "json"):
            return response.json()
        raise TypeError(f"Unexpected BrainSTEM response type: {type(response)!r}")


def _parse_json_arg(value: str, argument_name: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for {argument_name}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{argument_name} must decode to a JSON object")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BrainSTEM experiment logging helper for BrainSTEM Automation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--token", default=None, help="BrainSTEM PAT (or use BRAINSTEM_TOKEN)")
    parser.add_argument("--url", default=os.getenv("BRAINSTEM_URL", "https://www.brainstem.org/"))
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Use device-code flow without opening a browser (ignored when --token is used)",
    )
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    sub = parser.add_subparsers(dest="command", required=True)

    p_list_projects = sub.add_parser("list-projects", help="List projects")
    p_list_projects.add_argument("--public", action="store_true", help="Query public portal")
    p_list_projects.add_argument("--name-contains", default=None)

    p_list_sessions = sub.add_parser("list-sessions", help="List sessions")
    p_list_sessions.add_argument("--public", action="store_true", help="Query public portal")
    p_list_sessions.add_argument("--project-id", default=None, help="Filter by project UUID")
    p_list_sessions.add_argument("--name-contains", default=None)
    p_list_sessions.add_argument("--limit", type=int, default=None)
    p_list_sessions.add_argument("--offset", type=int, default=None)

    p_create_session = sub.add_parser("create-session", help="Create a session")
    p_create_session.add_argument("--name", required=True)
    p_create_session.add_argument("--project-id", action="append", required=True)
    p_create_session.add_argument("--description", default=None)
    p_create_session.add_argument("--date-time", default=None, help="ISO 8601 datetime")
    p_create_session.add_argument("--tags-json", default=None, help='JSON array string, e.g. ["tag1","tag2"]')
    p_create_session.add_argument("--extra-fields-json", default=None, help='JSON object string')

    p_update_session = sub.add_parser("update-session", help="Patch an existing session")
    p_update_session.add_argument("--session-id", required=True)
    p_update_session.add_argument("--description", default=None)
    p_update_session.add_argument("--date-time", default=None)
    p_update_session.add_argument("--tags-json", default=None, help='JSON array string')
    p_update_session.add_argument("--extra-fields-json", default=None, help='JSON object string')

    p_create_log = sub.add_parser("create-subject-log", help="Create a subject log")
    p_create_log.add_argument("--subject-id", required=True)
    p_create_log.add_argument("--type", required=True, help="Subject log type")
    p_create_log.add_argument("--description", default=None)

    p_add_entry = sub.add_parser("add-subject-log-entry", help="Add an entry to a subject log")
    p_add_entry.add_argument("--log-id", required=True)
    p_add_entry.add_argument("--details-json", required=True, help='JSON object, e.g. {"weight":23.4}')
    p_add_entry.add_argument("--date-time", default=None, help="ISO 8601 for instantaneous entry")
    p_add_entry.add_argument("--start-date-time", default=None, help="ISO 8601 for interval entry")
    p_add_entry.add_argument("--end-date-time", default=None, help="ISO 8601 for interval entry")
    p_add_entry.add_argument("--notes", default=None)

    p_generic_load = sub.add_parser("load", help="Generic model loader")
    p_generic_load.add_argument("--model", required=True)
    p_generic_load.add_argument("--id", default=None)
    p_generic_load.add_argument("--public", action="store_true")
    p_generic_load.add_argument("--filters-json", default=None)
    p_generic_load.add_argument("--include", action="append", default=None)
    p_generic_load.add_argument("--sort", action="append", default=None)
    p_generic_load.add_argument("--load-all", action="store_true")
    p_generic_load.add_argument("--limit", type=int, default=None)
    p_generic_load.add_argument("--offset", type=int, default=None)

    return parser


def _parse_tags_json(tags_json: Optional[str]) -> Optional[list[str]]:
    if tags_json is None:
        return None
    parsed = json.loads(tags_json)
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("--tags-json must be a JSON array of strings")
    return parsed


def run_cli(args: argparse.Namespace) -> int:
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s %(levelname)s %(message)s")

    token = args.token if args.token else os.getenv("BRAINSTEM_TOKEN")
    client = BrainstemLoggingSystem(token=token, url=args.url, headless=args.headless)

    if args.command == "list-projects":
        filters = {"name.icontains": args.name_contains} if args.name_contains else None
        portal = "public" if args.public else "private"
        payload = client.load_records("project", portal=portal, filters=filters, load_all=True)
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "list-sessions":
        filters: dict[str, Any] = {}
        if args.project_id:
            filters["projects"] = args.project_id
        if args.name_contains:
            filters["name.icontains"] = args.name_contains
        portal = "public" if args.public else "private"
        payload = client.load_records(
            "session",
            portal=portal,
            filters=filters or None,
            limit=args.limit,
            offset=args.offset,
            load_all=(args.limit is None and args.offset is None),
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "create-session":
        tags = _parse_tags_json(args.tags_json)
        extra_fields = _parse_json_arg(args.extra_fields_json, "--extra-fields-json") if args.extra_fields_json else None
        payload = client.create_session(
            name=args.name,
            project_ids=args.project_id,
            description=args.description,
            date_time=args.date_time,
            tags=tags,
            extra_fields=extra_fields,
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "update-session":
        update_data: dict[str, Any] = {}
        if args.description is not None:
            update_data["description"] = args.description
        if args.date_time is not None:
            update_data["date_time"] = args.date_time
        if args.tags_json is not None:
            update_data["tags"] = _parse_tags_json(args.tags_json)
        if args.extra_fields_json is not None:
            update_data["extra_fields"] = _parse_json_arg(args.extra_fields_json, "--extra-fields-json")
        if not update_data:
            raise ValueError("No update fields provided")
        payload = client.update_session(args.session_id, update_data)
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "create-subject-log":
        payload = client.create_subject_log(
            subject_id=args.subject_id,
            log_type=args.type,
            description=args.description,
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "add-subject-log-entry":
        details = _parse_json_arg(args.details_json, "--details-json")
        payload = client.add_subject_log_entry(
            log_id=args.log_id,
            details=details,
            date_time=args.date_time,
            start_date_time=args.start_date_time,
            end_date_time=args.end_date_time,
            notes=args.notes,
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "load":
        filters = _parse_json_arg(args.filters_json, "--filters-json") if args.filters_json else None
        portal = "public" if args.public else "private"
        payload = client.load_records(
            args.model,
            portal=portal,
            record_id=args.id,
            filters=filters,
            include=args.include,
            sort=args.sort,
            load_all=args.load_all,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps(payload, indent=2))
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return run_cli(args)
    except BrainstemUnavailableError as exc:
        logger.error(str(exc))
        return 2
    except Exception as exc:  # pragma: no cover - CLI safety net
        logger.exception("BrainSTEM command failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
