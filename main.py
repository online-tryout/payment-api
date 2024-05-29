from fastapi import FastAPI

from payment.router import router


app = FastAPI()
app.include_router(router, prefix="/api/payment", tags=["payment"])


@app.get("/")
async def main():
    return {"message" : "Server is running"}
