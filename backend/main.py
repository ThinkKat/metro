"""
1. Start collect service
2. Start fastapi server
"""

import subprocess

subprocess.Popen([".venv/bin/python", "-m", "services.collect.main"])
subprocess.Popen(["uvicorn", "api.main:app", "--port", "8000", "--log-config", "api/log_conf.yaml"])