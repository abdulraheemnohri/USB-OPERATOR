import secrets
from datetime import datetime,timedelta,timezone
from ..models import CommandPlan,CommandRequest
from ..adapters.simulator import SimulatorAdapter
class CommandService:
    def __init__(self,registry,policy,audit=None): self.registry=registry; self.policy=policy; self.plans={}; self.approvals=set(); self.sim=SimulatorAdapter(); self.audit=audit
    def _record(self,event,payload):
        if self.audit: self.audit.record(event,payload)
    def plan(self,request:CommandRequest):
        device=self.registry.get(request.device_id)
        if not device: raise LookupError("Device not found. Run discovery first.")
        if request.action not in device.capabilities: raise PermissionError("Device profile does not declare this capability.")
        decision=self.policy.evaluate(request.action); status="blocked" if not decision.allowed else ("awaiting_approval" if decision.requires_approval else "ready")
        plan=CommandPlan(id=secrets.token_urlsafe(18),device_id=request.device_id,action=request.action,parameters=request.parameters,risk=decision.risk,status=status,explanation=decision.reason,expires_at=datetime.now(timezone.utc)+timedelta(minutes=5)); self.plans[plan.id]=plan
        self._record("command.planned",{"plan_id":plan.id,"device_id":plan.device_id,"action":plan.action,"risk":plan.risk,"status":plan.status,"reason":request.reason})
        return plan
    def approve(self,plan_id):
        p=self.plans.get(plan_id)
        if not p or p.expires_at<datetime.now(timezone.utc): raise LookupError("Plan missing or expired.")
        if p.status!="awaiting_approval": raise ValueError("Only plans awaiting approval can be approved.")
        self.approvals.add(plan_id); p=p.model_copy(update={"status":"approved"}); self.plans[plan_id]=p
        self._record("command.approved",{"plan_id":p.id,"device_id":p.device_id,"action":p.action})
        return p
    async def execute(self,plan_id):
        p=self.plans.get(plan_id)
        if not p or p.expires_at<datetime.now(timezone.utc): raise LookupError("Plan missing or expired.")
        if p.status=="blocked": raise PermissionError(p.explanation)
        if p.status=="awaiting_approval" or (p.status=="approved" and plan_id not in self.approvals): raise PermissionError("Operator approval is required.")
        if p.status not in {"ready","approved"}: raise ValueError("Plan already executed or invalid.")
        d=self.registry.get(p.device_id)
        if not d: raise LookupError("Device disconnected.")
        if d.transport.value!="simulator": raise NotImplementedError("Live control adapter is not enabled for this device profile.")
        try:
            result=await self.sim.execute(d,p.action,p.parameters)
            self._record("command.executed",{"plan_id":p.id,"device_id":p.device_id,"action":p.action,"simulated":True,"ok":bool(result.get("ok"))})
            self.approvals.discard(plan_id); self.plans[plan_id]=p.model_copy(update={"status":"executed"}); return result
        except Exception as exc:
            self._record("command.failed",{"plan_id":p.id,"device_id":p.device_id,"action":p.action,"error_type":type(exc).__name__})
            raise
