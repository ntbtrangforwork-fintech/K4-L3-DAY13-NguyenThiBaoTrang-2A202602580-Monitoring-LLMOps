from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from statistics import mean
from typing import Any

import yaml


LOG_PATH = Path(os.getenv("LOG_PATH", "data/logs.jsonl"))
CONFIG_PATH = Path("config/dashboard.yaml")


def _percentile(values: list[float], percentile: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(
        0,
        min(len(ordered) - 1, round((percentile / 100) * len(ordered) + 0.5) - 1),
    )
    return float(ordered[index])


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _load_recent_records(
    log_path: Path, *, now: datetime, window_minutes: int
) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []
    cutoff = now - timedelta(minutes=window_minutes)
    records: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        timestamp = _parse_timestamp(record.get("ts"))
        if timestamp is not None and cutoff <= timestamp <= now:
            records.append(record)
    return records


def build_dashboard_snapshot(
    log_path: Path = LOG_PATH,
    config_path: Path = CONFIG_PATH,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))["dashboard"]
    window_minutes = int(config["time_range_minutes"])
    records = _load_recent_records(log_path, now=now, window_minutes=window_minutes)
    requests = [record for record in records if record.get("event") == "request_received"]
    responses = [record for record in records if record.get("event") == "response_sent"]
    failures = [record for record in records if record.get("event") == "request_failed"]

    latencies = [float(record["latency_ms"]) for record in responses if record.get("latency_ms") is not None]
    ttfts = [float(record["ttft_ms"]) for record in responses if record.get("ttft_ms") is not None]
    costs = [float(record["cost_usd"]) for record in responses if record.get("cost_usd") is not None]
    tokens_in = [int(record["tokens_in"]) for record in responses if record.get("tokens_in") is not None]
    tokens_out = [int(record["tokens_out"]) for record in responses if record.get("tokens_out") is not None]
    quality = [float(record["quality_score"]) for record in responses if record.get("quality_score") is not None]
    retrieval_results = [record["tool_success"] for record in records if isinstance(record.get("tool_success"), bool)]

    traffic_by_minute: Counter[str] = Counter()
    cost_by_minute: Counter[str] = Counter()
    for record in requests:
        timestamp = _parse_timestamp(record.get("ts"))
        if timestamp:
            traffic_by_minute[timestamp.strftime("%H:%M")] += 1
    for record in responses:
        timestamp = _parse_timestamp(record.get("ts"))
        if timestamp and record.get("cost_usd") is not None:
            cost_by_minute[timestamp.strftime("%H:%M")] += float(record["cost_usd"])

    error_rate = (len(failures) / len(requests) * 100) if requests else 0.0
    retrieval_success = (
        sum(1 for result in retrieval_results if result) / len(retrieval_results) * 100
        if retrieval_results
        else 0.0
    )

    return {
        "generated_at": now.isoformat(),
        "window_minutes": window_minutes,
        "refresh_seconds": int(config["refresh_seconds"]),
        "record_count": len(records),
        "latency": {
            "p50": _percentile(latencies, 50),
            "p95": _percentile(latencies, 95),
            "p99": _percentile(latencies, 99),
            "ttft_p95": _percentile(ttfts, 95),
        },
        "traffic": {
            "count": len(requests),
            "rate_per_minute": len(requests) / window_minutes,
            "series": dict(sorted(traffic_by_minute.items())),
        },
        "errors": {
            "count": len(failures),
            "rate_pct": error_rate,
            "retrieval_success_pct": retrieval_success,
            "breakdown": dict(Counter(str(record.get("error_type", "unknown")) for record in failures)),
        },
        "cost": {
            "total": sum(costs),
            "series": dict(sorted(cost_by_minute.items())),
        },
        "tokens": {"input": sum(tokens_in), "output": sum(tokens_out)},
        "quality": {"mean": mean(quality) if quality else 0.0},
    }


def _status(value: float, operator: str, threshold: float) -> tuple[str, str]:
    healthy = value <= threshold if operator == "lte" else value >= threshold
    return ("Within threshold", "ok") if healthy else ("Outside threshold", "alert")


def _format_series(series: dict[str, float | int], *, currency: bool = False) -> str:
    if not series:
        return '<span class="empty">No samples in this window</span>'
    maximum = max(float(value) for value in series.values()) or 1.0
    bars = []
    for label, raw_value in list(series.items())[-12:]:
        value = float(raw_value)
        height = max(8, round(value / maximum * 54))
        formatted = f"${value:.4f}" if currency else f"{value:g}"
        bars.append(
            f'<div class="bar-wrap" title="{escape(label)}: {formatted}">'
            f'<div class="bar" style="height:{height}px"></div><small>{escape(label)}</small></div>'
        )
    return f'<div class="bars">{"".join(bars)}</div>'


def render_dashboard_html(
    snapshot: dict[str, Any] | None = None,
    config_path: Path = CONFIG_PATH,
) -> str:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))["dashboard"]
    snapshot = snapshot or build_dashboard_snapshot(config_path=config_path)
    thresholds = {panel["id"]: panel["threshold"] for panel in config["panels"]}

    def badge(panel_id: str, value: float) -> str:
        threshold = thresholds[panel_id]
        label, class_name = _status(value, threshold["operator"], float(threshold["value"]))
        symbol = "≤" if threshold["operator"] == "lte" else "≥"
        return (
            f'<span class="badge {class_name}">{label}</span>'
            f'<span class="threshold">Threshold {symbol} {threshold["value"]}</span>'
        )

    latency = snapshot["latency"]
    traffic = snapshot["traffic"]
    errors = snapshot["errors"]
    cost = snapshot["cost"]
    tokens = snapshot["tokens"]
    quality = snapshot["quality"]

    panels = [
        (
            "latency",
            "Latency percentiles and TTFT",
            '<div class="metrics">'
            f'<div><strong>{latency["p50"]:.0f}</strong><span>P50 ms</span></div>'
            f'<div><strong>{latency["p95"]:.0f}</strong><span>P95 ms</span></div>'
            f'<div><strong>{latency["p99"]:.0f}</strong><span>P99 ms</span></div>'
            f'<div><strong>{latency["ttft_p95"]:.0f}</strong><span>TTFT P95 ms</span></div></div>'
            + badge("latency", latency["p95"]),
        ),
        (
            "traffic",
            "Request traffic",
            '<div class="metrics two">'
            f'<div><strong>{traffic["count"]}</strong><span>requests</span></div>'
            f'<div><strong>{traffic["rate_per_minute"]:.2f}</strong><span>requests/min</span></div></div>'
            + _format_series(traffic["series"])
            + badge("traffic", traffic["rate_per_minute"]),
        ),
        (
            "errors",
            "Error rate and retrieval success",
            '<div class="metrics">'
            f'<div><strong>{errors["rate_pct"]:.2f}%</strong><span>error rate</span></div>'
            f'<div><strong>{errors["count"]}</strong><span>errors</span></div>'
            f'<div><strong>{errors["retrieval_success_pct"]:.1f}%</strong><span>retrieval success</span></div></div>'
            + badge("errors", errors["rate_pct"]),
        ),
        (
            "cost",
            "Cost over time",
            f'<div class="hero-metric"><strong>${cost["total"]:.4f}</strong><span>total USD</span></div>'
            + _format_series(cost["series"], currency=True)
            + badge("cost", cost["total"]),
        ),
        (
            "tokens",
            "Input and output tokens",
            '<div class="metrics two">'
            f'<div><strong>{tokens["input"]:,}</strong><span>input tokens</span></div>'
            f'<div><strong>{tokens["output"]:,}</strong><span>output tokens</span></div></div>'
            + badge("tokens", max(tokens["input"], tokens["output"])),
        ),
        (
            "quality",
            "Quality proxy",
            f'<div class="hero-metric"><strong>{quality["mean"]:.2f}</strong><span>mean score · 0–1</span></div>'
            + f'<div class="quality-track"><i style="width:{max(0, min(100, quality["mean"] * 100)):.0f}%"></i></div>'
            + badge("quality", quality["mean"]),
        ),
    ]

    panel_html = "".join(
        f'<section class="panel" data-panel-id="{panel_id}"><div class="panel-kicker">{panel_id}</div>'
        f'<h2>{escape(title)}</h2>{body}</section>'
        for panel_id, title, body in panels
    )
    generated = escape(str(snapshot["generated_at"]).replace("T", " ").replace("+00:00", " UTC"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="{snapshot['refresh_seconds']}">
  <title>{escape(config['title'])}</title>
  <style>
    :root {{ color-scheme: dark; --bg:#0b1020; --panel:#151c30; --line:#29334d; --text:#f4f7ff; --muted:#9aa7c2; --cyan:#54d6ff; --green:#52d6a0; --red:#ff7787; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:radial-gradient(circle at 10% 0%,#182a48 0,var(--bg) 35%); color:var(--text); font:14px/1.45 Inter,Segoe UI,sans-serif; }}
    main {{ max-width:1260px; margin:auto; padding:38px 32px 54px; }} header {{ display:flex; justify-content:space-between; gap:24px; align-items:end; margin-bottom:28px; }}
    h1 {{ margin:4px 0 0; font-size:30px; letter-spacing:-.03em; }} .eyebrow,.panel-kicker {{ color:var(--cyan); text-transform:uppercase; letter-spacing:.14em; font-size:11px; font-weight:700; }}
    .meta {{ color:var(--muted); text-align:right; }} .grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:18px; }}
    .panel {{ min-height:250px; padding:22px; border:1px solid var(--line); border-radius:16px; background:linear-gradient(145deg,rgba(27,37,62,.98),rgba(17,24,43,.98)); box-shadow:0 18px 45px rgba(0,0,0,.2); }}
    h2 {{ margin:5px 0 22px; font-size:18px; }} .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }} .metrics.two {{ grid-template-columns:repeat(2,1fr); }}
    .metrics div,.hero-metric {{ padding:13px; background:rgba(8,14,29,.52); border-radius:10px; }} strong {{ display:block; font-size:24px; letter-spacing:-.03em; }} span {{ color:var(--muted); font-size:12px; }}
    .badge {{ display:inline-block; margin-top:18px; padding:5px 9px; border-radius:999px; font-weight:700; }} .badge.ok {{ color:var(--green); background:rgba(82,214,160,.12); }} .badge.alert {{ color:var(--red); background:rgba(255,119,135,.12); }}
    .threshold {{ margin-left:9px; }} .bars {{ height:76px; display:flex; align-items:end; gap:5px; margin-top:14px; }} .bar-wrap {{ flex:1; text-align:center; min-width:0; }} .bar {{ background:linear-gradient(var(--cyan),#5778ff); border-radius:4px 4px 1px 1px; }} .bar-wrap small {{ display:block; color:var(--muted); font-size:9px; overflow:hidden; }}
    .quality-track {{ height:9px; margin-top:20px; background:#0a1020; border-radius:10px; overflow:hidden; }} .quality-track i {{ display:block; height:100%; background:linear-gradient(90deg,#5778ff,var(--green)); }} .empty {{ display:block; margin-top:22px; }}
    footer {{ margin-top:22px; color:var(--muted); }} @media(max-width:820px) {{ .grid {{ grid-template-columns:1fr; }} header {{ align-items:start; flex-direction:column; }} .meta {{ text-align:left; }} }}
  </style>
</head>
<body><main>
  <header><div><div class="eyebrow">Runtime observability</div><h1>{escape(config['title'])}</h1></div>
  <div class="meta">Last {snapshot['window_minutes']} minutes · refresh {snapshot['refresh_seconds']}s<br>{generated} · {snapshot['record_count']} log records</div></header>
  <div class="grid">{panel_html}</div>
  <footer>Source: data/logs.jsonl · Thresholds: config/dashboard.yaml</footer>
</main></body></html>"""
