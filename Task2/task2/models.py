from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    role = Column(String)

class Checkout(Base):
    __tablename__ = "checkouts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)

    queue = relationship("Queue", back_populates="checkout", uselist=False)

class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True)
    checkout_id = Column(Integer, ForeignKey("checkouts.id"))
    people_count = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow)

    checkout = relationship("Checkout", back_populates="queue")