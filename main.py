from fastapi import FastAPI

from payment.router import router
from payment.websocket import router as ws_router


app = FastAPI(docs_url="/api/payment/docs")
app.include_router(router, prefix="/api/payment", tags=["payment"])
app.include_router(ws_router, prefix="/api/payment/ws", tags=["payment_ws"])


@app.get("/api/payment/health/")
async def main():
    return {"message" : "Server is running"}
