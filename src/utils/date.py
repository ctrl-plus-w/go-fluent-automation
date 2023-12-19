from datetime import datetime


def is_current_month(date: datetime) -> bool:
    """Return whether the date is of the same month as now"""
    return date.month == datetime.now().month
