SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CLIENT_SECRET_FILE = "json_files/client_secret_file.json"
CHROME_LOCATION = "/usr/bin/google-chrome"
PYTHON_LIB_LOCATION = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages"
QUIET_PATH = "/Users/ginoprasad/Scripts/miscellaneous/text_files/quiet.txt"

CHROME_PROFILES = {
	0: "Default",
	1: "Profile 1"
}

TOKEN_FILES = {
	0: "json_files/gcal_personal.json",
	1: "json_files/gcal_school.json"
}

OUTFILES = {
	0: "../schedules/gcal_personal.txt",
	1: "../schedules/gcal_school.txt"
}

ZOOM_SUBSTRINGS = ["Join Zoom Meeting", "Meeting URL"]
LINK_PREFIX = "https://"

HOURS_PER_DAY = 24
MIN_PER_HOUR = SECONDS_PER_MIN = 60
HOUR_THRESHOLD = 9

