"""Bounded DMZ1 Nginx metrics aggregation."""

import re
import threading
import time
from collections import Counter, defaultdict, deque
from typing import List


class MetricsCollector:
    _WINDOW_SEC = 60
    _TIMELINE_SEC = 30

    def __init__(self, max_samples: int = 10000):
        self.max_samples = max_samples
        self._lock = threading.RLock()
        self._records = deque()

    def add_request(self, data: dict) -> None:
        zone = str(data.get("zone", "DMZ1") or "DMZ1")
        if zone.upper() != "DMZ1":
            return
        now = time.time()
        timestamp = _number(data.get("timestamp"), now)
        record = {
            "timestamp": timestamp,
            "request_time": _number(data.get("request_time"), 0.0),
            "upstream_time": _number(data.get("upstream_time"), 0.0),
            "status": _integer(data.get("status"), 0),
            "url": str(data.get("url", "")),
            "route": _route_template(str(data.get("url", ""))),
            "method": str(data.get("method", "")),
            "source": str(data.get("source", "unknown")),
            "request_id": str(data.get("request_id", "")),
            "remote_addr": str(data.get("remote_addr", "")),
            "upstream": str(data.get("upstream", "")),
            "zone": "DMZ1",
            "agent_queue_pct": _number(data.get("agent_queue_pct"), 0.0),
            "agent_dropped": _integer(data.get("agent_dropped"), 0),
            "sample_rate": _number(data.get("sample_rate"), 1.0),
            "log_rate_bps": _number(data.get("log_rate_bps"), 0.0),
            "data_delay": max(0.0, now - timestamp),
        }
        with self._lock:
            self._records.append(record)
            while len(self._records) > self.max_samples:
                self._records.popleft()

    def get_metrics(self) -> dict:
        now = time.time()
        with self._lock:
            while (
                self._records
                and self._records[0]["timestamp"] < now - self._WINDOW_SEC
            ):
                self._records.popleft()
            records = list(self._records)
        if not records:
            return _empty_metrics()

        times = sorted(item["request_time"] for item in records)
        statuses = Counter(_status_group(item["status"]) for item in records)
        nodes = self._group_health(records, "source")
        upstreams = self._group_health(
            [item for item in records if item["upstream"]], "upstream"
        )
        routes = self._route_stats(records)
        traced = sum(1 for item in records if item["request_id"])
        return {
            "avg": round(sum(times) / len(times), 4),
            "p50": round(_percentile(times, 0.50), 4),
            "p95": round(_percentile(times, 0.95), 4),
            "p99": round(_percentile(times, 0.99), 4),
            "qps": round(len(records) / self._WINDOW_SEC, 2),
            "total_requests": len(records),
            "error_rate": round(statuses["5xx"] / len(records), 4),
            "client_error_rate": round(statuses["4xx"] / len(records), 4),
            "request_id_coverage": round(traced / len(records), 4),
            "node_count": len(nodes),
            "upstream_count": len(upstreams),
            "status_distribution": [
                {"name": name, "count": statuses[name]}
                for name in ("2xx", "3xx", "4xx", "5xx")
            ],
            "nodes": nodes,
            "upstreams": upstreams,
            "routes": routes,
            "alerts": self._alerts(
                nodes, upstreams, routes, statuses, len(records)
            )[:20],
            "agents": self._agent_health(records, now),
            "recent_timeline": self._build_timeline(records, now),
            "recent_requests": [dict(item) for item in records[-50:]],
        }

    def get_trace(self, request_id: str) -> dict:
        with self._lock:
            records = [
                dict(item)
                for item in self._records
                if item["request_id"] == request_id
            ]
        records.sort(key=lambda item: item["timestamp"])
        return {
            "trace_id": request_id,
            "hop_count": len(records),
            "total_time": round(max(
                [item["request_time"] for item in records] or [0.0]
            ), 4),
            "has_error": any(item["status"] >= 500 for item in records),
            "hops": records,
        }

    def _group_health(self, records, key):
        groups = defaultdict(list)
        for item in records:
            groups[item[key]].append(item)
        result = []
        for name, items in groups.items():
            times = sorted(item["request_time"] for item in items)
            errors = sum(1 for item in items if item["status"] >= 500)
            timeouts = sum(
                1 for item in items
                if item["status"] in (502, 503, 504)
                or item["request_time"] >= 3
            )
            error_rate = errors / len(items)
            p95 = _percentile(times, 0.95)
            result.append({
                "name": name,
                "requests": len(items),
                "qps": round(len(items) / self._WINDOW_SEC, 2),
                "share": 0.0,
                "p95": round(p95, 4),
                "error_rate": round(error_rate, 4),
                "timeouts": timeouts,
                "last_seen": max(item["timestamp"] for item in items),
                "status": "critical" if error_rate >= 0.05
                else "warning" if timeouts or p95 >= 1
                else "healthy",
            })
        total = sum(item["requests"] for item in result) or 1
        for item in result:
            item["share"] = round(item["requests"] / total, 4)
        return sorted(result, key=lambda item: item["requests"], reverse=True)

    def _route_stats(self, records):
        groups = defaultdict(list)
        for item in records:
            groups[item["route"]].append(item)
        result = []
        for route, items in groups.items():
            times = sorted(item["request_time"] for item in items)
            errors = sum(1 for item in items if item["status"] >= 500)
            result.append({
                "route": route,
                "requests": len(items),
                "p95": round(_percentile(times, 0.95), 4),
                "max": round(max(times), 4),
                "errors": errors,
                "error_rate": round(errors / len(items), 4),
            })
        return sorted(
            result,
            key=lambda item: (item["errors"], item["p95"], item["requests"]),
            reverse=True,
        )[:15]

    def _agent_health(self, records, now):
        latest = {}
        for item in records:
            current = latest.get(item["source"])
            if current is None or item["timestamp"] > current["timestamp"]:
                latest[item["source"]] = item
        return [
            {
                "name": name,
                "delay": round(item["data_delay"], 2),
                "queue_pct": round(item["agent_queue_pct"], 1),
                "dropped": item["agent_dropped"],
                "sample_rate": round(item["sample_rate"], 4),
                "log_rate_bps": round(item["log_rate_bps"], 0),
                "online": now - item["timestamp"] < 15,
            }
            for name, item in sorted(latest.items())
        ]

    def _alerts(self, nodes, upstreams, routes, statuses, total):
        alerts = []
        for item in nodes:
            if item["status"] != "healthy":
                alerts.append(_alert(
                    "节点异常", item["name"],
                    "P95 %.0fms / 5xx %.1f%%" % (
                        item["p95"] * 1000, item["error_rate"] * 100
                    ),
                    item["status"],
                ))
        for item in upstreams:
            if item["status"] != "healthy":
                alerts.append(_alert(
                    "上游异常", item["name"],
                    "超时 %d / 5xx %.1f%%" % (
                        item["timeouts"], item["error_rate"] * 100
                    ),
                    item["status"],
                ))
        for item in routes:
            if item["errors"] or item["p95"] >= 1:
                alerts.append(_alert(
                    "接口异常", item["route"],
                    "P95 %.0fms / 错误 %d" % (
                        item["p95"] * 1000, item["errors"]
                    ),
                    "critical" if item["errors"] else "warning",
                ))
        if total and statuses["5xx"] / total >= 0.03:
            alerts.append(_alert(
                "错误率告警", "DMZ1 总体",
                "5xx 比例 %.1f%%" % (statuses["5xx"] / total * 100),
                "critical",
            ))
        return alerts

    def _build_timeline(self, records: List[dict], now: float) -> List[dict]:
        buckets = {}
        for item in records:
            if item["timestamp"] < now - self._TIMELINE_SEC:
                continue
            buckets.setdefault(int(item["timestamp"]), []).append(item)
        return [
            {
                "time": second,
                "avg_time": round(
                    sum(item["request_time"] for item in items) / len(items), 4
                ),
                "p95_time": round(_percentile(sorted(
                    item["request_time"] for item in items
                ), 0.95), 4),
                "qps": len(items),
                "errors": sum(1 for item in items if item["status"] >= 500),
            }
            for second, items in sorted(buckets.items())
        ]


def _empty_metrics():
    return {
        "avg": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0,
        "qps": 0.0, "total_requests": 0, "error_rate": 0.0,
        "client_error_rate": 0.0, "request_id_coverage": 0.0,
        "node_count": 0, "upstream_count": 0,
        "status_distribution": [], "nodes": [], "upstreams": [],
        "routes": [], "alerts": [], "agents": [],
        "recent_timeline": [], "recent_requests": [],
    }


def _route_template(url):
    path = url.split("?", 1)[0]
    path = re.sub(r"/\d+(?=/|$)", "/:id", path)
    path = re.sub(
        r"/[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}(?=/|$)", "/:uuid", path
    )
    return path or "/"


def _status_group(status):
    if 200 <= status < 300:
        return "2xx"
    if 300 <= status < 400:
        return "3xx"
    if 400 <= status < 500:
        return "4xx"
    return "5xx" if status >= 500 else "other"


def _alert(kind, target, detail, level):
    return {
        "type": kind, "target": target, "detail": detail,
        "level": level, "timestamp": time.time(),
    }


def _number(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _integer(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _percentile(values: List[float], percentile: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    position = percentile * (len(values) - 1)
    low = int(position)
    high = min(low + 1, len(values) - 1)
    fraction = position - low
    return values[low] + fraction * (values[high] - values[low])
