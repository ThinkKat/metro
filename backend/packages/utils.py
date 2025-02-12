import holidays
from datetime import date, datetime, timedelta

def op_date():
    return (datetime.now() - timedelta(hours = 4, minutes = 50)).date()
    
def check_holiday(date: date | str):
    # Metro operational hours: 04:50 - tomorrow 02:00
    holiday_kr = holidays.KR(years = date.year, language = "ko")
    is_weekend = (date.weekday() >= 5)
    is_holiday = date in holiday_kr
    return is_weekend or is_holiday
