from datetime import datetime


def pretty_date(date, date_format="%d %b %Y • %H:%M"):
    return datetime.strftime(datetime.fromisoformat(date), date_format)
