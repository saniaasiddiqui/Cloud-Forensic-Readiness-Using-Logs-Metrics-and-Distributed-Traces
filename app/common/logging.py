import json
import logging
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        # Python logging uses 'extra' dictionary
        if hasattr(record, "extra_fields"):
            log_record.update(record.extra_fields)
            
        redact_keys = ["password", "token", "secret", "credit_card"]
        for key in redact_keys:
            if key in log_record:
                log_record[key] = "[REDACTED]"
        return json.dumps(log_record)

def get_logger(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger