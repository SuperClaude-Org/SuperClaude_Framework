@echo off
cd /d I:\codex\projects\logsview\nginx-log-dashboard
set PORT=8000
set LOG_FILE_PATH=I:\codex\projects\logsview\nginx-log-dashboard\sample_access.log
set DEMO_MODE=1
I:\python3.10.10\python.exe run_server.py
