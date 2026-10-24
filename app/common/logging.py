import json
import logging
import sys
from opentelemetry import trace

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # OpenTelemetry se current span nikalne ki direct koshish
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            log_record["trace_id"] = format(current_span.get_span_context().trace_id, '032x')
            log_record["span_id"] = format(current_span.get_span_context().span_id, '016x')
        
        if hasattr(record, "extra_fields"):
            log_record.update(record.extra_fields)
            
        return json.dumps(log_record)

def get_logger(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger