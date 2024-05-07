from sqlalchemy import TIMESTAMP, Column, DECIMAL, Integer, String, func

from database import Base


class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    tryoutId = Column(Integer)
    userId = Column(Integer)

    amount = Column(DECIMAL(10, 2))
    status = Column(String)

    createdAt = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True), server_onupdate=func.now())
