#!/usr/bin/env python3
"""Push local Nginx access log records to a central dashboard."""

import json
import os
import queue
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from log_parser import tail_log


BASE_DIR = Path(__file__).resolve().parent
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", str(BASE_DIR / "sample_access.log"))
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://127.0.0.1:8000")
INGEST_TOKEN = os.environ.get("INGEST_TOKEN", "")
SOURCE_NAME = os.environ.get("SOURCE_NAME", socket.gethostname())
ZONE_NAME = os.environ.get("ZONE_NAME", "DMZ1")
SAMPLE_RATE = float(os.environ.get("SAMPLE_RATE", "1.0"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "50"))
FLUSH_INTERVAL = float(os.environ.get("FLUSH_INTERVAL", "2.0"))
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "0.5"))
QUEUE_SIZE = int(os.environ.get("QUEUE_SIZE", "100000"))

records_queue = queue.Queue(maxsize=QUEUE_SIZE)
stop_event = threading.Event()
dropped_records = 0


def enqueue_record(record: dict) -> None:
    global dropped_records
    record["source"] = SOURCE_NAME
    record["zone"] = ZONE_NAME
    record["agent_queue_pct"] = (
        records_queue.qsize() / float(QUEUE_SIZE) * 100 if QUEUE_SIZE else 0.0
    )
    record["agent_dropped"] = dropped_records
    record["sample_rate"] = SAMPLE_RATE
    try:
        records_queue.put_nowait(record)
    except queue.Full:
        dropped_records += 1
        if dropped_records == 1 or dropped_records % 1000 == 0:
            print(
                "[WARN] queue full, dropped_records=%s" % dropped_records,
                file=sys.stderr,
            )


def post_records(records):
    payload = json.dumps({"source": SOURCE_NAME, "records": records}).encode("utf-8")
    request = urllib.request.Request(
        DASHBOARD_URL.rstrip("/") + "/api/ingest",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Ingest-Token": INGEST_TOKEN,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        body = response.read().decode("utf-8")
        if response.status >= 300:
            raise RuntimeError("dashboard returned %s: %s" % (response.status, body))
        return body


def sender_loop():
    batch = []
    last_flush = time.time()
    while not stop_event.is_set():
        timeout = max(0.1, FLUSH_INTERVAL - (time.time() - last_flush))
        try:
            batch.append(records_queue.get(timeout=timeout))
        except queue.Empty:
            pass

        should_flush = batch and (
            len(batch) >= BATCH_SIZE or time.time() - last_flush >= FLUSH_INTERVAL
        )
        if not should_flush:
            continue

        while batch:
            try:
                post_records(batch)
                batch = []
                last_flush = time.time()
            except (urllib.error.URLError, OSError, RuntimeError) as exc:
                print("[WARN] push failed: %s; retrying in 5s" % exc, file=sys.stderr)
                time.sleep(5)


def main():
    print("Nginx log agent started")
    print("  log_file     : %s" % LOG_FILE_PATH)
    print("  dashboard_url: %s" % DASHBOARD_URL.rstrip("/"))
    print("  source_name  : %s" % SOURCE_NAME)
    print("  zone_name    : %s" % ZONE_NAME)
    print("  sample_rate  : %s" % SAMPLE_RATE)
    print("  auth_enabled : %s" % ("yes" if INGEST_TOKEN else "no"))
    print("  batch_size   : %s" % BATCH_SIZE)
    print("  queue_size   : %s" % QUEUE_SIZE)

    sender = threading.Thread(target=sender_loop, daemon=True)
    sender.start()
    try:
        tail_log(LOG_FILE_PATH, enqueue_record, poll_interval=POLL_INTERVAL)
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    main()
