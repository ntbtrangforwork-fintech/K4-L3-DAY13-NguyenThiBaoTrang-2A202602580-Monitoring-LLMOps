from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.dashboard import build_dashboard_snapshot, render_dashboard_html


def test_dashboard_aggregates_six_runtime_panels(tmp_path: Path) -> None:
    now = datetime(2026, 9, 30, 5, 0, tzinfo=timezone.utc)
    records = [
        {
            "ts": (now - timedelta(minutes=2)).isoformat(),
            "event": "request_received",
            "correlation_id": "req-11111111",
        },
        {
            "ts": (now - timedelta(minutes=1)).isoformat(),
            "event": "response_sent",
            "latency_ms": 1200,
            "ttft_ms": 80,
            "cost_usd": 0.01,
            "tokens_in": 100,
            "tokens_out": 200,
            "quality_score": 0.9,
            "tool_success": True,
        },
    ]
    log_path = tmp_path / "logs.jsonl"
    log_path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8"
    )

    snapshot = build_dashboard_snapshot(log_path=log_path, now=now)

    assert snapshot["latency"]["p95"] == 1200
    assert snapshot["traffic"]["count"] == 1
    assert snapshot["errors"]["rate_pct"] == 0
    assert snapshot["errors"]["retrieval_success_pct"] == 100
    assert snapshot["cost"]["total"] == 0.01
    assert snapshot["tokens"] == {"input": 100, "output": 200}
    assert snapshot["quality"]["mean"] == 0.9

    html = render_dashboard_html(snapshot)
    assert html.count('data-panel-id="') == 6
    assert "TTFT P95" in html
    assert "retrieval success" in html
