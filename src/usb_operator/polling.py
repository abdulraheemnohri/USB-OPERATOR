"""Explicitly configured, read-only protocol-to-telemetry polling bridge."""
from __future__ import annotations
import math
from pydantic import BaseModel, Field, field_validator
from .models import Transport
from .protocols.modbus import ModbusTCPReadClient
from .protocols.jsonl import SerialJSONLClient
from .telemetry import TelemetryBatch, TelemetrySample, TelemetryService

class PollChannel(BaseModel):
    metric: str = Field(min_length=1, max_length=64)
    unit: str = Field(default="", max_length=24)
    channel: str | None = Field(default=None, min_length=1, max_length=32)
    address: int | None = Field(default=None, ge=0, le=65535)
    register_index: int = Field(default=0, ge=0, le=124)
    function_code: int = Field(default=3)
    scale: float = Field(default=1.0, allow_inf_nan=False)
    offset: float = Field(default=0.0, allow_inf_nan=False)

    @field_validator("function_code")
    @classmethod
    def read_function_only(cls, value):
        if value not in (3, 4):
            raise ValueError("Only Modbus read function codes 3 and 4 are permitted")
        return value

class PollRequest(BaseModel):
    protocol: str
    channels: list[PollChannel] = Field(min_length=1, max_length=32)
    unit_id: int = Field(default=1, ge=0, le=247)
    timeout: float = Field(default=2.0, ge=0.2, le=5.0)

    @field_validator("protocol")
    @classmethod
    def supported_protocol(cls, value):
        if value not in {"modbus_tcp", "esp32_jsonl"}:
            raise ValueError("Supported poll protocols: modbus_tcp, esp32_jsonl")
        return value

class ReadOnlyPoller:
    def __init__(self, telemetry: TelemetryService, modbus_client=None, jsonl_client=None):
        self.telemetry = telemetry
        self._modbus_override = modbus_client
        self._jsonl_override = jsonl_client

    async def poll(self, device_id: str, request: PollRequest):
        device = self.telemetry.registry.get(device_id)
        if not device:
            raise LookupError(f"Unknown device: {device_id}")
        if device.state.value not in {"connected", "simulated"}:
            raise PermissionError("Polling requires a connected or simulated device")
        samples = []
        if request.protocol == "modbus_tcp":
            if device.transport != Transport.NETWORK or not device.location:
                raise PermissionError("Modbus TCP requires a discovered network device with a configured host location")
            host, port = self._host_port(device.location)
            client = self._modbus_override or ModbusTCPReadClient(timeout=request.timeout)
            for item in request.channels:
                if item.address is None or item.channel is not None:
                    raise ValueError("Modbus channels require an explicit register address and no JSONL channel")
                if item.register_index != 0:
                    raise ValueError("Single-register polling requires register_index=0")
                result = await client.read_registers(host, port, request.unit_id, item.address, 1, item.function_code)
                raw = result.registers[0]
                value = raw * item.scale + item.offset
                samples.append(TelemetrySample(device_id=device_id, metric=item.metric, value=value, unit=item.unit, source="modbus_tcp"))
        else:
            if device.transport != Transport.SERIAL:
                raise PermissionError("ESP32 JSONL polling requires a serial device")
            client = self._jsonl_override or SerialJSONLClient(timeout=request.timeout)
            for item in request.channels:
                if not item.channel or item.address is not None:
                    raise ValueError("ESP32 JSONL channels require an explicit channel name and no register address")
                response = await client.execute(device, "read", {"channel": item.channel})
                data = response.get("data", {})
                raw = data.get("value", data.get(item.channel))
                if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(float(raw)):
                    raise ValueError(f"Device returned no finite numeric value for channel {item.channel}")
                samples.append(TelemetrySample(device_id=device_id, metric=item.metric, value=float(raw) * item.scale + item.offset, unit=item.unit or str(data.get("unit", "")), source="esp32_jsonl"))
        return self.telemetry.ingest(TelemetryBatch(samples=samples))

    @staticmethod
    def _host_port(location: str):
        if "://" in location or any(c in location for c in "/\\\\@"):
            raise ValueError("Network device location must be a plain host or host:port")
        if location.count(":") > 1:
            raise ValueError("IPv6 Modbus locations must be configured as a hostname; bracketed IPv6 is not supported")
        if ":" in location:
            host, raw_port = location.rsplit(":", 1)
            if not raw_port.isdigit() or not 1 <= int(raw_port) <= 65535:
                raise ValueError("Invalid Modbus TCP port in device location")
            return host, int(raw_port)
        return location, 502
