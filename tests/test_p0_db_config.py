import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts"/"check_db_config.py"
spec=importlib.util.spec_from_file_location("dbcheck",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_reject_shared_database():
    url="postgresql://user:secret@example.org/wero1eletrico"
    assert m.inspect({"WERO_ELETRICO_DATABASE_URL":url,"DATABASE_URL":url})["isolated"] is False
def test_accept_dedicated_database_without_leaking_secret():
    result=m.inspect({"WERO_ELETRICO_DATABASE_URL":"postgresql://user:secret@example.org/wero1eletrico"})
    assert result == {"configured":True,"valid_format":True,"isolated":True}
    assert "secret" not in str(result)
