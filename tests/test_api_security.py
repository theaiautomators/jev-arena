import pytest
from fastapi.testclient import TestClient
from arena.api import app

def test_mutations_require_local_token_and_origin():
    client=TestClient(app)
    assert client.post('/api/runs',json={}).status_code==403
    token=client.get('/api/session').json()['token']
    assert client.post('/api/runs',json={},headers={'X-Arena-Token':token,'Origin':'https://attacker.example'}).status_code==403
    assert client.get('/api/session',headers={'Host':'attacker.example'}).status_code==403

def test_unknown_run_and_path_are_not_filesystem_reads():
    client=TestClient(app)
    assert client.get('/api/runs/unknown/results').status_code==404
    assert client.get('/api/not-an-endpoint').status_code==404
