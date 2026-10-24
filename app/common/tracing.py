from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

def setup_tracing(service_name: str):
    # 1. Tracer Provider set karein
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    
    # 2. Auto-instrumentation enable karein (Yeh headers inject aur extract karta hai)
    FastAPIInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    
    return trace.get_tracer(service_name)