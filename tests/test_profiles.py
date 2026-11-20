import json
from usb_operator.profiles import DeviceProfile,ProfileStore

def profile_payload():
 return {"id":"test.profile.v1","version":1,"display_name":"Test profile","transport":"serial","protocol":"jsonl/1","capabilities":["identify","gpio_set"],"actions":{"gpio_set":{"risk":"high","approval":True,"read_only":False,"pin_min":0,"pin_max":10}},"enabled":False}

def test_valid_profile_loads_but_remains_disabled():
 profile=DeviceProfile.model_validate(profile_payload()); assert profile.enabled is False

def test_profile_rejects_undeclared_action():
 payload=profile_payload(); payload["capabilities"]=["identify"]
 try: DeviceProfile.model_validate(payload)
 except Exception as exc: assert "missing from capabilities" in str(exc)
 else: raise AssertionError("Undeclared action accepted")

def test_profile_store_reports_invalid_json(tmp_path):
 (tmp_path/"bad.json").write_text("{broken",encoding="utf-8")
 result=ProfileStore(str(tmp_path)).list(); assert not result["profiles"] and result["errors"]

def test_profile_store_loads_example_shape(tmp_path):
 payload=profile_payload(); (tmp_path/"good.json").write_text(json.dumps(payload),encoding="utf-8")
 result=ProfileStore(str(tmp_path)).list(); assert result["profiles"][0]["id"]=="test.profile.v1"
