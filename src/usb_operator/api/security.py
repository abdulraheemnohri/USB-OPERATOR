from fastapi import Header,HTTPException
from ..config import settings
async def require_remote_token(x_operator_token:str|None=Header(default=None)):
    """Optional shared-token guard for deployments exposed beyond localhost.
    Keep the service on loopback unless a strong token and TLS reverse proxy are configured.
    """
    if settings.remote_token and x_operator_token!=settings.remote_token:
        raise HTTPException(status_code=401,detail="Invalid operator token.")
