#!/usr/bin/env python3

import sys
import schedule_manager

if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "today"):
	schedule_manager.print_meetings()
elif (len(sys.argv) == 2 and sys.argv[1] == "tomorrow"):
	schedule_manager.print_tomorrows_meetings()
else:
	raise TypeError
