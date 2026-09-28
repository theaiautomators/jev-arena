from pathlib import Path
from arena.judge import args,MODEL,DISABLED

def test_judge_transport_has_no_direct_api_or_shell_interpolation(tmp_path):
    argv=args('codex',tmp_path)
    assert argv[-1]=='-'
    assert argv[argv.index('--model')+1]=='gpt-6-astra'
    assert argv[argv.index('--sandbox')+1]=='read-only'
    assert '--ignore-user-config' in argv
    assert 'shell_tool' in DISABLED and 'plugins' in DISABLED and 'apps' in DISABLED
    assert '--dangerously-bypass-approvals-and-sandbox' not in argv
