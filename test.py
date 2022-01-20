date_1 = ((1, 19), (14, 43))
date_2 = ((1, 18), (14, 42))

YEAR = 2022


def get_month_days(year):
	month_num_days_=[(31 if not (month_num + (month_num // 7)) % 2 else 30) for month_num, month in enumerate(MONTHS)]
	month_num_days_[1] = (29 if (year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)) else 28)
	return tuple(month_num_days_)


def get_abs_days(date, year_month_days):
	(month, days), _ = date
	days_ = 0
	for month_num in range(month):
		if month_num == month - 1:
			days_ += days
		else:
			days_ += year_month_days[month - 1]
	return days_

def first(d1, d2):
	d1 = d1[0] + d1[1]
	d2 = d2[0] + d2[1]
	for c1, c2 in zip(d1, d2):
		if c1 > c2:
			return False
		elif c1 < c2:
			return True
	return True


def get_distance(d1, d2):
	this_year_month_days = get_month_days(YEAR)
	next_year_month_days = get_month_days(YEAR + 1)
	date_1_days = get_abs_days(date_1, this_year_month_days)
	if first(d1, d2):
		date_2_days = get_abs_days(date_2, this_year_month_days)
	else:
		date_2_days = sum(this_year_month_days) + get_abs_days(date_2, next_year_month_days)

	# print(date_1_days, date_2_days)
	# print(date_2_days - date_1_days)
	# print(sum(this_year_month_days))

	d1 = d1[1]
	d2 = d2[1]
	return ((((date_2_days - date_1_days) * 24) + d2[0] - d1[0]) * 60) + d2[1] - d1[1]



def parse_distance(d1, d2):
	dist = get_distance(date_1, date_2)

	minutes = dist % 60
	dist //= 60
	hours = dist % 24
	dist //= 24
	days = dist
	print(f"{days} days, {hours} hours, {minutes} minutes")
	
print(parse_distance(date_1, date_2))