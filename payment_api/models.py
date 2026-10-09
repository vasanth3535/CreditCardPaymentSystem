from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Numeric, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions_app_transaction"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    card_id = Column(BigInteger, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(10), nullable=False, default="PENDING")
    transaction_reference = Column(
        String(50),
        unique=True,
        nullable=False
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )