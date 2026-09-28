import json
import pytest
from arena import config

def test_transient_windows_lock_retries_without_losing_existing_ledger(tmp_path,monkeypatch):
    path=tmp_path/'ledger.json';path.write_text('{"reserved":1}',encoding='utf-8')
    replace=config.os.replace;attempts=[]
    def locked(source,target):
        attempts.append(source)
        if len(attempts)<3:
            assert json.loads(path.read_text())=={"reserved":1}
            raise PermissionError("sharing violation")
        replace(source,target)
    monkeypatch.setattr(config.os,'replace',locked);monkeypatch.setattr(config.time,'sleep',lambda _:None)
    config.write_json(path,{"reserved":2})
    assert json.loads(path.read_text())=={"reserved":2}
    assert len(attempts)==3 and list(tmp_path.iterdir())==[path]

def test_persistent_lock_preserves_ledger_and_raises(tmp_path,monkeypatch):
    path=tmp_path/'ledger.json';path.write_text('{"reserved":1}',encoding='utf-8')
    def locked(*_):raise PermissionError("sharing violation")
    monkeypatch.setattr(config.os,'replace',locked);monkeypatch.setattr(config.time,'sleep',lambda _:None)
    with pytest.raises(PermissionError):config.write_json(path,{"reserved":2})
    assert json.loads(path.read_text())=={"reserved":1}
    assert list(tmp_path.iterdir())==[path]
