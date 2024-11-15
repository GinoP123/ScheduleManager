#!/usr/bin/env python3

import os, glob

os.makedirs('cache', exist_ok=True)
os.makedirs('log', exist_ok=True)

with open('cache/events_cache.py', 'w') as outfile:
	outfile.write('events = []\n')

if os.environ['SHELL'].strip() == '':
	exit(1)

for file in glob.glob("*.sh") + glob.glob("*/*.sh") + glob.glob("bin/*"):
	with open(file) as infile:
		file_output = infile.read().replace('#!/bin/zsh', '#!' + os.environ['SHELL'])

	with open(file, 'w') as outfile:
		outfile.write(file_output)
