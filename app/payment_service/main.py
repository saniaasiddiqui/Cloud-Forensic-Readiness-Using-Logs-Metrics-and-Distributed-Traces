import time
import uuid
import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from app.common.logging import get_logger
from app.common.tracing import setup_tracing
from opentelemetry import trace
from opentelemetry.propagate import extract

app = FastAPI(title="Payment Service")
logger = get_logger("payment_service")
tracer = setup_tracing("payment_service")

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "service": "payment_service"}

@app.post("/payments")
async def process_payment(
    request: Request,
    fail: str = Query(None, description="Inject fault: 'timeout' or 'error'")
):
    # Gateway se aaye hue headers se trace context extract karein
    ctx = extract(dict(request.headers))
    
    # Extracted context ke sath naya span start karein
    with tracer.start_as_current_span("process_payment_span", context=ctx):
        transaction_id = str(uuid.uuid4())
        log_context = {"extra": {"extra_fields": {"transaction_id": transaction_id, "service": "payment_service"}}}
        
        logger.info(f"Received payment request: {transaction_id}", **log_context)
        
        if fail == "timeout":
            logger.warning("Injecting timeout delay", **log_context)
            time.sleep(3) 
            
        if fail == "error":
            logger.error("Injecting internal error", **log_context)
            
            # --- NAYA CODE: Forensic Backend ko incident bhejein ---
            current_span = trace.get_current_span()
            trace_id = format(current_span.get_span_context().trace_id, '032x') if current_span else "unknown"
            
            try:
                async with httpx.AsyncClient() as client:
                    # Port 8002 par chal rahe Forensic Backend ko call
                    await client.post("http://localhost:8002/incidents", json={
                        "incident_id": f"INC-{transaction_id[:8]}",
                        "trace_id": trace_id,
                        "service_name": "payment_service",
                        "severity": "HIGH",
                        "error_message": "Simulated internal payment failure"
                    }, timeout=5.0)
            except Exception as e:
                logger.error(f"Failed to send to forensic backend: {e}")
            # --------------------------------------------------------
            
            raise HTTPException(status_code=500, detail="Simulated internal payment failure")

        time.sleep(0.1) 
        logger.info("Payment processed successfully", **log_context)
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": 100.00,
            "currency": "USD"
        }