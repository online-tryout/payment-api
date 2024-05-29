from datetime import datetime
import uuid
from pydantic import BaseModel


class TransactionBase(BaseModel):
    tryout_id: uuid.UUID
    user_id: uuid.UUID
    amount: float
    status: str

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionDetail(Transaction):
    tryout_name: str
    bank: str
    account_number: str
