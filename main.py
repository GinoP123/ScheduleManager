#!/usr/bin/env python3

import schedule_manager
import sys
import os

os.chdir(os.path.dirname(sys.argv[0]))
os.environ["PATH"] = "/usr/local/bin:/usr/local/sbin:~/bin:/usr/bin:/bin:/usr/sbin:/sbin"
schedule_manager.main()
