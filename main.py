from fastapi import FastAPI

from payment.router import router
from payment import models
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router, prefix="/api/payment", tags=["payment"])


@app.get("/")
async def main():
    return {"message" : "Server is running"}
