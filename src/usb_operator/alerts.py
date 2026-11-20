"""Monitoring-only telemetry threshold rules and alert lifecycle."""
from __future__ import annotations
import math
from pydantic import BaseModel, Field, field_validator
from .telemetry import METRIC_RE

class AlertRuleCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=160)
    metric: str = Field(min_length=1, max_length=64)
    operator: str = Field(pattern="^(gt|gte|lt|lte|eq|ne)$")
    threshold: float = Field(allow_inf_nan=False)
    unit: str = Field(default="", max_length=24)
    severity: str = Field(default="warning", pattern="^(info|warning|critical)$")
    enabled: bool = True

    @field_validator("metric")
    @classmethod
    def validate_metric(cls, value):
        if not METRIC_RE.fullmatch(value):
            raise ValueError("Metric name must be a simple identifier")
        return value

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, value):
        if any(ord(char) < 32 for char in value):
            raise ValueError("Unit contains control characters")
        return value

class RuleEnabled(BaseModel):
    enabled: bool

class AlertService:
    def __init__(self, registry, store):
        self.registry = registry
        self.store = store

    def create_rule(self, rule: AlertRuleCreate):
        if not self.registry.get(rule.device_id):
            raise LookupError(f"Unknown device: {rule.device_id}")
        if self.store.count_alert_rules() >= 200:
            raise ValueError("Maximum of 200 alert rules reached")
        return self.store.create_alert_rule(rule.model_dump())

    def list_rules(self, device_id: str | None = None):
        return self.store.list_alert_rules(device_id)

    def set_enabled(self, rule_id: int, enabled: bool):
        result = self.store.set_alert_rule_enabled(rule_id, enabled)
        if result is None:
            raise LookupError("Alert rule not found")
        return result

    def list_alerts(self, status: str | None = None, limit: int = 100):
        return self.store.list_alerts(status, limit)

    def acknowledge(self, alert_id: int):
        result = self.store.acknowledge_alert(alert_id)
        if result is None:
            raise LookupError("Alert not found or already resolved")
        return result
