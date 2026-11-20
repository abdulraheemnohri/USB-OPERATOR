"""SQLite persistence for device inventory and tamper-evident audit chaining."""
from __future__ import annotations
import hashlib,json,sqlite3
from pathlib import Path
from threading import RLock
from datetime import datetime,timezone
from .models import Device
class SQLiteStore:
    def __init__(self,path:str):
        self.path=path; self.lock=RLock()
        if path != ":memory:": Path(path).expanduser().parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS devices (id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, event TEXT NOT NULL, payload TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL)")
    def _connect(self):
        db=sqlite3.connect(self.path,timeout=10); db.row_factory=sqlite3.Row; return db
    def save_device(self,device:Device):
        payload=device.model_dump_json()
        with self.lock,self._connect() as db: db.execute("INSERT INTO devices(id,payload,updated_at) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,updated_at=excluded.updated_at",(device.id,payload,datetime.now(timezone.utc).isoformat()))
    def load_devices(self)->list[Device]:
        with self.lock,self._connect() as db: rows=db.execute("SELECT payload FROM devices ORDER BY id").fetchall()
        result=[]
        for row in rows:
            try: result.append(Device.model_validate_json(row["payload"]))
            except ValueError: continue
        return result
    def remove_device(self,device_id:str):
        with self.lock,self._connect() as db: db.execute("DELETE FROM devices WHERE id=?",(device_id,))
    def record(self,event:str,payload:dict):
        created=datetime.now(timezone.utc).isoformat(); body=json.dumps(payload,sort_keys=True,separators=(",",":"),default=str)
        with self.lock,self._connect() as db:
            row=db.execute("SELECT event_hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone(); previous=row["event_hash"] if row else "GENESIS"
            digest=hashlib.sha256(f"{previous}|{created}|{event}|{body}".encode()).hexdigest()
            db.execute("INSERT INTO audit(created_at,event,payload,previous_hash,event_hash) VALUES(?,?,?,?,?)",(created,event,body,previous,digest))
        return {"created_at":created,"event":event,"payload":payload,"previous_hash":previous,"event_hash":digest}
    def list_audit(self,limit:int=100):
        limit=max(1,min(int(limit),500))
        with self.lock,self._connect() as db: rows=db.execute("SELECT seq,created_at,event,payload,previous_hash,event_hash FROM audit ORDER BY seq DESC LIMIT ?",(limit,)).fetchall()
        return [{"seq":r["seq"],"created_at":r["created_at"],"event":r["event"],"payload":json.loads(r["payload"]),"previous_hash":r["previous_hash"],"event_hash":r["event_hash"]} for r in rows]
    def verify_audit(self):
        with self.lock,self._connect() as db: rows=db.execute("SELECT created_at,event,payload,previous_hash,event_hash FROM audit ORDER BY seq").fetchall()
        previous="GENESIS"
        for row in rows:
            expected=hashlib.sha256(f"{previous}|{row['created_at']}|{row['event']}|{row['payload']}".encode()).hexdigest()
            if row["previous_hash"]!=previous or row["event_hash"]!=expected: return {"valid":False,"checked":0,"reason":"Audit chain mismatch"}
            previous=row["event_hash"]
        return {"valid":True,"checked":len(rows),"head":previous}
