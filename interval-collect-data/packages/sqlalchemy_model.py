from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Float, TIMESTAMP, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class MockRealtime(Base):
    __tablename__ = "test_realtimes"

    line_id = Column(Integer, nullable=False)
    station_id = Column(Integer, nullable=False)
    train_id = Column(String(10), nullable=False)
    received_at = Column(TIMESTAMP, nullable=False)
    train_status = Column(Integer, nullable=False)
    requested_at = Column(TIMESTAMP, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('line_id', 'station_id', 'train_id', 'train_status'),
    )
    
class Realtime(Base):
    __tablename__ = "realtimes"

    line_id = Column(Integer, nullable=False)
    station_id = Column(Integer, nullable=False)
    train_id = Column(String(10), nullable=False)
    received_at = Column(TIMESTAMP, nullable=False)
    train_status = Column(Integer, nullable=False)
    requested_at = Column(TIMESTAMP, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('line_id', 'station_id', 'train_id', 'train_status'),
    )