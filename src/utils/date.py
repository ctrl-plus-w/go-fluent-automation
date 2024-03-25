from datetime import datetime


def is_current_month(date: datetime) -> bool:
    """Return whether the date is of the same month as now"""
    return date.month == datetime.now().month

def is_current_month_and_year(date: datetime) -> bool:
    """Return whether the date is of the same month and year as now"""
    now = datetime.now()
    return date.month == now.month and date.year == now.year
