# src/ledger/log.py
"""One JSON object per log line, so GitHub Actions logs (and anything else) can be searched by field."""

from __future__ import annotations

import json
import logging
import sys
import time


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        line = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname.lower(),
            "logger": record.name,
            "event": record.getMessage(),
            **getattr(record, "fields", {}),
        }
        if record.exc_info:
            line["exc"] = self.formatException(record.exc_info)
        return json.dumps(line, default=str)


class PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        fields = " ".join(f"{k}={v}" for k, v in getattr(record, "fields", {}).items())
        base = f"{time.strftime('%H:%M:%S')} {record.levelname:<7} {record.name}: {record.getMessage()}"
        line = f"{base} {fields}".rstrip()
        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        return line


def setup(level: str = "INFO", json_logs: bool = True) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter() if json_logs else PlainFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
    logging.getLogger("urllib3").setLevel("WARNING")


class Log:
    """log.info("pulled", rows=123, version="v20260424")"""

    def __init__(self, name: str):
        self._log = logging.getLogger(name)

    def debug(self, event: str, **fields) -> None:
        self._log.debug(event, extra={"fields": fields})

    def info(self, event: str, **fields) -> None:
        self._log.info(event, extra={"fields": fields})

    def warning(self, event: str, **fields) -> None:
        self._log.warning(event, extra={"fields": fields})

    def error(self, event: str, **fields) -> None:
        self._log.error(event, extra={"fields": fields})

    def exception(self, event: str, **fields) -> None:
        self._log.exception(event, extra={"fields": fields})


def get_logger(name: str) -> Log:
    return Log(name)
