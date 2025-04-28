import holidays
from datetime import date, datetime, timedelta

def op_date(datetime_: datetime = datetime.now()) -> date:
    return (datetime_ - timedelta(hours = 4, minutes = 50)).date()
    
def check_holiday(date_: date | str) -> bool:
    # Metro operational hours: 04:50 - tomorrow 02:00
    if isinstance(date_, str):
        date_ = datetime.strptime(date_, "%Y-%m-%d")
    holiday_kr = holidays.KR(years = date_.year, language = "ko")
    is_weekend = (date_.weekday() >= 5)
    is_holiday = date_ in holiday_kr
    return is_weekend or is_holiday

def is_next_date(time: str) -> bool:
    # time: HH:MM:SS
    # 00시부터 4시 50분 사이인 경우, next_date 정보
    return (time[0:2] == "04" and time[3:5] < "50") or time[0:2] <= "03"