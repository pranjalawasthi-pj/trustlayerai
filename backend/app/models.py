from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_ref = Column(String, unique=True, index=True)
    product_id = Column(String, index=True)
    product_name = Column(String)
    seller = Column(String)
    amount = Column(Float)
    currency = Column(String, default="INR")
    status = Column(String, default="PENDING")
    trust_score = Column(Integer)
    paypal_order_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    severity = Column(String)
    description = Column(Text)
    product_id = Column(String, nullable=True)
    transaction_ref = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
