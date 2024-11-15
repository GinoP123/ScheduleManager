#!/usr/bin/env python3

import os
import sys
import subprocess as sp
import library as lb
import presets as pre
import external_scripts as ext


def parse(source):
	path = pre.EVENTS_PATHS[source]
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
				curr = {"name": line, "descriptions": [], "links": [], "index": [i, None], "source": source, "open_auto": True, "silence": False}
			elif "name" in curr:
				line_data = lb.get_attribute_data(line)

				if ' '.join(line_data).lower() == 'do not open automatically':
					curr["open_auto"] = False
				elif ' '.join(line_data).lower() == "silence notifications":
					curr["silence"] = True
				elif lb.is_time_slot(line_data, source=source):
					time_slot = lb.get_time_slot(line_data, source=source)
					# if time_slot in time_slots:
					# 	raise TypeError("ERROR: Multiple Events In Same Timeslot")
					time_slots.add(time_slot)
					curr["time_slot"] = time_slot
				elif lb.is_link(line_data):
					curr["links"].append(lb.get_link(line_data, source))
				else:
					if line_data and line_data[0]:
						curr["descriptions"].append(' '.join(line_data))
		if curr and 'time_slot' in curr:
			curr["index"][1] = i+1
			events.append(curr)
	return events


def get_events_parse():
	events = []
	for source in pre.EVENTS_PATHS:
		if 'w' in source:
			events.extend(parse(source))
			continue
		for event in parse(source):
			day_dist = lb.day_distance(lb.get_current_datetime_full(), event['time_slot'])
			if day_dist < len(pre.DAYS) or event['time_slot'][0] == lb.get_current_datetime_full()[0]:
				event['time_slot'] = ((lb.get_day(event['time_slot']),), event['time_slot'][1])
				events.append(event)
	return events


def update_cache(events):
	with open(pre.CACHE_LOG_PATH, 'a') as outfile:
		outfile.write(lb.get_formatted_current_datetime() + '\n')
	with open(pre.CACHE_PATH, 'w') as outfile:
		outfile.write("events = [\n")
		for event in events:
			outfile.write(f"\t{event},\n")
		outfile.write("]\n")


def get_events():
	cache_mtime = os.path.getmtime(pre.CACHE_PATH)
	current_time = os.times().elapsed

	files_updated = any((os.path.getmtime(path) - cache_mtime >= 0 for path in pre.EVENTS_PATHS.values()))
	new_day = bool((current_time - cache_mtime) // (24 * 60 * 60))

	if files_updated or new_day:
		events = get_events_parse()
		update_cache(events)
	else:
		from cache.events_cache import events	
	return events


def update_m_cache():
	with open(pre.M_CACHE_PATH, 'r+') as file:
		meetings_str = print_meetings(0, 'silence', to_str=True)
		if file.read() != meetings_str:
			file.seek(0)
			file.truncate()
			file.write(meetings_str)


def update_url_file(event, outfile_path):
	with open(outfile_path, 'w') as outfile:
		outfile.write("#!/bin/zsh\n\n")
		# outfile.write("import subprocess as sp\n")
		# outfile.write('import external_scripts as ext\n\n')
		outfile.write(': \'\n\n')
		outfile.write('\t' + event['name'] + '\n\n')
		for description in event["descriptions"]:
			outfile.write('\t' + description + "\n")
		outfile.write('\n\'\n\n')
		outfile.write(f'open_link_script="{ext.open_link_script}"\n')
		for link in event["links"]:
			profile = ""
			if not link.startswith("Application: ") and link.count(' '):
				profile = link.split()[1]
				link = link.split()[0]

			outfile.write(f'link="{link}"\n')
			outfile.write(f'"$open_link_script" "$link" "{profile}"\n')


def delete_event(event):
	path = pre.EVENTS_PATHS[event['source']]
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

	weekly = input(weekly_question).strip().lower()
	while weekly not in ('y', 'n'):
		weekly = input(weekly_question).strip().lower()
	source = 'lw' if weekly == 'y' else 'le'

	date = time_slot = days = ""
	while not lb.is_time_slot(time_slot, source=source):
		if weekly == 'y':
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

	return convert_to_event_format(name, time_slot, link, description), source


def create_event():
	event, source = get_new_event_data()
	path = pre.EVENTS_PATHS[source]

	with open(path, 'a') as outfile:
		outfile.write(event)
	print("\tEvent Successfully Created!\n")


def print_meetings(day_diff='0', silence_empty=False, to_str=False):
	current_datetime, day_diff, silence_empty = lb.get_current_datetime(), int(day_diff), silence_empty == 'silence'
	if day_diff != 0:
		current_datetime = ((current_datetime[0] + day_diff) % 7, (0, 0))
	day_name = list(pre.DAY_TO_INT.keys())[current_datetime[0]]

	events = get_events()
	meetings = []
	
	for event in events:
		if current_datetime[0] in event['time_slot'][0] and \
			lb.time_distance(current_datetime, event['time_slot']) < (24 * 60):
			meetings.append(event)

	message = ""
	announcements = []
	if meetings:
		message += f"\n\tEvents {day_name}:\n"
		announcements.append(f"say Events {day_name}")
	else:
		if not silence_empty:
			message += f"\n\tNo Events {day_name}\n"
			announcements.append(f"say No Events {day_name}")

	for event in sorted(meetings, key=lambda ev: ev['time_slot'][1]):
		name = event['name']
		hours, minutes = event['time_slot'][1]
		time = lb.get_time_name(*event['time_slot'][1])
		time_string = "\t\t{}:{} {}".format(*time)
		message += '\t'.join((time_string, name)) + "\n"
		announcements.append(f"say {name} at {int(time[0])} {minutes if minutes else ''} {time[2]}")

	if to_str:
		return message + '\n' if message else ''
	print(message)

	if pre.SPEAK:
		for announcement in announcements:
			sp.run(announcement.split())


def main():
	events = get_events()
	current_datetime = lb.get_current_datetime()

	if not events:
		exit(0)

	closest = min(events, key=lambda x: lb.time_distance(current_datetime, x['time_slot']))
	distance = lb.time_distance(current_datetime, closest['time_slot'])

	if distance < 5:
		update_url_file(closest, pre.OUTFILE)
		sp.run([ext.open_file_script, pre.OUTFILE])
		if closest["open_auto"] and 'links' in closest:
			sp.run(f"/opt/homebrew/bin/ttab '{ext.schedule_open_url}; exit'", shell=True)
		if closest['source'] == 'le':
			delete_event(closest)
	elif (distance == 30 or distance < 15) and not closest["silence"]:
		plural = lambda x: 's' if x != 1 else ''
		sp.run(f"say '{closest['name']} in {distance} minute{plural(distance)}' 2> /dev/null", shell=True)
	update_m_cache()


if __name__ == '__main__':
	os.chdir(os.path.dirname(sys.argv[0]))
	sys.path.append(pre.PYTHON_LIB_LOCATION)
	if len(sys.argv) >= 2:
		if sys.argv[1] == 'print':
			print_meetings(*sys.argv[2:])
		else:
			raise TypeError("\n\tERROR: COMMAND NOT FOUND")
	else:
		main()