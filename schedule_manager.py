#!/usr/bin/env python3

import datetime
import subprocess as sp
import os


ATTRIBUTE_CHAR = "-"
DAYS={"U": "Sunday", "M": "Monday", "T": "Tuesday", "W": "Wednesday", "R": "Thursday", "F": "Friday", "S": "Saturday"}
DAY_TO_INT={"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
TIME_SUFFIXES={"AM": 0, "PM": 12}
YEAR=int(datetime.datetime.now().strftime("%Y"))


def get_month_days(year):
	month_num_days_=[(31 if not (month_num + (month_num // 7)) % 2 else 30) for month_num, month in enumerate(MONTHS)]
	month_num_days_[1] = (29 if (year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)) else 28)
	return tuple(month_num_days_)


MONTH_NUM_DAYS_THIS = get_month_days(YEAR)
MONTH_NUM_DAYS_NEXT = get_month_days(YEAR+1)


def is_attribute(line):
	return line.strip().startswith(ATTRIBUTE_CHAR)


def get_attribute_data(line):
	assert line.startswith(ATTRIBUTE_CHAR)
	return line.strip().lstrip(ATTRIBUTE_CHAR).split()


def is_time_slot(line_data, weekly):
	if len(line_data) != 2 or line_data[1][-2:] not in TIME_SUFFIXES:
		return False
	if weekly:
		return is_weekly_day(line_data[0])

	date = line_data[0].split('/')
	if len(date) != 2:
		return False
	month, day = map(lambda x: int(x.strip()), date)
	if first(get_current_datetime_full(), ((month, day), abs_time(line_data[1]))):
		month_days = MONTH_NUM_DAYS_THIS[month - 1]
	else:
		month_days = MONTH_NUM_DAYS_NEXT[month - 1]
	return 0 < day <= month_days


def is_weekly_day(days_):
	return all([(ch in DAYS) for ch in days_])


def abs_time(string):
	suffix = string[-2:]
	assert suffix in TIME_SUFFIXES

	if ':' in string[:-2]:
		hour, minute = [int(t) for t in string[:-2].split(':')]
	else:
		hour = int(string[:-2])
		minute = 0
	hour %= 12
	hour += TIME_SUFFIXES[suffix]
	return (hour, minute) 


def get_time_slot(line_data, weekly=True):
	assert len(line_data) == 2
	if weekly:
		return (tuple([DAY_TO_INT[DAYS[ch]] for ch in line_data[0]]), abs_time(line_data[1]))
	else:
		return (tuple(map(lambda x: int(x), line_data[0].split('/'))), abs_time(line_data[1]))


def get_current_datetime():
	now = datetime.datetime.now()
	return (DAY_TO_INT[now.strftime("%A")], abs_time(now.strftime("%I:%M%p")))


def time_distance(time_1, time_2):
	if type(time_2[0]) != int:
		return min([time_distance(time_1, (day, time_2[1])) for day in time_2[0]])
	distance = (((((time_2[0] - time_1[0]) % len(DAYS)) * 24) + (time_2[1][0] - time_1[1][0])) * 60) + time_2[1][1] - time_1[1][1]
	return distance if distance >= 0 else (distance + (7 * 24 * 60))


def is_link(line_data):
	return len(line_data) == 1 and line_data[0].startswith("https://")


def get_link(line_data):
	assert len(line_data) == 1
	return line_data[0]


def pad(num, length=2):
	if len(str(num)) == length:
		return str(num)
	elif len(str(num)) < length:
		return '0' * (length - len(str(num))) + str(num)


def get_time_name(hours, minutes):
	return f"{pad(hours % 12) if hours % 12 else 12} {pad(minutes)} {'AM' if hours < 12 else 'PM'}".split(' ')


def parse(path, weekly=True):
	events = []

	time_slots = set()

	with open(path) as infile:
		lines = infile.readlines()
		curr = {}
		for line in lines:
			line = line.strip()
			if not line:
				continue
			elif not line.startswith(ATTRIBUTE_CHAR):
				if curr and 'time_slot' in curr:
					events.append(curr)
				curr = {"name": line, "descriptions": [], "links": []}
			elif "name" in curr:
				line_data = get_attribute_data(line)
				if is_time_slot(line_data, weekly=weekly):
					time_slot = get_time_slot(line_data, weekly=weekly)
					if time_slot in time_slots:
						raise TypeError("ERROR: Multiple Events In Same Timeslot")
					time_slots.add(time_slot)
					curr["time_slot"] = time_slot
				elif is_link(line_data):
					curr["links"].append(get_link(line_data))
				else:
					if line_data and line_data[0]:
						curr["descriptions"].append(' '.join(line_data))
		if curr and 'time_slot' in curr:
			events.append(curr)
	return events


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
			days_ += year_month_days[month - 1]
	return days_

def first(d1, d2):
	for c1, c2 in zip(d1[0] + d1[1], d2[0] + d2[1]):
		if c1 > c2:
			return False
		elif c1 < c2:
			return True
	return True


def get_distance(d1, d2):
	this_year_month_days = get_month_days(YEAR)
	next_year_month_days = get_month_days(YEAR + 1)
	date_1_days = get_abs_days(d1, MONTH_NUM_DAYS_THIS)
	if first(d1, d2):
		date_2_days = get_abs_days(d2, MONTH_NUM_DAYS_THIS)
	else:
		date_2_days = sum(MONTH_NUM_DAYS_THIS) + get_abs_days(d2, MONTH_NUM_DAYS_NEXT)
	return ((((date_2_days - date_1_days) * 24) + d2[1][0] - d1[1][0]) * 60) + d2[1][1] - d1[1][1]



def day_distance(d1, d2):
	return get_distance(d1, d2) // (24 * 60)


def get_events_parse():
	weekly_path = "/Users/ginoprasad/Scripts/schedule_manager/schedules/weekly_schedule.txt"
	events_path = "/Users/ginoprasad/Scripts/schedule_manager/schedules/events.txt"
	events = parse(weekly_path)
	for event in parse(events_path, weekly=False):
		day_dist = day_distance(get_current_datetime_full(), event['time_slot'])
		if day_dist < len(DAYS):
			event['time_slot'] = (((get_current_datetime()[0] + event['time_slot'][0][1] - get_current_datetime_full()[0][1]),), event['time_slot'][1])
			events.append(event)
	return events



def update_cache(events, cache_path):
	with open(cache_path, 'w') as outfile:
		outfile.write("events = [\n")
		for event in events:
			outfile.write(f"\t{event},\n")
		outfile.write("]\n")



def get_events(cache_path="/Users/ginoprasad/Scripts/schedule_manager/cache/events_cache.py"):
	script_modified_time = os.path.getmtime(cache_path) // 60
	current_time = os.times().elapsed // 60

	if (current_time - script_modified_time) // (24 * 60):
		events = get_events_parse()
		update_cache(events, cache_path)
	else:
		from cache.events_cache import events
		return events



def update_url_file(event, outfile_path):
	with open(outfile_path, 'w') as outfile:
		outfile.write("import webbrowser\n\n")
		outfile.write('"""\n\n')
		outfile.write('\t' + event['name'] + '\n\n')
		for description in event["descriptions"]:
			outfile.write('\t' + description + "\n")
		outfile.write('\n"""\n\n')
		for link in event["links"]:
			outfile.write(f'url = "{link}"\n')
			outfile.write("webbrowser.open(url)\n")


def print_meetings():
	events = get_events()
	current_day = get_current_datetime()[0]

	meetings = []

	for event in events:
		if current_day in event['time_slot'][0]:
			meetings.append(event)

	print()
	if meetings:
		print("\tEvents Today:")
		sp.run("say Events Today".split())
	else:
		print("\tNo Events Today")
		sp.run("say No Events Today".split())

	for event in sorted(meetings, key=lambda ev: ev['time_slot'][1]):
		name = event['name']
		hours, minutes = event['time_slot'][1]
		time = get_time_name(*event['time_slot'][1])
		time_string = "\t\t{}:{} {}".format(*time)
		print('\t'.join((time_string, name)))
		sp.run(f"say {name} at {int(time[0])} {minutes if minutes else ''} {time[2]}".split())
	print()


def main():
	outfile = "/Users/ginoprasad/Scripts/schedule_manager/schedule_open_url.py"
	events = get_events()
	current_datetime = get_current_datetime()

	if not events:
		exit(0)

	closest = min(events, key=lambda x: time_distance(current_datetime, x['time_slot']))
	distance = time_distance(current_datetime, closest['time_slot'])

	open(outfile, 'w').close()
	if distance == 0:
		if closest["links"]:
			update_url_file(closest, outfile)
			sp.run("/Users/ginoprasad/Scripts/change_chrome_profile.sh 1".split(), capture_output=True)
			sp.run(["/Users/ginoprasad/Scripts/open_folder.sh", outfile])
	elif distance <= 30:
		sp.run(f"say '{closest['name']} in {distance} minute{'s' if distance != 1 else ''}'".split(' '))
