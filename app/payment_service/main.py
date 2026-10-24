import time
import uuid
from fastapi import FastAPI, HTTPException, Query
from app.common.logging import get_logger

app = FastAPI(title="Payment Service")
logger = get_logger("payment_service")

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "service": "payment_service"}

@app.post("/payments")
async def process_payment(
    fail: str = Query(None, description="Inject fault: 'timeout' or 'error'")
):
    transaction_id = str(uuid.uuid4())
    
    # Yahan hum 'extra' use kar rahe hain, 'extra_fields' nahi
    log_context = {"extra": {"extra_fields": {"transaction_id": transaction_id, "service": "payment_service"}}}
    
    logger.info(f"Received payment request: {transaction_id}", **log_context)
    
    if fail == "timeout":
        logger.warning("Injecting timeout delay", **log_context)
        time.sleep(3) 
        
    if fail == "error":
        logger.error("Injecting internal error", **log_context)
        raise HTTPException(status_code=500, detail="Simulated internal payment failure")

    time.sleep(0.1) 
    logger.info("Payment processed successfully", **log_context)
    return {
        "status": "success",
        "transaction_id": transaction_id,
        "amount": 100.00,
        "currency": "USD"
    }