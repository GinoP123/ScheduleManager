import datetime
import settings


def is_attribute(line):
	return line.strip().startswith(settings.ATTRIBUTE_CHAR)


def get_attribute_data(line):
	assert line.startswith(settings.ATTRIBUTE_CHAR)
	return tuple(line.strip().lstrip(settings.ATTRIBUTE_CHAR).split())


def is_link(line_data):
	return line_data[0].startswith("https://") or line_data[0].startswith("Application:")


def get_link(line_data, source):
	if 'p' in source:
		line_data += ('0',)
	elif 's' in source:
		line_data += ('1',)
	return ' '.join(line_data)


def pad(num, length=2):
	if len(str(num)) == length:
		return str(num)
	elif len(str(num)) < length:
		return '0' * (length - len(str(num))) + str(num)


def get_time_name(hours, minutes):
	return f"{pad(hours % 12) if hours % 12 else 12} {pad(minutes)} {'AM' if hours < 12 else 'PM'}".split(' ')


def get_current_datetime_full():
	now = datetime.datetime.now()
	date = (now.month, now.day)
	return (date, get_current_datetime()[1])


def get_abs_days(date, year_month_days):
	(month, days), _ = date
	days_ = 0
	for month_num in range(month):
		if month_num == month - 1:
			days_ += days
		else:
			days_ += year_month_days[month_num]
	return days_


def first(d1, d2):
	for c1, c2 in zip(d1[0] + d1[1], d2[0] + d2[1]):
		if c1 > c2:
			return False
		elif c1 < c2:
			return True
	return True

