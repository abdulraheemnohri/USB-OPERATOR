import secrets
from datetime import datetime,timedelta,timezone
from ..models import CommandPlan,CommandRequest
from ..adapters.simulator import SimulatorAdapter
class CommandService:
    def __init__(self,registry,policy): self.registry=registry; self.policy=policy; self.plans={}; self.approvals=set(); self.sim=SimulatorAdapter()
    def plan(self,request:CommandRequest):
        device=self.registry.get(request.device_id)
        if not device: raise LookupError("Device not found. Run discovery first.")
        if request.action not in device.capabilities: raise PermissionError("Device profile does not declare this capability.")
        decision=self.policy.evaluate(request.action); status="blocked" if not decision.allowed else ("awaiting_approval" if decision.requires_approval else "ready")
        plan=CommandPlan(id=secrets.token_urlsafe(18),device_id=request.device_id,action=request.action,parameters=request.parameters,risk=decision.risk,status=status,explanation=decision.reason,expires_at=datetime.now(timezone.utc)+timedelta(minutes=5)); self.plans[plan.id]=plan; return plan
    def approve(self,plan_id):
        p=self.plans.get(plan_id)
        if not p or p.expires_at<datetime.now(timezone.utc): raise LookupError("Plan missing or expired.")
        if p.status!="awaiting_approval": raise ValueError("Only plans awaiting approval can be approved.")
        self.approvals.add(plan_id); p=p.model_copy(update={"status":"approved"}); self.plans[plan_id]=p; return p
    async def execute(self,plan_id):
        p=self.plans.get(plan_id)
        if not p or p.expires_at<datetime.now(timezone.utc): raise LookupError("Plan missing or expired.")
        if p.status=="blocked": raise PermissionError(p.explanation)
        if p.status=="awaiting_approval" or (p.status=="approved" and plan_id not in self.approvals): raise PermissionError("Operator approval is required.")
        if p.status not in {"ready","approved"}: raise ValueError("Plan already executed or invalid.")
        d=self.registry.get(p.device_id)
        if not d: raise LookupError("Device disconnected.")
        if d.transport.value!="simulator": raise NotImplementedError("Live control adapter is not enabled for this device profile.")
        result=await self.sim.execute(d,p.action,p.parameters); self.approvals.discard(plan_id); self.plans[plan_id]=p.model_copy(update={"status":"executed"}); return result
