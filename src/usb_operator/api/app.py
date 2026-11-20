from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ..config import settings
from ..models import CommandRequest
from ..policy import SafetyPolicy
from ..registry import DeviceRegistry
from ..services.discovery import DiscoveryService
from ..services.commands import CommandService
registry=DeviceRegistry(); policy=SafetyPolicy(); discovery=DiscoveryService(registry); commands=CommandService(registry,policy)
app=FastAPI(title="USB-OPERATOR API",version="0.2.0",description="Policy-governed universal physical-device operator.")
app.add_middleware(CORSMiddleware,allow_origins=list(settings.cors_origins),allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*"])
@app.get("/health")
async def health(): return {"status":"ok","service":"usb-operator","version":"0.2.0"}
@app.get("/v1/devices")
async def list_devices(): return {"devices":[d.model_dump(mode="json") for d in registry.list()]}
@app.post("/v1/discovery/scan")
async def scan_devices():
    devices=await discovery.scan(); return {"count":len(devices),"devices":[d.model_dump(mode="json") for d in devices]}
@app.get("/v1/policy")
async def get_policy(): return policy.public_config()
@app.post("/v1/commands/plan")
async def plan_command(request:CommandRequest):
    try: return commands.plan(request).model_dump(mode="json")
    except LookupError as e: raise HTTPException(404,str(e)) from e
@app.post("/v1/commands/{plan_id}/approve")
async def approve_command(plan_id:str):
    try: return commands.approve(plan_id).model_dump(mode="json")
    except LookupError as e: raise HTTPException(404,str(e)) from e
    except ValueError as e: raise HTTPException(409,str(e)) from e
@app.post("/v1/commands/{plan_id}/execute")
async def execute_command(plan_id:str):
    try: return await commands.execute(plan_id)
    except LookupError as e: raise HTTPException(404,str(e)) from e
    except PermissionError as e: raise HTTPException(403,str(e)) from e
    except NotImplementedError as e: raise HTTPException(501,str(e)) from e
    except ValueError as e: raise HTTPException(400,str(e)) from e
