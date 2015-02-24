import subprocess
import sys
from pyvmmonitor_core.exec_external import kill_process


def test_kill_process():
    p = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(5)'])
    kill_process(p.pid, kill_children=True)
