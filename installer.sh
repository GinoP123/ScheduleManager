#!/usr/bin/env python3

import os, glob
import subprocess as sp

os.makedirs('cache', exist_ok=True)
os.makedirs('log', exist_ok=True)
os.makedirs('schedules', exist_ok=True)
os.makedirs('google_calendar/json_files', exist_ok=True)

with open('cache/events_cache.py', 'w') as outfile:
	outfile.write('events = []\n')

for file in ['schedules/gcal_personal.txt', 'schedules/gcal_school.txt', 'schedules/local_events.txt', 'schedules/local_weekly.txt', 'cache/m_cache.txt']:
	sp.run("touch " + file, shell=True)

shell = os.environ['SHELL']
shell = shell.strip().lstrip('-')
shell = sp.run("which " + shell, shell=True, capture_output=True).stdout.decode().strip()

if shell.strip().lstrip('-') == '':
	exit(1)

for file in glob.glob("*.sh") + glob.glob("*/*.sh") + glob.glob("bin/*"):
	with open(file) as infile:
		file_output = infile.read().replace('#!/bin/zsh', '#!' + shell)

	with open(file, 'w') as outfile:
		outfile.write(file_output)
