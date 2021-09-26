from datetime import datetime

days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def weekdays(index=datetime.today().weekday(), reverse=True):
    days_list = list(days[index:] + days)[:7]
    if reverse:
        days_list.reverse()

    return days_list
