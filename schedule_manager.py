#!/usr/bin/env python3

import datetime
import subprocess as sp

path = "/Users/ginoprasad/Scripts/schedule_manager/schedules/weekly_schedule.txt"


ATTRIBUTE_CHAR = "-"
DAYS={"U": "Sunday", "M": "Monday", "T": "Tuesday", "W": "Wednesday", "R": "Thursday", "F": "Friday", "S": "Saturday"}
DAY_TO_INT={"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
TIME_SUFFIXES={"AM": 0, "PM": 12}

def is_attribute(line):
	return line.strip().startswith(ATTRIBUTE_CHAR)


def get_attribute_data(line):
	assert line.startswith(ATTRIBUTE_CHAR)
	return line.strip().lstrip(ATTRIBUTE_CHAR).split()


def is_time_slot(line_data):
	if len(line_data) != 2 or not all([(ch in DAYS) for ch in line_data[0]]) or line_data[1][-2:] not in TIME_SUFFIXES:
		return False
	return True


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


def get_time_slot(line_data):
	assert len(line_data) == 2
	return (tuple([DAY_TO_INT[DAYS[ch]] for ch in line_data[0]]), abs_time(line_data[1]))


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


def parse():
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
			else:
				line_data = get_attribute_data(line)
				if is_time_slot(line_data):
					if get_time_slot(line_data) in time_slots:
						raise TypeError("ERROR: Multiple Events In Same Timeslot")
					time_slots.add(get_time_slot(line_data))
					curr["time_slot"] = get_time_slot(line_data)
				elif is_link(line_data):
					curr["links"].append(get_link(line_data))
				else:
					if line_data and line_data[0]:
						curr["descriptions"].append(' '.join(line_data))
		if curr:
			events.append(curr)
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
	events = parse()
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
	events = parse()
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
			sp.run(["/Users/ginoprasad/Scripts/schedule_manager/open_schedule.sh", outfile])
	elif distance <= 30:
		sp.run(f"say '{closest['name']} in {distance} minute{'s' if distance != 1 else ''}'".split(' '))
