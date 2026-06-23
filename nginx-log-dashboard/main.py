"""DMZ1 Nginx observability dashboard API."""

import asyncio
import logging
import os
import threading
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from websockets.exceptions import ConnectionClosed

from log_parser import tail_log
from metrics import MetricsCollector


logger = logging.getLogger("nginx-log-dashboard")
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE_PATH = os.environ["LOG_FILE_PATH"]
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "0.5"))
INGEST_TOKEN = os.environ.get("INGEST_TOKEN", "")
DEMO_MODE = os.environ.get("DEMO_MODE", "") == "1"
WS_INTERVAL = 2

collector = MetricsCollector(max_samples=10000)
_tailer_thread = None
_demo_thread = None
app = FastAPI(title="DMZ1 Nginx Dashboard")
static_dir = BASE_DIR / "static"
PUBLIC_BASE_PATH = os.environ.get(
    "DASHBOARD_BASE_PATH", "/nginx-log-dashboard"
).strip()
if PUBLIC_BASE_PATH and not PUBLIC_BASE_PATH.startswith("/"):
    PUBLIC_BASE_PATH = "/" + PUBLIC_BASE_PATH
PUBLIC_BASE_PATH = PUBLIC_BASE_PATH.rstrip("/")
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
if PUBLIC_BASE_PATH:
    app.mount(
        f"{PUBLIC_BASE_PATH}/static",
        StaticFiles(directory=str(static_dir)),
        name="prefixed_static",
    )


def _on_log_record(record):
    record.setdefault("source", "dmz1-local")
    record["zone"] = "DMZ1"
    collector.add_request(record)


def _tail_blocking():
    while True:
        try:
            tail_log(LOG_FILE_PATH, _on_log_record, poll_interval=POLL_INTERVAL)
        except FileNotFoundError:
            logger.warning("Log file not found: %s", LOG_FILE_PATH)
            time.sleep(5)
        except Exception as exc:
            logger.error("Tailer error: %s", exc)
            time.sleep(5)


def _demo_loop():
    nodes = ["dmz1-nginx-01", "dmz1-nginx-02", "dmz1-nginx-03"]
    upstreams = [
        "10.20.1.10:8080", "10.20.1.11:8080",
        "10.20.1.12:8080", "10.20.2.20:9000",
    ]
    urls = [
        "/api/policy/query", "/api/customer/profile",
        "/api/order/submit", "/api/payment/status",
        "/static/config.json", "/health",
    ]
    sequence = 0
    while True:
        request_id = "dmz1-%s-%05d" % (
            time.strftime("%H%M%S"), sequence % 100000
        )
        incident = sequence % 9 == 8
        for index in range(12):
            duration = 0.025 + (index % 5) * 0.028 + (sequence % 4) * 0.01
            status = 404 if index % 11 == 0 else 200
            if incident and index in (3, 8):
                duration = 1.25 + index * 0.02
                status = 504 if index == 8 else 502
            collector.add_request({
                "timestamp": time.time(),
                "request_time": duration,
                "upstream_time": max(0.0, duration - 0.01),
                "url": urls[(sequence + index) % len(urls)],
                "method": "POST" if index % 4 == 0 else "GET",
                "status": status,
                "request_id": request_id,
                "zone": "DMZ1",
                "source": nodes[(sequence + index) % len(nodes)],
                "upstream": upstreams[(sequence * 2 + index) % len(upstreams)],
                "remote_addr": "10.10.8.%d" % (20 + index),
                "agent_queue_pct": 12 + (sequence + index) % 18,
                "agent_dropped": 0 if sequence % 13 else 2,
                "sample_rate": 0.01,
                "log_rate_bps": 420000 + index * 18000,
            })
        sequence += 1
        time.sleep(2)


@app.on_event("startup")
async def startup():
    global _tailer_thread, _demo_thread
    _tailer_thread = threading.Thread(target=_tail_blocking, daemon=True)
    _tailer_thread.start()
    if DEMO_MODE:
        _demo_thread = threading.Thread(target=_demo_loop, daemon=True)
        _demo_thread.start()


PREFIX_DISABLED = "/__disabled_prefix__"


@app.get("/")
@app.get(f"{PUBLIC_BASE_PATH}/" if PUBLIC_BASE_PATH else f"{PREFIX_DISABLED}/")
async def index():
    return HTMLResponse((static_dir / "index.html").read_text(encoding="utf-8"))


@app.get(PUBLIC_BASE_PATH if PUBLIC_BASE_PATH else PREFIX_DISABLED)
async def prefixed_index_redirect():
    return RedirectResponse(f"{PUBLIC_BASE_PATH}/")


@app.get("/api/metrics")
@app.get(
    f"{PUBLIC_BASE_PATH}/api/metrics"
    if PUBLIC_BASE_PATH else f"{PREFIX_DISABLED}/api/metrics"
)
async def api_metrics():
    return collector.get_metrics()


@app.post("/api/ingest")
@app.post(
    f"{PUBLIC_BASE_PATH}/api/ingest"
    if PUBLIC_BASE_PATH else f"{PREFIX_DISABLED}/api/ingest"
)
async def ingest(data: dict, x_ingest_token: str = Header(default="")):
    if INGEST_TOKEN and x_ingest_token != INGEST_TOKEN:
        raise HTTPException(status_code=401, detail="invalid ingest token")
    records = data.get("records") if isinstance(data.get("records"), list) else [data]
    source = str(data.get("source", "dmz1-remote"))
    accepted = 0
    ignored = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        if str(record.get("zone", "DMZ1")).upper() != "DMZ1":
            ignored += 1
            continue
        try:
            normalized = {
                "timestamp": float(record.get("timestamp", time.time())),
                "request_time": float(record.get("request_time", 0.0)),
                "upstream_time": float(record.get("upstream_time", 0.0)),
                "url": str(record.get("url", "")),
                "method": str(record.get("method", "")),
                "status": int(record.get("status", 0)),
                "source": str(record.get("source", source)),
                "request_id": str(record.get("request_id", "")),
                "remote_addr": str(record.get("remote_addr", "")),
                "upstream": str(record.get("upstream", "")),
                "zone": "DMZ1",
                "agent_queue_pct": float(record.get("agent_queue_pct", 0.0)),
                "agent_dropped": int(record.get("agent_dropped", 0)),
                "sample_rate": float(record.get("sample_rate", 1.0)),
                "log_rate_bps": float(record.get("log_rate_bps", 0.0)),
            }
        except (TypeError, ValueError):
            continue
        collector.add_request(normalized)
        accepted += 1
    return {"accepted": accepted, "ignored_non_dmz1": ignored}


@app.get("/api/traces/{request_id}")
@app.get(
    f"{PUBLIC_BASE_PATH}/api/traces/{{request_id}}"
    if PUBLIC_BASE_PATH else f"{PREFIX_DISABLED}/api/traces/{{request_id}}"
)
async def trace_detail(request_id: str):
    trace = collector.get_trace(request_id)
    if not trace["hops"]:
        raise HTTPException(status_code=404, detail="request not found")
    return trace


@app.websocket("/ws")
@app.websocket(
    f"{PUBLIC_BASE_PATH}/ws" if PUBLIC_BASE_PATH else f"{PREFIX_DISABLED}/ws"
)
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(collector.get_metrics())
            await asyncio.sleep(WS_INTERVAL)
    except (WebSocketDisconnect, ConnectionClosed):
        pass


@app.get("/api/debug")
@app.get(
    f"{PUBLIC_BASE_PATH}/api/debug"
    if PUBLIC_BASE_PATH else f"{PREFIX_DISABLED}/api/debug"
)
async def debug():
    return {
        "tailer_thread_alive": bool(
            _tailer_thread and _tailer_thread.is_alive()
        ),
        "collector_total": collector.get_metrics()["total_requests"],
        "log_file": LOG_FILE_PATH,
        "zone": "DMZ1",
        "demo_mode": DEMO_MODE,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
