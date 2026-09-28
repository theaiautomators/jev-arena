import pytest
from arena.episodes import Warehouse,Tickets,run_episodes
from arena.contracts import Prediction

def test_independent_shortest_path_oracle_reaches_goal_for_all_seeds():
    for seed in range(5090,5110):
        env=Warehouse(seed)
        while not env.done:
            case=env.case();env.step(Prediction(case_id=case.id,model_id='oracle',status='ok',selected=case.gold,request_ms=1))
        assert env.result()['success'] and env.violations==0 and env.steps==10

async def test_deadline_misses_change_outcome_instead_of_only_annotation():
    class SlowOracle:
        id='oracle'
        async def predict(self,case,cap):return Prediction(case_id=case.id,model_id=self.id,status='ok',selected=case.gold,request_ms=600)
    fast=await run_episodes(SlowOracle(),2,0)
    late=await run_episodes(SlowOracle(),2,0,deadline_ms=500)
    assert all(e['success'] for e in fast)
    assert not any(e['success'] for e in late)
    assert all(e['deadline_misses']==e['steps'] for e in late)
