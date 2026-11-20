from __future__ import annotations
from dataclasses import dataclass
import os
import httpx
@dataclass
class AIProposal:
    text:str
    provider:str
    model:str
class HybridAI:
    """Optional OpenAI-compatible endpoint adapter. Never executes hardware actions."""
    def __init__(self):
        self.local_url=os.getenv("USB_OPERATOR_LOCAL_AI_URL","http://127.0.0.1:11434/v1/chat/completions")
        self.local_model=os.getenv("USB_OPERATOR_LOCAL_MODEL","qwen2.5:3b")
        self.remote_url=os.getenv("USB_OPERATOR_REMOTE_AI_URL","")
        self.remote_key=os.getenv("USB_OPERATOR_REMOTE_AI_KEY","")
        self.remote_model=os.getenv("USB_OPERATOR_REMOTE_MODEL","")
    async def propose(self,prompt:str,prefer_local:bool=True)->AIProposal:
        candidates=[]
        if prefer_local: candidates.append(("local",self.local_url,self.local_model,""))
        if self.remote_url and self.remote_model: candidates.append(("remote",self.remote_url,self.remote_model,self.remote_key))
        if not prefer_local: candidates.append(("local",self.local_url,self.local_model,""))
        for name,url,model,key in candidates:
            try:
                headers={"Authorization":f"Bearer {key}"} if key else {}
                async with httpx.AsyncClient(timeout=20) as client:
                    response=await client.post(url,headers=headers,json={"model":model,"messages":[{"role":"system","content":"You are a cautious physical-device assistant. Return advice only; never claim to have executed hardware commands. Recommend read-only diagnostics first."},{"role":"user","content":prompt}]})
                    response.raise_for_status(); data=response.json()
                    return AIProposal(text=data["choices"][0]["message"]["content"],provider=name,model=model)
            except (httpx.HTTPError,KeyError,ValueError):
                continue
        return AIProposal(text="AI provider unavailable. Use deterministic device discovery and command planning.",provider="none",model="none")
