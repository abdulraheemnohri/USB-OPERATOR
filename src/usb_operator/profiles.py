"""Validated, inert device profile manifests. Loading a profile never enables hardware control."""
from pathlib import Path
from typing import Any,Literal
import json
from pydantic import BaseModel,ConfigDict,Field,model_validator
class ProfileAction(BaseModel):
    model_config=ConfigDict(extra="forbid")
    risk:Literal["low","medium","high","critical"]="high"
    approval:bool=True
    read_only:bool=False
    pin_min:int|None=None
    pin_max:int|None=None
    timeout_ms:int=Field(default=1000,ge=50,le=30000)
    @model_validator(mode="after")
    def validate_pin_range(self):
        if self.pin_min is not None and self.pin_max is not None and self.pin_min>self.pin_max: raise ValueError("pin_min cannot exceed pin_max")
        if self.read_only and self.approval: raise ValueError("read-only actions must not request write approval")
        if self.risk=="critical" and not self.approval: raise ValueError("critical actions cannot be configured for automatic approval")
        return self
class DeviceProfile(BaseModel):
    model_config=ConfigDict(extra="forbid")
    id:str=Field(min_length=3,max_length=120,pattern=r"^[a-zA-Z0-9_.-]+$")
    version:int=Field(ge=1)
    display_name:str=Field(min_length=1,max_length=120)
    transport:str=Field(min_length=1,max_length=32)
    protocol:str=Field(min_length=1,max_length=100)
    identity:dict[str,Any]=Field(default_factory=dict)
    capabilities:list[str]=Field(default_factory=list)
    actions:dict[str,ProfileAction]=Field(default_factory=dict)
    enabled:bool=False
    note:str=""
    @model_validator(mode="after")
    def validate_actions_are_declared(self):
        undeclared=set(self.actions)-set(self.capabilities)
        if undeclared: raise ValueError(f"Actions missing from capabilities: {', '.join(sorted(undeclared))}")
        if len(self.capabilities)!=len(set(self.capabilities)): raise ValueError("Duplicate capabilities are not allowed")
        return self
class ProfileStore:
    def __init__(self,directory:str): self.directory=Path(directory)
    def list(self):
        profiles=[]; errors=[]
        if not self.directory.exists(): return {"profiles":[],"errors":[]}
        for path in sorted(self.directory.glob("*.json")):
            try:
                profile=DeviceProfile.model_validate(json.loads(path.read_text(encoding="utf-8")))
                profiles.append({"file":path.name,**profile.model_dump()})
            except Exception as exc: errors.append({"file":path.name,"error":str(exc)[:300]})
        return {"profiles":profiles,"errors":errors}
