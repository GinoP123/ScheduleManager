#!/usr/bin/env python3

import os
import sys
import subprocess as sp
import library as lb
import settings
import datetime

def parse(source):
	path = settings.EVENTS_PATHS[source]
	events = []
	time_slots = set()

	with open(path) as infile:
		lines = infile.readlines()
		curr = {}
		for i, line in enumerate(lines):
			line = line.strip()
			if not line:
				continue
			elif not line.startswith(settings.ATTRIBUTE_CHAR):
				if curr and 'time_slot' in curr:
					curr["index"][1] = i
					events.append(curr)
				curr = {"name": line, "descriptions": [], "links": [], "index": [i, None], "source": source, "open_auto": False, "silence": False}
			elif "name" in curr:
				line_data = lb.get_attribute_data(line)

				if ' '.join(line_data).lower() == 'open automatically':
					curr["open_auto"] = True
				elif ' '.join(line_data).lower() == "silence notifications":
					curr["silence"] = True
				elif lb.is_time_slot(line_data):
					time_slot = lb.get_time_slot(line_data)
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
	for source in settings.EVENTS_PATHS:
		for event in parse(source):
			events.append(event)
	return events


def update_cache(events):
	with open(settings.CACHE_LOG_PATH, 'a') as outfile:
		now = lb.get_current_datetime()
		outfile.write(now.strftime(settings.DATE_FORMAT) + '\n')
	with open(settings.CACHE_PATH, 'w') as outfile:
		outfile.write("import datetime\n\nevents = [\n")
		for event in events:
			outfile.write(f"\t{event},\n")
		outfile.write("]\n")


def get_events():
	cache_mtime = os.path.getmtime(settings.CACHE_PATH)
	current_time = os.times().elapsed

	files_updated = any((os.path.getmtime(path) - cache_mtime >= 0 for path in settings.EVENTS_PATHS.values()))
	new_day = bool((current_time - cache_mtime) // (24 * 60 * 60))

	# TODO
	if True or files_updated or new_day:
		events = get_events_parse()
		update_cache(events)
	else:
		from cache.events_cache import events	
	return events


def update_m_cache():
	with open(settings.M_CACHE_PATH, 'r+') as file:
		meetings_str = print_meetings(silence_empty=False, to_str=True)
		if file.read() != meetings_str:
			file.seek(0)
			file.truncate()
			file.write(meetings_str)


def update_url_file(event, outfile_path):
	with open(outfile_path, 'w') as outfile:
		outfile.write("#!/bin/bash\n\n")
		outfile.write(': \'\n\n')
		outfile.write('\t' + event['name'] + '\n\n')
		for description in event["descriptions"]:
			outfile.write('\t' + description + "\n")
		outfile.write('\n\'\n\n')
		outfile.write(f'open_link_script="{os.getcwd()}/{settings.open_link_script}"\n')
		for link in event["links"]:
			profile = ""
			if not link.startswith("Application: ") and link.count(' '):
				profile = link.split()[1]
				link = link.split()[0]

			outfile.write(f'link="{link}"\n')
			outfile.write(f'"$open_link_script" "$link" "{profile}"\n')


def delete_event(event):
	path = settings.EVENTS_PATHS[event['source']]
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


def print_meetings(days=0, silence_empty=False, to_str=False):
	now = lb.get_current_datetime() + datetime.timedelta(days=int(days))
	day_name = now.strftime('%A')

	events = get_events()
	meetings = []
	
	for event in events:
		if now.date() == event['time_slot'][0].date():
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

	for event in sorted(meetings, key=lambda ev: ev['time_slot'][0]):
		name = event['name']
		time = event['time_slot'][0].strftime(settings.PRINT_FORMAT)
		time_string = f"\t\t{time}"
		message += '\t'.join((time_string, name)) + "\n"
		announcements.append(f"say {name} at {time}")

	if to_str:
		return message + '\n' if message else ''
	print(message)

	if settings.SPEAK:
		for announcement in announcements:
			sp.run(announcement.split())


def main():
	events = get_events()
	current_datetime = lb.get_current_datetime()

	if not events:
		exit(0)

	closest = min(events, key=lambda x: (x['time_slot'][0] - current_datetime).total_seconds())
	distance = (closest['time_slot'][0] - current_datetime).total_seconds() / 60
	if distance < 5:
		update_url_file(closest, settings.OUTFILE)
		if distance >= 0:
			sp.run([settings.open_file_script, settings.OUTFILE])
			if closest["open_auto"] and 'links' in closest:
				sp.run(f"{settings.shell_path} '{settings.schedule_open_url}'; exit", shell=True)
	elif (distance == 30 or distance < 15) and not closest["silence"]:
		plural = lambda x: 's' if x != 1 else ''
		sp.run(f"say '{closest['name']} in {distance} minute{plural(distance)}' 2> /dev/null", shell=True)
	update_m_cache()


if __name__ == '__main__':
	os.chdir(os.path.dirname(sys.argv[0]))
	if len(sys.argv) >= 2:
		if sys.argv[1] == 'print':
			print_meetings(*sys.argv[2:])
		else:
			raise TypeError("\n\tERROR: COMMAND NOT FOUND")
	else:
		main()