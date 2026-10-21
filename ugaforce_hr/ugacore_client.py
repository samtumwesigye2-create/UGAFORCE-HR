"""Fail-open UGACORE adapter for UGAFORCE-HR.

UGAFORCE-HR remains authoritative for HR business data and its local audit log.
This adapter only forwards cross-cutting monitoring/audit signals when UGACORE
is configured. A slow or unavailable platform service must never break an HR
user request.
"""
from __future__ import annotations

import json
import os
import threading
import urllib.request
from typing import Any

UGACORE_URL = os.getenv("UGACORE_URL", "").rstrip("/")
SERVICE_ID = os.getenv("UGACORE_SERVICE_ID", "ugaforce-hr")
SERVICE_TOKEN = os.getenv("UNG_HR_SERVICE_TOKEN", "")
TIMEOUT_SECONDS = float(os.getenv("UGACORE_TIMEOUT_SECONDS", "1.5"))
PUBLIC_URL = os.getenv("UGAFORCE_HR_PUBLIC_URL", "https://ugaforce-hr-production.up.railway.app").rstrip("/")


def _request(path: str, payload: dict[str, Any], method: str = "POST") -> None:
    if not UGACORE_URL or not SERVICE_TOKEN:
        return
    try:
        body = json.dumps(payload, default=str).encode("utf-8")
        request = urllib.request.Request(
            f"{UGACORE_URL}{path}",
            data=body,
            method=method,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {SERVICE_TOKEN}",
            },
        )
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS):
            pass
    except Exception:
        return


def _background(path: str, payload: dict[str, Any], method: str = "POST") -> None:
    threading.Thread(target=_request, args=(path, payload, method), daemon=True).start()


def _register() -> None:
    _request(
        f"/v1/services/{SERVICE_ID.upper()}",
        {
            "service_key": SERVICE_ID.upper(),
            "display_name": "UGAFORCE-HR",
            "base_url": PUBLIC_URL,
            "version": "1.1.0",
            "capabilities": ["workforce", "recruiting", "onboarding", "payroll", "performance", "approvals"],
            "health_path": "/health",
            "enabled": True,
        },
        "PUT",
    )


def heartbeat(status: str = "online", **metadata: Any) -> None:
    def send() -> None:
        _register()
        normalized = "degraded" if str(status).lower() in {"degraded", "warning"} else "healthy"
        _request(
            f"/v1/services/{SERVICE_ID.upper()}/heartbeat",
            {"status": normalized, "latency_ms": None, "details": metadata},
        )

    threading.Thread(target=send, daemon=True).start()


def mirror_audit(action: str, entity_type: str, entity_id: str, actor_id: str | None = None, **metadata: Any) -> None:
    _background(
        "/v1/audit/events",
        {
            "actor_id": actor_id or SERVICE_ID,
            "action": action,
            "resource_type": entity_type,
            "resource_id": entity_id,
            "payload": metadata,
        },
    )
