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

if os.environ['SHELL'].strip() == '':
	exit(1)

for file in glob.glob("*.sh") + glob.glob("*/*.sh") + glob.glob("bin/*"):
	with open(file) as infile:
		file_output = infile.read().replace('#!/bin/bash', '#!' + os.environ['SHELL'])

	with open(file, 'w') as outfile:
		outfile.write(file_output)
