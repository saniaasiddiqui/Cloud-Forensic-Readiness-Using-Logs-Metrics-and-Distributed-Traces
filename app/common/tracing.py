from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

def setup_tracing(service_name: str):
    # Tracer Provider setup
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    
    # Auto-instrumentation enable karein
    FastAPIInstrumentor.instrument()
    HTTPXClientInstrumentor.instrument()
    
    return trace.get_tracer(service_name)