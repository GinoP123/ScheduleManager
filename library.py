import datetime
import presets as pre


def is_attribute(line):
	return line.strip().startswith(pre.ATTRIBUTE_CHAR)


def get_attribute_data(line):
	assert line.startswith(pre.ATTRIBUTE_CHAR)
	return tuple(line.strip().lstrip(pre.ATTRIBUTE_CHAR).split())


def is_weekly_day(days_):
	return all([(ch in pre.DAYS) for ch in days_]) and days_


def abs_time(string):
	suffix = string[-2:]
	assert suffix in pre.TIME_SUFFIXES

	if ':' in string[:-2]:
		hour, minute = [int(t) for t in string[:-2].split(':')]
	else:
		hour = int(string[:-2])
		minute = 0

	if hour == 12:
		hour = 0

	hour += pre.TIME_SUFFIXES[suffix]
	return (hour, minute)


def is_time_slot(line_data, source):
	if len(line_data) != 2 or line_data[1][-2:] not in pre.TIME_SUFFIXES:
		return False

	hour, minute = abs_time(line_data[1])
	if not (0 <= hour < 24 and 0 <= minute < 60):
		return False

	if 'w' in source:
		return is_weekly_day(line_data[0])

	date = line_data[0].split('/')
	if len(date) != 2:
		return False
	month, day = map(lambda x: int(x.strip()), date)
	if first(get_current_datetime_full(), ((month, day), (hour, minute))):
		month_days = pre.MONTH_NUM_DAYS_THIS[month - 1]
	else:
		month_days = pre.MONTH_NUM_DAYS_NEXT[month - 1]

	return 0 < day <= month_days


def get_time_slot(line_data, source=True):
	assert len(line_data) == 2
	if 'w' in source:
		return (tuple([pre.DAY_TO_INT[pre.DAYS[ch]] for ch in line_data[0]]), abs_time(line_data[1]))
	else:
		return (tuple(map(lambda x: int(x), line_data[0].split('/'))), abs_time(line_data[1]))


def get_formatted_current_datetime():
	return datetime.datetime.now().strftime("%Y/%m/%d %H:%M")


def get_current_datetime():
	now = datetime.datetime.now()
	return (pre.DAY_TO_INT[now.strftime("%A")], abs_time(now.strftime("%I:%M%p")))


def time_distance(time_1, time_2):
	if type(time_2[0]) != int:
		return min([time_distance(time_1, (day, time_2[1])) for day in time_2[0]])
	distance = (((((time_2[0] - time_1[0]) % len(pre.DAYS)) * 24) + (time_2[1][0] - time_1[1][0])) * 60) + time_2[1][1] - time_1[1][1]
	return distance if distance >= 0 else (distance + (7 * 24 * 60))


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


def get_distance(d1, d2):
	date_1_days = get_abs_days(d1, pre.MONTH_NUM_DAYS_THIS)
	if first(d1, d2):
		date_2_days = get_abs_days(d2, pre.MONTH_NUM_DAYS_THIS)
	else:
		date_2_days = sum(pre.MONTH_NUM_DAYS_THIS) + get_abs_days(d2, pre.MONTH_NUM_DAYS_NEXT)
	return ((((date_2_days - date_1_days) * 24) + d2[1][0] - d1[1][0]) * 60) + d2[1][1] - d1[1][1]


def day_distance(d1, d2):
	return get_distance(d1, d2) // (24 * 60)


def get_day(datetime):
	curr_date = (get_current_datetime_full()[0], (0, 0))
	date = (datetime[0], (0, 0))
	day_dist = day_distance(curr_date, date)
	return (day_dist + get_current_datetime()[0]) % 7


