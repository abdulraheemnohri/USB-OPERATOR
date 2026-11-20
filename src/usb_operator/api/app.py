from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Depends,Query
from fastapi.middleware.cors import CORSMiddleware
from ..config import settings
from ..models import CommandRequest
from ..policy import SafetyPolicy
from ..registry import DeviceRegistry
from ..storage import SQLiteStore
from ..profiles import ProfileStore
from ..services.discovery import DiscoveryService
from ..services.commands import CommandService
from ..services.hotplug import HotplugMonitor
from ..telemetry import TelemetryBatch,TelemetryService
from ..polling import PollRequest,ReadOnlyPoller
from ..alerts import AlertRuleCreate,RuleEnabled,AlertService
from .security import require_remote_token
store=SQLiteStore(settings.database_path); registry=DeviceRegistry(store=store); policy=SafetyPolicy(); discovery=DiscoveryService(registry,enable_ble=settings.enable_ble); commands=CommandService(registry,policy,audit=store); profiles=ProfileStore(settings.profiles_dir); monitor=HotplugMonitor(discovery,registry,store,settings.hotplug_interval); telemetry=TelemetryService(registry,store); poller=ReadOnlyPoller(telemetry); alerts=AlertService(registry,store)
@asynccontextmanager
async def lifespan(app):
    await monitor.start()
    yield
    await monitor.stop()
app=FastAPI(title="USB-OPERATOR API",version="0.10.0",description="Policy-governed universal physical-device operator.",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=list(settings.cors_origins),allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*","X-Operator-Token"])
@app.get("/health")
async def health(): return {"status":"ok","service":"usb-operator","version":"0.10.0"}
@app.get("/v1/devices")
async def list_devices(): return {"devices":[d.model_dump(mode="json") for d in registry.list()]}
@app.post("/v1/discovery/scan",dependencies=[Depends(require_remote_token)])
async def scan_devices():
    try: return await monitor.scan_once()
    except Exception as e: raise HTTPException(500,"Discovery scan failed.") from e
@app.get("/v1/monitor")
async def monitor_status(): return monitor.status()
@app.get("/v1/profiles")
async def list_profiles(): return profiles.list()
@app.get("/v1/policy")
async def get_policy(): return policy.public_config()
@app.post("/v1/telemetry/ingest",dependencies=[Depends(require_remote_token)])
async def ingest_telemetry(batch:TelemetryBatch):
    try: return telemetry.ingest(batch)
    except LookupError as e: raise HTTPException(404,str(e)) from e
    except PermissionError as e: raise HTTPException(403,str(e)) from e
    except ValueError as e: raise HTTPException(422,str(e)) from e
@app.get("/v1/telemetry/latest")
async def latest_telemetry(device_id:str|None=None,limit:int=Query(default=100,ge=1,le=500)):
    if device_id and not registry.get(device_id): raise HTTPException(404,"Device not found.")
    return {"samples":telemetry.latest(device_id,limit)}
@app.get("/v1/telemetry/history/{device_id}")
async def telemetry_history(device_id:str,metric:str|None=None,limit:int=Query(default=100,ge=1,le=1000)):
    if not registry.get(device_id): raise HTTPException(404,"Device not found.")
    return {"samples":telemetry.history(device_id,metric,limit)}
@app.post("/v1/devices/{device_id}/telemetry/poll",dependencies=[Depends(require_remote_token)])
async def poll_device_telemetry(device_id:str,request:PollRequest):
    try: return await poller.poll(device_id,request)
    except LookupError as e: raise HTTPException(404,str(e)) from e
    except PermissionError as e: raise HTTPException(403,str(e)) from e
    except ValueError as e: raise HTTPException(422,str(e)) from e
    except (OSError,TimeoutError,RuntimeError) as e: raise HTTPException(502,"Read-only device polling failed.") from e

@app.post("/v1/alerts/rules",dependencies=[Depends(require_remote_token)])
async def create_alert_rule(rule:AlertRuleCreate):
    try: return alerts.create_rule(rule)
    except LookupError as e: raise HTTPException(404,str(e)) from e
    except ValueError as e: raise HTTPException(422,str(e)) from e
@app.get("/v1/alerts/rules")
async def list_alert_rules(device_id:str|None=None):
    if device_id and not registry.get(device_id): raise HTTPException(404,"Device not found.")
    return {"rules":alerts.list_rules(device_id)}
@app.post("/v1/alerts/rules/{rule_id}/enabled",dependencies=[Depends(require_remote_token)])
async def set_alert_rule_enabled(rule_id:int,body:RuleEnabled):
    try: return alerts.set_enabled(rule_id,body.enabled)
    except LookupError as e: raise HTTPException(404,str(e)) from e
@app.get("/v1/alerts")
async def list_alerts(status:str|None=Query(default=None,pattern="^(active|acknowledged|resolved)$"),limit:int=Query(default=100,ge=1,le=500)):
    return {"alerts":alerts.list_alerts(status,limit)}
@app.post("/v1/alerts/{alert_id}/acknowledge",dependencies=[Depends(require_remote_token)])
async def acknowledge_alert(alert_id:int):
    try: return alerts.acknowledge(alert_id)
    except LookupError as e: raise HTTPException(404,str(e)) from e
@app.get("/v1/audit",dependencies=[Depends(require_remote_token)])
async def get_audit(limit:int=Query(default=100,ge=1,le=500)): return {"events":store.list_audit(limit),"integrity":store.verify_audit()}
@app.post("/v1/commands/plan",dependencies=[Depends(require_remote_token)])
async def plan_command(request:CommandRequest):
    try: return commands.plan(request).model_dump(mode="json")
    except LookupError as e: raise HTTPException(404,str(e)) from e
    except PermissionError as e: raise HTTPException(403,str(e)) from e
@app.post("/v1/commands/{plan_id}/approve",dependencies=[Depends(require_remote_token)])
async def approve_command(plan_id:str):
    try: return commands.approve(plan_id).model_dump(mode="json")
    except LookupError as e: raise HTTPException(404,str(e)) from e
    except ValueError as e: raise HTTPException(409,str(e)) from e
@app.post("/v1/commands/{plan_id}/execute",dependencies=[Depends(require_remote_token)])
async def execute_command(plan_id:str):
    try: return await commands.execute(plan_id)
    except LookupError as e: raise HTTPException(404,str(e)) from e
    except PermissionError as e: raise HTTPException(403,str(e)) from e
    except NotImplementedError as e: raise HTTPException(501,str(e)) from e
    except ValueError as e: raise HTTPException(400,str(e)) from e
