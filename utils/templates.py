# templates.py - auto-generated
# utils/templates.py
"""
Response templates and helpers for RTI_Agents.
Central place to format agent outputs consistently for APIs / logs.
"""

from __future__ import annotations
import datetime
import json
from typing import Any, Dict, Optional


def _utc_now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class ResponseTemplates:
    """
    Utilities to create uniform responses across agents.
    Each method returns a plain dict (easily serializable to JSON).
    """

    @staticmethod
    def classifier_response(department: str, confidence: str, notes: str = "") -> Dict[str, Any]:
        return {
            "agent": "ClassifierAgent",
            "timestamp": _utc_now_iso(),
            "result": {
                "department": department,
                "confidence": confidence,
                "notes": notes or ""
            }
        }

    @staticmethod
    def formatter_response(formatted_query: str, language: str = "en") -> Dict[str, Any]:
        return {
            "agent": "FormatterAgent",
            "timestamp": _utc_now_iso(),
            "result": {
                "formatted_query": formatted_query,
                "language": language
            }
        }

    @staticmethod
    def info_fetcher_response(status: str, info: Optional[str] = None, notes: str = "") -> Dict[str, Any]:
        return {
            "agent": "InfoFetcherAgent",
            "timestamp": _utc_now_iso(),
            "result": {
                "status": status,
                "info": info or "",
                "notes": notes or ""
            }
        }

    @staticmethod
    def tracker_response(tracking_id: str, status: str, last_updated: Optional[str] = None, notes: str = "") -> Dict[str, Any]:
        return {
            "agent": "TrackerAgent",
            "timestamp": _utc_now_iso(),
            "result": {
                "tracking_id": tracking_id,
                "status": status,
                "last_updated": last_updated or _utc_now_iso(),
                "notes": notes or ""
            }
        }

    @staticmethod
    def error_response(agent: str, message: str, details: Optional[str] = None) -> Dict[str, Any]:
        return {
            "agent": agent,
            "timestamp": _utc_now_iso(),
            "error": {
                "message": message,
                "details": details or ""
            }
        }

    @staticmethod
    def memory_snapshot(session_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "agent": "MemoryManager",
            "timestamp": _utc_now_iso(),
            "session_id": session_id,
            "memory_snapshot": content
        }

    @staticmethod
    def to_json(obj: Dict[str, Any], pretty: bool = True) -> str:
        if pretty:
            return json.dumps(obj, indent=2, ensure_ascii=False)
        return json.dumps(obj, ensure_ascii=False)
