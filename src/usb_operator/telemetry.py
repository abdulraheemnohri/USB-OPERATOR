"""Validated telemetry ingestion and query service."""
from __future__ import annotations
import re
from datetime import datetime,timezone,timedelta
from pydantic import BaseModel,Field,field_validator
from .models import utcnow
METRIC_RE=re.compile(r"^[a-zA-Z][a-zA-Z0-9_.-]{0,63}$")
class TelemetrySample(BaseModel):
    device_id:str=Field(min_length=1,max_length=160)
    metric:str=Field(min_length=1,max_length=64)
    value:float=Field(allow_inf_nan=False)
    unit:str=Field(default="",max_length=24)
    quality:str=Field(default="good",pattern="^(good|uncertain|bad)$")
    recorded_at:datetime=Field(default_factory=utcnow)
    source:str=Field(default="host",max_length=32)
    @field_validator("metric")
    @classmethod
    def metric_name(cls,value):
        if not METRIC_RE.fullmatch(value): raise ValueError("Metric name must be a simple identifier")
        return value
    @field_validator("unit")
    @classmethod
    def unit_text(cls,value):
        if any(ord(c)<32 for c in value): raise ValueError("Unit contains control characters")
        return value
    @field_validator("recorded_at")
    @classmethod
    def normalize_timestamp(cls,value): return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
class TelemetryBatch(BaseModel): samples:list[TelemetrySample]=Field(min_length=1,max_length=100)
class TelemetryService:
    def __init__(self,registry,store): self.registry=registry; self.store=store
    def ingest(self,batch:TelemetryBatch):
        now=datetime.now(timezone.utc); validated=[]
        for sample in batch.samples:
            device=self.registry.get(sample.device_id)
            if not device: raise LookupError(f"Unknown device: {sample.device_id}")
            if device.state.value not in {"connected","simulated"}: raise PermissionError("Telemetry from disconnected/degraded devices is rejected")
            if sample.recorded_at>now+timedelta(minutes=5): raise ValueError("Telemetry timestamp is too far in the future")
            validated.append(sample)
        accepted=[self.store.record_telemetry(sample.model_dump(mode="json")) for sample in validated]
        return {"accepted":len(accepted),"samples":accepted}
    def latest(self,device_id:str|None=None,limit:int=100): return self.store.latest_telemetry(device_id,limit)
    def history(self,device_id:str,metric:str|None=None,limit:int=100): return self.store.query_telemetry(device_id,metric,limit)
