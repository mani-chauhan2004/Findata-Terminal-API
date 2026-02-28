import datetime
import json
import logging
import logging.handlers
from typing import override

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}

class CustomJSONFormatter(logging.Formatter):
    def __init__(
        self, 
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        log = self._prepare_log_dict(record)
        return json.dumps(log, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict:
        always_fields = {
            "message": record.getMessage(),
            "timestamp": datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)
        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class RotatingJSONLFileHandler(logging.handlers.RotatingFileHandler):

    def rotation_filename(self, default_name: str) -> str:
        if not default_name.startswith(self.baseFilename + "."):
            return default_name
        suffix = default_name[len(self.baseFilename) + 1 :]
        if suffix.isdigit():
            base_no_ext = self.baseFilename.rsplit(".jsonl", 1)[0]
            return f"{base_no_ext}.{suffix}.jsonl"
        return default_name


class NonErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO