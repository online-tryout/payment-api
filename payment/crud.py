import uuid
from sqlalchemy.orm import Session

from . import models, schema


def get_transaction(db: Session, transaction_id: uuid.UUID):
    return db.query(models.Transactions).filter(models.Transactions.id == transaction_id).first()


def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transactions).offset(skip).limit(limit).all()


def get_transactions_by_user(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Transactions).filter(models.Transactions.userId == user_id).offset(skip).limit(limit).all()


def get_transactions_by_tryout(db: Session, tryout_id: uuid.UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Transactions).filter(models.Transactions.tryoutId == tryout_id).offset(skip).limit(limit).all()


def create_transaction(db: Session, transaction: schema.TransactionCreate):
    db_transaction = models.Transactions(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def update_transaction(db: Session, transaction_id: uuid.UUID, updated_transaction: schema.TransactionCreate):
    transaction = get_transaction(db, transaction_id)
    for key, value in updated_transaction.dict().items():
        setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return transaction

