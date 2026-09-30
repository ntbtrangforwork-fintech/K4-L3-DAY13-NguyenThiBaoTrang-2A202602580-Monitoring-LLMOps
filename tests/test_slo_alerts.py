from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_slo_has_explicit_error_budget_example() -> None:
    slo = yaml.safe_load((REPO_ROOT / "config" / "slo.yaml").read_text(encoding="utf-8"))
    primary = slo["primary_slo"]

    assert primary["target_percent"] == 99.5
    assert primary["error_budget_percent"] == 0.5
    assert primary["error_budget"]["example_total_requests"] == 10_000
    assert primary["error_budget"]["allowed_bad_requests"] == 50
    assert primary["rationale"]


def test_three_alerts_have_operational_ownership_and_runbooks() -> None:
    config = yaml.safe_load(
        (REPO_ROOT / "config" / "alert_rules.yaml").read_text(encoding="utf-8")
    )
    alerts = config["alerts"]

    assert len(alerts) == 3
    assert {alert["name"] for alert in alerts} == {
        "HighLatencyP95",
        "HighErrorRate",
        "LowQualityScore",
    }
    for alert in alerts:
        assert alert["severity"] in {"warning", "critical"}
        assert alert["duration"]
        assert alert["condition"]
        assert alert["type"] == "symptom-based"
        assert alert["channel"].startswith("slack:#")
        assert alert["owner"] == "student-2A202602580"
        assert alert["runbook"].startswith("docs/alerts.md#alert-")
