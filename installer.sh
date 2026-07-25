#!/usr/bin/env python3

import os, glob
import subprocess as sp

os.makedirs('cache', exist_ok=True)
os.makedirs('log', exist_ok=True)
os.makedirs('schedules', exist_ok=True)
os.makedirs('json_files', exist_ok=True)
os.makedirs('text_files', exist_ok=True)

with open('cache/events_cache.py', 'w') as outfile:
	outfile.write('events = []\n')

for file in ['schedules/gcal_personal.txt', 'schedules/gcal_school.txt', 'schedules/local_events.txt', 'schedules/local_weekly.txt', 'cache/m_cache.txt']:
	sp.run("touch " + file, shell=True)

