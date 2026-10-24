import httpx
from fastapi import FastAPI, HTTPException
from app.common.logging import get_logger

app = FastAPI(title="API Gateway")
logger = get_logger("api_gateway")

PAYMENT_SERVICE_URL = "http://localhost:8001"

@app.get("/health")
def health_check():
    logger.info("Gateway health check requested")
    return {"status": "healthy", "service": "api_gateway"}

@app.post("/payments")
async def gateway_payment(fail: str = None):
    log_context = {"extra": {"extra_fields": {"service": "api_gateway"}}}
    logger.info("Gateway received payment request. Forwarding to Payment Service...", **log_context)

    try:
        async with httpx.AsyncClient() as client:
            url = f"{PAYMENT_SERVICE_URL}/payments"
            if fail:
                url += f"?fail={fail}"
                
            response = await client.post(url, timeout=10.0)
            
            if response.status_code != 200:
                logger.error(f"Payment Service returned error: {response.status_code}", **log_context)
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
            
            logger.info("Gateway successfully received response from Payment Service", **log_context)
            return response.json()

    except httpx.RequestError as exc:
        logger.error(f"Gateway failed to reach Payment Service: {exc}", **log_context)
        raise HTTPException(status_code=503, detail="Payment Service is unavailable")