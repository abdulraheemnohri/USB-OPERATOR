from dataclasses import dataclass,field
@dataclass
class PolicyDecision:
    allowed:bool; requires_approval:bool; risk:str; reason:str
@dataclass
class SafetyPolicy:
    safe_auto_actions:set[str]=field(default_factory=lambda:{"status","identify","read","list_capabilities","capture_preview"})
    blocked_actions:set[str]=field(default_factory=lambda:{"firmware_flash","erase_storage","format_storage","unlock","disable_safety","bypass_interlock","mains_switch","motor_unbounded"})
    approval_actions:set[str]=field(default_factory=lambda:{"write","gpio_set","relay_set","motor_move","restart","firmware_update","network_config","storage_write"})
    def evaluate(self,action,**_):
        a=action.strip().lower()
        if a in self.blocked_actions: return PolicyDecision(False,False,"critical","Action is blocked by safety policy.")
        if a in self.safe_auto_actions: return PolicyDecision(True,False,"low","Read-only action is allowed.")
        if a in self.approval_actions: return PolicyDecision(True,True,"high","Explicit operator approval is required.")
        return PolicyDecision(False,False,"unknown","Unknown actions are denied by default.")
    def public_config(self): return {"mode":"policy","default":"deny","safe_auto_actions":sorted(self.safe_auto_actions),"approval_actions":sorted(self.approval_actions),"blocked_actions":sorted(self.blocked_actions),"hardware_interlocks_required":True}
