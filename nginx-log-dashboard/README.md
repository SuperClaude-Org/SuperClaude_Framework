# nginx-log-dashboard

Lightweight DMZ1 Nginx observability dashboard for offline or intranet deployments.

## Features

- FastAPI dashboard API with WebSocket metrics updates.
- Nginx access log parsing with Request ID correlation.
- Agent-based log ingestion for DMZ1 Nginx nodes.
- Static frontend with no build step or third-party browser dependencies.
- Offline deployment helper scripts and Python 3.7-compatible requirements.

## Project Layout

- `main.py` - FastAPI application, HTTP APIs, WebSocket endpoint, static dashboard.
- `metrics.py` - metrics aggregation for nodes, upstreams, routes, requests, alerts, and agents.
- `log_parser.py` - Nginx access log parser.
- `agent.py` - remote log collection agent.
- `static/` - dashboard HTML, CSS, and JavaScript.
- `start.sh` - dashboard startup script.
- `start_agent.sh` - agent startup script.
- `DEPLOY.md` - offline deployment notes.
- `bundle_offline.py` and `deploy_offline.py` - offline packaging helpers.

## Local Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export LOG_FILE_PATH="$PWD/sample_access.log"
python run_server.py
```

Then open `http://127.0.0.1:8000`.

## Server Start and Stop

For server deployments over SSH, use the background scripts so the process survives after the SSH session closes:

```bash
chmod +x start.sh start_server.sh stop_server.sh
./start_server.sh
./stop_server.sh
```

The background process writes its PID to `run/dashboard.pid` and logs to `logs/dashboard.log`.

## Dashboard Levels

The dashboard provides four static presentation levels for customer demos and staged product growth:

- `static/index1.html` - level 1, basic visibility with 3 core indicators.
- `static/index2.html` - level 2, runtime monitoring with 4 indicators.
- `static/index3.html` - level 3, link analysis with correlation, trend, status, and alerts.
- `static/index4.html` - level 4, full governance loop with all dashboard sections.

`static/index.html` remains unchanged as the default full dashboard entry.

## Deployment

For offline deployment, build or use the offline archive generated under `dist/` and follow `DEPLOY.md`.
Runtime dependency folders such as `pylib_py37/` are intentionally ignored by Git and should be regenerated or packaged as deployment artifacts.
