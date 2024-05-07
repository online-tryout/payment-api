from datetime import datetime
from pydantic import BaseModel


class TransactionBase(BaseModel):
    tryoutId: int
    userId: int
    amount: float
    status: str

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
