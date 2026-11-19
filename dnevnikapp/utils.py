from datetime import date, timedelta
def getWeekStart(day):
    return day - timedelta(days=day.weekday())
