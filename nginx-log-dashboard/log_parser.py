"""Parse and tail Nginx access logs with Request ID trace fields."""

import os
import re
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional


_LOG_PATTERN = re.compile(
    r'(?P<remote_addr>\S+)\s+-\s+(?P<remote_user>\S+)\s+'
    r'\[(?P<time_local>[^\]]+)\]\s+'
    r'"(?P<request>[^"]*)"\s+'
    r'(?P<rest>.*)$'
)
_KEY_VALUE = re.compile(r'([a-zA-Z_][\w-]*)=(?:"([^"]*)"|(\S+))')
_TOKEN_PATTERN = re.compile(r'"([^"]*)"|(\S+)')
_NGINX_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


def parse_nginx_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse supported Nginx logs and optional request tracing fields.

    Supported positional formats:
      test without request id:
        "$request" $status $body_bytes_sent $request_time
        $upstream_response_time "$referer" "$ua" "$xff" "$host"
      test with request id:
        "$request" $request_id $status $body_bytes_sent $request_time
        $upstream_response_time "$referer" "$ua" "$xff" "$host"
      production without request id:
        "$request" $status $request_length $body_bytes_sent $request_time
        "$referer" "$ua" "$xff"
      production with request id:
        "$request" $request_id $status $request_length $body_bytes_sent
        $request_time "$referer" "$ua" "$xff"

    The legacy key=value suffix is still accepted after combined logs.
    """
    match = _LOG_PATTERN.match(line.strip())
    if not match:
        return None
    data = match.groupdict()
    fields = _parse_rest(data.get("rest", ""))
    if fields is None:
        return None
    request_id = _clean_id(fields.get("request_id"))
    trace_id = _clean_id(fields.get("trace_id")) or request_id
    return {
        "timestamp": _parse_timestamp(data["time_local"]),
        "request_time": _as_float(fields.get("request_time")),
        "upstream_time": _as_float(fields.get("upstream_time")),
        "url": _extract_url(data.get("request", "")),
        "method": _extract_method(data.get("request", "")),
        "status": _as_int(fields.get("status")),
        "remote_addr": data.get("remote_addr", ""),
        "request_id": request_id,
        "trace_id": trace_id,
        "upstream": _clean_value(fields.get("upstream", "")),
        "zone": _clean_value(fields.get("zone", "")),
        "service": _clean_value(fields.get("service", "")),
        "request_length": _as_int(fields.get("request_length"), 0),
        "body_bytes_sent": _as_int(fields.get("body_bytes_sent"), 0),
        "host": _clean_value(fields.get("host", "")),
        "log_format": fields.get("log_format", ""),
    }


def tail_log(
    filepath: str,
    callback: Callable[[dict], None],
    poll_interval: float = 0.5,
) -> None:
    if not os.path.isfile(filepath):
        raise FileNotFoundError("Log file not found: %s" % filepath)
    stat = os.stat(filepath)
    last_inode = stat.st_ino
    last_size = stat.st_size
    try:
        while True:
            try:
                current = os.stat(filepath)
            except OSError:
                time.sleep(poll_interval)
                continue
            rotated = current.st_ino != last_inode or current.st_size < last_size
            if rotated:
                last_inode = current.st_ino
                last_size = 0
            if current.st_size <= last_size:
                time.sleep(poll_interval)
                continue
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as stream:
                    stream.seek(last_size)
                    for raw_line in stream:
                        record = parse_nginx_line(raw_line)
                        if record is not None:
                            try:
                                callback(record)
                            except Exception:
                                pass
                    last_size = stream.tell()
            except OSError:
                pass
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        pass


def _parse_rest(value: str) -> Optional[Dict[str, Any]]:
    tokens = _tokenize(value)
    if not tokens:
        return None

    index = 0
    request_id = ""
    if not _is_status(tokens[0]):
        request_id = tokens[0]
        index = 1
    if len(tokens) <= index or not _is_status(tokens[index]):
        return None

    status = tokens[index]
    tail = tokens[index + 1:]
    result = {
        "request_id": request_id,
        "status": status,
        "request_time": "0",
        "upstream_time": "0",
        "request_length": "0",
        "body_bytes_sent": "0",
        "host": "",
        "log_format": "",
    }

    # Test format:
    #   body_bytes_sent request_time upstream_response_time referer ua xff host
    if len(tail) >= 7 and _looks_float(tail[1]) and _looks_float(tail[2]):
        result.update({
            "body_bytes_sent": tail[0],
            "request_time": tail[1],
            "upstream_time": tail[2],
            "host": tail[6],
            "log_format": "test_with_request_id" if request_id
            else "test_without_request_id",
        })
        return result

    # Production format:
    #   request_length body_bytes_sent request_time referer ua xff
    if len(tail) >= 6 and _looks_float(tail[2]):
        result.update({
            "request_length": tail[0],
            "body_bytes_sent": tail[1],
            "request_time": tail[2],
            "log_format": "production_with_request_id" if request_id
            else "production_without_request_id",
        })
        return result

    return _parse_legacy_rest(tokens, request_id, status)


def _parse_legacy_rest(tokens, request_id, status):
    if len(tokens) < 4:
        return None
    tail = tokens[2:] if request_id else tokens[1:]
    if len(tail) < 2:
        return None
    extras_text = " ".join(tail[2:])
    extras = _parse_extras(extras_text)
    legacy_request_id = _clean_id(
        extras.get("request_id")
        or extras.get("req_id")
        or extras.get("x_request_id")
        or request_id
    )
    return {
        "request_id": legacy_request_id,
        "trace_id": _clean_id(extras.get("trace_id")) or legacy_request_id,
        "status": status,
        "body_bytes_sent": tail[0],
        "request_time": extras.get(
            "request_time", extras.get("rt", extras.get("_positional", "0"))
        ),
        "upstream_time": extras.get("upstream_time", extras.get("urt", "0")),
        "upstream": extras.get("upstream", ""),
        "zone": extras.get("zone", ""),
        "service": extras.get("service", ""),
        "request_length": "0",
        "host": "",
        "log_format": "legacy_key_value",
    }


def _parse_extras(value: str) -> Dict[str, str]:
    result = {}
    for match in _KEY_VALUE.finditer(value):
        result[match.group(1).lower()] = match.group(2) or match.group(3) or ""
    if result:
        return result
    tokens = value.split()
    if tokens:
        result["_positional"] = tokens[0]
    if len(tokens) > 1:
        result["request_id"] = tokens[1]
    if len(tokens) > 2:
        result["upstream"] = tokens[2]
    if len(tokens) > 3:
        result["upstream_time"] = tokens[3]
    return result


def _tokenize(value: str):
    return [
        match.group(1) if match.group(1) is not None else match.group(2)
        for match in _TOKEN_PATTERN.finditer(value.strip())
    ]


def _is_status(value: Any) -> bool:
    try:
        number = int(str(value))
    except (TypeError, ValueError):
        return False
    return 100 <= number <= 599


def _looks_float(value: Any) -> bool:
    if value in ("", "-", None):
        return True
    try:
        float(str(value).split(",")[0])
        return True
    except (TypeError, ValueError):
        return False


def _parse_timestamp(value: str) -> float:
    try:
        return datetime.strptime(value, _NGINX_TIME_FORMAT).timestamp()
    except (TypeError, ValueError):
        return time.time()


def _extract_url(request_line: str) -> str:
    parts = request_line.split()
    return parts[1] if len(parts) >= 2 else request_line


def _extract_method(request_line: str) -> str:
    parts = request_line.split()
    return parts[0] if parts else ""


def _as_float(value: Any) -> float:
    try:
        if value in ("", "-", None):
            return 0.0
        return float(str(value).split(",")[0])
    except (TypeError, ValueError):
        return 0.0


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clean_value(value: Any) -> str:
    text = str(value or "")
    return "" if text == "-" else text


def _clean_id(value: Any) -> str:
    text = _clean_value(value).strip()
    return text[:128]
