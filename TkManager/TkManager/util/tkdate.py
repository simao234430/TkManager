from datetime import datetime, timedelta, date

def get_today():
    return date.today()

def get_tomorrow():
    return date.today() + timedelta(1)

def get_yestoday():
    return date.today() - timedelta(1)

def get_first_day_of_week():
    return date.today() - timedelta(date.today().weekday())

def get_first_day_of_month():
    return date.today().replace(day=1)

