import os
import sys
import datetime

# Enables audible announcements for iterary
SPEAK = False

ATTRIBUTE_CHAR = "-"
DAYS={"U": "Sunday", "M": "Monday", "T": "Tuesday", "W": "Wednesday", "R": "Thursday", "F": "Friday", "S": "Saturday"}
DAY_TO_INT={"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
TIME_SUFFIXES={"AM": 0, "PM": 12}

YEAR=int(datetime.datetime.now().strftime("%Y"))

EVENTS_PATHS = {
	'lw': "schedules/local_weekly.txt",
	'le': "schedules/local_events.txt",
	'gp': "schedules/gcal_personal.txt",
	'gs': "schedules/gcal_school.txt"
}

OUTFILE = "schedule_open_url.sh"
CACHE_PATH = f"cache/events_cache.py"
CACHE_LOG_PATH = "log/cache_updates.txt"
M_CACHE_PATH = "cache/m_cache.txt"
PYTHON_LIB_LOCATION  = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages"


def get_month_days(year):
	month_num_days_=[(31 if not (month_num + (month_num // 7)) % 2 else 30) for month_num, month in enumerate(MONTHS)]
	month_num_days_[1] = (29 if (year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)) else 28)
	return tuple(month_num_days_)


MONTH_NUM_DAYS_THIS = get_month_days(YEAR)
MONTH_NUM_DAYS_NEXT = get_month_days(YEAR+1)


