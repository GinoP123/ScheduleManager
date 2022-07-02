#!/usr/bin/env python3

import sys
import os
import schedule_manager

os.chdir(os.path.dirname(sys.argv[0]))
schedule_manager.create_event()
