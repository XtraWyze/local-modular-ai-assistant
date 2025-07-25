import sys
import subprocess

from sanity_check import MODULES


def test_sanity_check_runs(tmp_path):
    result = subprocess.run(
        [sys.executable, 'sanity_check.py'], capture_output=True, text=True, check=True
    )
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    assert len(lines) == len(MODULES)
    for line in lines:
        assert line.startswith(('✅', '❌', '⚠️'))
    for mod in MODULES:
        assert any(mod in line for line in lines)
