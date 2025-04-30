"""
아마도 삭제하게 될수도 있는 모듈

이유
1. 지연시간 계산을 맞는 함수는 realtime_transform에서 처리
"""


import sqlite3x
import logging
import time
from datetime import date, datetime, timedelta

import holidays
import pandas as pd
from sqlalchemy import create_engine, select, text, insert, delete # TODO: Substitue to repository modules
from sqlalchemy.orm import Session

from .sqlalchemy_model import Base, MockRealtime, Delay
from .config import SQLITE_REALTIME_DB_PATH, POSTGRESQL_METRO_DB_URL


# TODO: Get from util module
def check_holiday(date: date | str):
    # Metro operational hours: 04:50 - tomorrow 02:00
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    
    holiday_kr = holidays.KR(years = date.year, language = "ko")
    is_weekend = (date.weekday() >= 5) # 5 - Saturday / 6 - Sunday
    is_holiday = date in holiday_kr
    return is_weekend or is_holiday

def load_timetable_data(op_date, day_code) -> pd.DataFrame:
    db_url = f"postgresql://{POSTGRESQL_METRO_DB_URL}"
    engine = create_engine(db_url)
    with Session(engine) as session:
        # load timetable data
        # using self attributes
        data = session.execute(text("""
                SELECT 
                    tb.*,
                    s.station_id,
                    s.station_name
                FROM timetables tb
                INNER JOIN stations s
                ON tb.line_id = s.line_id
                AND tb.station_public_code = s.station_public_code
                WHERE ((tb.updated_at <= :op_date AND tb.end_date > :op_date) OR (tb.end_date IS NULL))
                AND tb.day_code = :day_code
            """),
            {"op_date": op_date, "day_code": day_code}
        )
        tb = pd.DataFrame(data.fetchall(), columns = data.keys())
    return tb

def convert_train_id_new_bundang_line(df: pd.DataFrame):
    TIME_GAP = pd.Timedelta(minutes=40)

    # 새로운 열차 ID 컬럼 초기화
    df["new_train_id"] = 0
    current_train_id = 1

    for train_id, group in df.groupby("train_id"):
        last_station = None
        last_time = None

        for idx in group.index:
            row = df.loc[idx]
            if (
                last_station is not None and row["last_station_id"] != last_station  # 기준 1
            ) or (
                last_time is not None and (pd.to_datetime(row["received_at"]) - last_time) > TIME_GAP  # 기준 2 (30분 간격)
            ):
                current_train_id += 1  # 새로운 열차 ID 부여
            
            df.at[idx, "new_train_id"] = current_train_id

            # 마지막 상태 업데이트
            last_station = row["last_station_id"]
            last_time = pd.to_datetime(row["received_at"])

        current_train_id += 1  # 같은 train_id가 끝나면 새로운 ID
    
    # new_train_id를 train_id 컬럼으로 변경
    df = df.drop(columns=["train_id"]).rename(columns={"new_train_id": "train_id"})
    return df

def is_next_date(time: str):
    # time: HH:MM:SS
    # 4시 50분 이전인 경우, next_date 정보
    return (time[0:2] == "04" and time[4:6] < "50") or time[0:2] <= "03"

class DelayCalculator:
    def __init__(self, op_date: date | str):
        self.op_date = op_date
        self.next_date = (datetime.strptime(op_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        self.day_code = 9 if check_holiday(op_date) else 8
        self.tb = load_timetable_data(self.op_date, self.day_code)
        
    def _calculate_delayed_time(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.reset_index(drop=True).reset_index()
        
        # 지연시간 계산.
        data_no_join = data[data["line_id"].isin([1077])][["line_id", "station_id", "train_id", "received_at", "train_status", "requested_at"]]

        # 시간표 join
        data_join = data[~data["line_id"].isin([1077])]
        data_join = pd.merge(
            left = data_join[["line_id", "station_id", "train_id", "received_at", "train_status", "requested_at"]],
            right = self.tb.drop(columns = ["train_id"]),
            left_on = ["line_id", "train_id", "station_id"],
            right_on = ["line_id", "realtime_train_id", "station_id"],
            how = "inner"
        )
        
        data_join["received_at"] = data_join["received_at"].astype("string").str.split(" ", expand=True)[1].apply(lambda x : self.next_date + " " + x if is_next_date(x) else self.op_date + " " + x)
        data_join["arrival_datetime"] = data_join["arrival_time"]
        data_join.loc[~data_join["arrival_time"].isna(), "arrival_datetime"] = data_join.loc[~data_join["arrival_time"].isna(),"arrival_time"].astype("string").apply(lambda x : self.next_date + " " + x if is_next_date(x) else self.op_date + " " + x)
        data_join["department_datetime"] = data_join["department_time"]
        data_join.loc[~data_join["department_time"].isna(), "department_datetime"] = data_join.loc[~data_join["department_time"].isna(), "department_time"].astype("string").apply(lambda x : self.next_date + " " + x if is_next_date(x) else self.op_date + " " + x)

        dateformat = "ISO8601"

        data_join["received_at_dt"] = pd.to_datetime(data_join["received_at"].str.strip(), format=dateformat)
        data_join["arrival_datetime_dt"] = pd.to_datetime(data_join["arrival_datetime"].str.strip(), format=dateformat)
        data_join["department_datetime_dt"] = pd.to_datetime(data_join["department_datetime"].str.strip(), format=dateformat)
        
        data_join.loc[data_join["train_status"]<=1, "delayed_time"] = (data_join["received_at_dt"] - data_join["arrival_datetime_dt"]).dt.total_seconds()
        data_join.loc[data_join["train_status"]==2, "delayed_time"] = (data_join["received_at_dt"] - data_join["department_datetime_dt"]).dt.total_seconds()
        data_join.loc[data_join["train_status"]==0, "delayed_time"] -= 30
        
        data = pd.concat([data_no_join, data_join]).reset_index(drop=True)
        return data
        
    def run(self, data: pd.DataFrame,):
        print("Calculate Delayed time")
        data = self._calculate_delayed_time(data)
        return data
    
if __name__ == "__main__":
    db_url = f"sqlite://{SQLITE_REALTIME_DB_PATH}"
    engine = create_engine(db_url)
    op_date = "2025-03-30"
    with Session(engine) as session:
        select_stmt = text("SELECT * FROM test_realtimes")
        response = session.execute(select_stmt)
        df = pd.DataFrame(response.fetchall(), columns = response.keys())
    print(len(df))
    
    dc = DelayCalculator(op_date)
    join = dc.run(df).sort_values(["line_id", "received_at"])
    join["op_date"] = dc.op_date
    join["day_code"] = dc.day_code
    join = join.astype({"first_last": "Int16", "stop_no": "Int16"})
    join["stop_no"] = join["stop_no"].fillna(-1)
    
    db_url = f"postgresql://{POSTGRESQL_METRO_DB_URL}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    usecols = ["line_id", "station_id", "train_id", "received_at", "train_status", "requested_at", "day_code", "first_last", "stop_no", "delayed_time", "op_date"]
    with Session(engine) as session:
        delay_data = join[usecols].to_dict(orient="records")
        insert_stmt = insert(Delay).values(delay_data)
        session.execute(insert_stmt)
        session.commit()
    
    