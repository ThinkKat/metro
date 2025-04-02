from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, Float, TIMESTAMP, PrimaryKeyConstraint
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
    left_direction = Column(Integer, nullable=False)
    right_direction = Column(Integer, nullable=False)
    
class Transfers(Base):
    __tablename__ = "transfers"
    
    transfer_station_code = Column(String(10), nullable=False)
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
    
class Timetables(Base):
    __tablename__ = "timetables"
    
    line_id = Column(Integer, nullable=False)
    train_id = Column(String(10), nullable=False)
    first_station_name = Column(String(20), nullable = False)
    last_station_name = Column(String(20), nullable = False)
    first_last = Column(Integer, nullable = False)
    station_public_code = Column(String(10), nullable=False)
    day_code = Column(Integer, nullable=False)
    up_down = Column(Boolean, nullable=False)
    express = Column(Boolean, nullable=False)
    arrival_time = Column(Time)
    department_time = Column(Time)
    updated_at = Column(Date, nullable=False)
    end_date = Column(Date)
    realtime_train_id = Column(String(10), nullable=False)
    stop_no = Column(Integer, nullable=False)
    express_non_stop = Column(Boolean, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('line_id', 'train_id', 'station_public_code', 'day_code', "stop_no", "updated_at"),
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
    delayed_time = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint('line_id', 'station_id', 'train_id', 'train_status', 'stop_no' ,'op_date'),
    )