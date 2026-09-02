#!/usr/bin/env python3

import re
import datetime
import os, glob
import sys
import settings
import subprocess as sp

os.chdir(os.path.realpath(os.path.dirname(sys.argv[0])))

with open(settings.log_path) as infile:
    logging = infile.read()

date_regex = r'[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9, ]* [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]{3} [0-9]{4}'
matches = re.findall(date_regex, logging)
if not matches:
    exit(1)

index = logging.split('\n').index(matches[-1])
if '\n'.join(logging.split('\n')[index+1:]).strip() != '':
    emails = ' '.join([f"'{email}'" for email in settings.logging_emails])
    sp.run(f'"{settings.create_event_path}" "{settings.error_message}" 0 {emails}', shell=True)

