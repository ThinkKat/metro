from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Float, TIMESTAMP, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Regions(Base):
    __tablename__ = "regions"
    
    region_id = Column(Integer, primary_key=True, autoincrement=True)
    region_name = Column(String(10), nullable=False)
    
class Lines(Base):
    __tablename__ = "lines"
    
    line_id = Column(Integer, primary_key=True)
    line_name = Column(String(20), nullable=False)
    line_color = Column(String(6), nullable=False)
    region_id = Column(Integer, nullable=False)
    
class Stations(Base):
    __tablename__ = "stations"
    
    line_id = Column(Integer, nullable=False)
    station_code = Column(String(10), nullable=False)
    station_public_code = Column(String(10),  primary_key=True, nullable=False)
    station_id = Column(Integer)
    station_name = Column(String(20), nullable=False)
    request_station_name = Column(String(20), nullable=False)
    left_station_public_code = Column(String(20))
    right_station_public_code = Column(String(20))
    left_station_name = Column(String(40))
    right_station_name = Column(String(40))
    left = Column(Integer, nullable=False)
    right = Column(Integer, nullable=False)
    
class Transfers(Base):
    __tablename__ = "transfers"
    
    transfer_station_code = Column(String(10))
    station_name = Column(String(20), nullable=False)
    line_id = Column(Integer, nullable=False)
    line_name = Column(String(20), nullable=False)
    station_public_code = Column(String(10), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('transfer_station_code', 'line_id'),
    )
    
class Connections(Base):
    __tablename__ = "connections"
    
    line_id = Column(Integer, nullable=False)
    from_station_public_code = Column(String(10), nullable=False)
    to_station_public_code = Column(String(10), nullable=False)
    direction = Column(String(10), nullable=False)
    up_down = Column(Boolean, nullable=False)
    movable = Column(Boolean, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('from_station_public_code', 'to_station_public_code'),
    )

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

class Delay(Base):
    __tablename__ = "delay"
    
    line_id = Column(Integer, nullable=False)
    station_id = Column(Integer, nullable=False)
    train_id = Column(String(10), nullable=False)
    received_at = Column(TIMESTAMP, nullable=False)
    train_status = Column(Integer, nullable=False)
    requested_at = Column(TIMESTAMP, nullable=False)
    day_code = Column(Integer, nullable=False)
    first_last = Column(Integer, nullable=True)
    stop_no = Column(Integer, nullable=False)
    op_date = Column(Date, nullable=False)
    delayed_time = Column(Float, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('line_id', 'station_id', 'train_id', 'train_status', 'stop_no' ,'op_date'),
    )