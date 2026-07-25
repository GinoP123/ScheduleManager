import os

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CLIENT_SECRET_FILE = "json_files/gcal_client_secret_file.json"

if os.path.exists("/usr/bin/google-chrome"):
	CHROME_LOCATION = "/usr/bin/google-chrome"
else:
	CHROME_LOCATION = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PYTHON_LIB_LOCATION = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages"

CHROME_PROFILES = {
	0: "Default",
	1: "Profile 2"
}

TOKEN_FILES = {
	0: "json_files/gcal_personal.json",
	1: "json_files/gcal_school.json"
}

OUTFILES = {
	0: "schedules/gcal_personal.txt",
	1: "schedules/gcal_school.txt"
}

ZOOM_SUBSTRINGS = ["Join Zoom Meeting", "Meeting URL"]
LINK_PREFIX = "https://"

HOURS_PER_DAY = 24
MIN_PER_HOUR = SECONDS_PER_MIN = 60
HOUR_THRESHOLD = 9

QUIET_PATH = "cache/quiet.txt"

open_link_script = "bin/open_url.sh"
schedule_open_url = "schedule_open_url.sh"
shell_path = "/bin/bash"

if os.path.exists("/usr/bin/subl"):
	open_file_script = "/usr/bin/subl"
elif os.path.exists("/usr/local/bin/subl"):
	open_file_script = "/usr/local/bin/subl"
else:
	open_file_script = "/usr/bin/vim"

