#!/usr/bin/env python3

import os
import subprocess as sp
import library as lb
import presets as pre
import external_scripts as ext


def parse(path, weekly=True):
	events = []

	time_slots = set()

	with open(path) as infile:
		lines = infile.readlines()
		curr = {}
		for i, line in enumerate(lines):
			line = line.strip()
			if not line:
				continue
			elif not line.startswith(pre.ATTRIBUTE_CHAR):
				if curr and 'time_slot' in curr:
					curr["index"][1] = i
					events.append(curr)
				curr = {"name": line, "descriptions": [], "links": [], "index": [i, None], "weekly": weekly, "open_auto": False, "silence": False}
			elif "name" in curr:
				line_data = lb.get_attribute_data(line)

				if ' '.join(line_data).lower() == 'open automatically':
					curr["open_auto"] = True
				elif ' '.join(line_data).lower() == "silence notifications":
					curr["silence"] = True
				elif lb.is_time_slot(line_data, weekly=weekly):
					time_slot = lb.get_time_slot(line_data, weekly=weekly)
					if time_slot in time_slots:
						raise TypeError("ERROR: Multiple Events In Same Timeslot")
					time_slots.add(time_slot)
					curr["time_slot"] = time_slot
				elif lb.is_link(line_data):
					curr["links"].append(lb.get_link(line_data))
				else:
					if line_data and line_data[0]:
						curr["descriptions"].append(' '.join(line_data))
		if curr and 'time_slot' in curr:
			curr["index"][1] = i+1
			events.append(curr)
	return events


def get_events_parse():
	events = parse(pre.WEEKLY_PATH)
	for event in parse(pre.EVENTS_PATH, weekly=False):
		day_dist = lb.day_distance(lb.get_current_datetime_full(), event['time_slot'])
		if day_dist < len(pre.DAYS) or event['time_slot'][0] == lb.get_current_datetime_full()[0]:
			event['time_slot'] = ((lb.get_day(event['time_slot']),), event['time_slot'][1])
			events.append(event)
	return events


def update_cache(events, cache_path):
	with open(cache_path, 'w') as outfile:
		outfile.write("events = [\n")
		for event in events:
			outfile.write(f"\t{event},\n")
		outfile.write("]\n")


def get_events(cache_path="/Users/ginoprasad/Scripts/ScheduleManager/cache/events_cache.py"):
	script_mtime = (os.path.getmtime(cache_path) // 60)
	current_time = (os.times().elapsed // 60)

	weekly_mtime = (os.path.getmtime(pre.WEEKLY_PATH) // 60)
	events_mtime = (os.path.getmtime(pre.EVENTS_PATH) // 60)

	if (current_time - script_mtime) // (24 * 60) or (weekly_mtime - script_mtime >= 0) or (events_mtime - script_mtime >= 0):
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


def delete_event(event):
	path = WEEKLY_PATH if event["weekly"] else EVENTS_PATH
	start, end = event["index"]
	with open(path) as infile:
		lines = infile.readlines()

	if start and lines[start-1].strip() == "":
		start -= 1

	lines = lines[:start] + lines[end:]
	with open(path, 'w') as outfile:
		outfile.write(''.join(lines))


def convert_to_event_format(name, time_slot, link, description):
	time_slot = ' '.join(time_slot)
	information = (info for info in (name, time_slot, link, description) if info)
	return '\n\t- '.join(information) + '\n\n'


def get_new_event_data():
	name_question = "\tName: "
	weekly_question = "\tWeekly Event (y or n): "
	days_question = "\tDays: "
	date_question = "\tDate: "
	time_question = "\tTime: "
	link_question = "\tLink: "
	description_question = "\tDescription: "

	print()
	name = input(name_question).strip()
	while not name:
		name = input(name_question).strip()

	weekly = input(weekly_question).lower()
	while weekly not in ('y', 'n'):
		weekly = input(weekly_question).lower()
	weekly = True if weekly == 'y' else False

	date = time_slot = days = ""
	while not lb.is_time_slot(time_slot, weekly=weekly):
		if weekly:
			days = input(days_question).upper()
			while not lb.is_weekly_day(days):
				days = input(days_question).upper()
		else:
			date = input(date_question)
		
		time = input(time_question)
		time_slot = (f"{days}{date}", time)

	link = input(link_question).strip()
	while link and not lb.is_link((link,)):
		link = input(link_question).strip()

	description = input(description_question).strip()
	print()

	return convert_to_event_format(name, time_slot, link, description), weekly


def create_event():
	event, weekly = get_new_event_data()
	path = (pre.EVENTS_PATH, pre.WEEKLY_PATH)[int(weekly)]

	with open(path, 'a') as outfile:
		outfile.write(event)
	print("\tEvent Successfully Created!\n")


def print_meetings(current_datetime=None):
	suffix = "Remaining"
	if current_datetime is None:
		current_datetime = lb.get_current_datetime()
	else:
		suffix = "Tomorrow"

	events = get_events()
	meetings = []
	
	for event in events:
		if current_datetime[0] in event['time_slot'][0] and \
			lb.time_distance(current_datetime, event['time_slot']) < (24 * 60):
			meetings.append(event)

	announcements = []
	print()
	if meetings:
		print(f"\tEvents {suffix}:")
		announcements.append(f"say Events {suffix}")
	else:
		print(f"\tNo Events {suffix}")
		announcements.append(f"say No Events {suffix}")

	for event in sorted(meetings, key=lambda ev: ev['time_slot'][1]):
		name = event['name']
		hours, minutes = event['time_slot'][1]
		time = lb.get_time_name(*event['time_slot'][1])
		time_string = "\t\t{}:{} {}".format(*time)
		print('\t'.join((time_string, name)))
		announcements.append(f"say {name} at {int(time[0])} {minutes if minutes else ''} {time[2]}")
	print()

	if pre.SPEAK:
		for announcement in announcements:
			sp.run(announcement.split())


def print_tomorrows_meetings():
	current_datetime = ((lb.get_current_datetime()[0] + 1) % 7, (0, 0))
	print_meetings(current_datetime)


def main():
	events = get_events()
	current_datetime = lb.get_current_datetime()

	if not events:
		exit(0)

	closest = min(events, key=lambda x: lb.time_distance(current_datetime, x['time_slot']))
	distance = lb.time_distance(current_datetime, closest['time_slot'])

	if distance < 5:
		update_url_file(closest, pre.OUTFILE)
		sp.run(f"{ext.change_chrome_profile} 1".split(), capture_output=True)
		sp.run([ext.open_file_script, pre.OUTFILE])
		if closest["open_auto"]:
			import schedule_open_url
		if not closest['weekly']:
			delete_event(closest)
	elif (distance == 30 or distance < 15) and not closest["silence"]:
		plural = lambda x: 's' if x != 1 else ''
		sp.run(f"say '{closest['name']} in {distance} minute{plural(distance)}'".split(' '))

