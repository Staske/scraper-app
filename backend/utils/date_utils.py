from datetime import datetime, timedelta

def convert_relative_date(relative_date):
    """
    Convert a relative date string (like '11d', '5h', '30m', '15s')
    into an absolute date/time string based on the current time.
    """
    now = datetime.now()
    try:
        if relative_date.endswith('d'):
            days = int(relative_date[:-1])
            full_date = now - timedelta(days=days)
        elif relative_date.endswith('h'):
            hours = int(relative_date[:-1])
            full_date = now - timedelta(hours=hours)
        elif relative_date.endswith('m'):
            minutes = int(relative_date[:-1])
            full_date = now - timedelta(minutes=minutes)
        elif relative_date.endswith('s'):
            seconds = int(relative_date[:-1])
            full_date = now - timedelta(seconds=seconds)
        else:
            full_date = now
        return full_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Error converting relative date:", e)
        return relative_date
