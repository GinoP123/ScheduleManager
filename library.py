import datetime
import settings


def is_time_slot(line_data):
	if len(line_data) != 4 or line_data[2] != '-':
		return False

	try:
		get_time_slot(line_data)
	except AssertionError as e:
		print("HERE")
		return False
	return True

def get_time_slot(line_data):
	assert len(line_data) == 4
	date, start, _, end = line_data
	return (datetime.datetime.strptime(f"{date} {start}", settings.DATE_FORMAT),
			datetime.datetime.strptime(f"{date} {end}", settings.DATE_FORMAT))


def get_current_datetime():
	return datetime.datetime.now().replace(microsecond=0, second=0)


def is_attribute(line):
	return line.strip().startswith(settings.ATTRIBUTE_CHAR)


def get_attribute_data(line):
	assert line.startswith(settings.ATTRIBUTE_CHAR)
	return tuple(line.strip().lstrip(settings.ATTRIBUTE_CHAR).split())


def is_link(line_data):
	return line_data[0].startswith("https://") or line_data[0].startswith("Application:")


def get_link(line_data, source):
	if 'p' in source:
		line_data += ('0',)
	elif 's' in source:
		line_data += ('1',)
	return ' '.join(line_data)


def pad(num, length=2):
	if len(str(num)) == length:
		return str(num)
	elif len(str(num)) < length:
		return '0' * (length - len(str(num))) + str(num)

