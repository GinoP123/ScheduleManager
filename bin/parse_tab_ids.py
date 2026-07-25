#!/usr/bin/env python3

import sys
import re

tab_ids = []
for line in (x for x in sys.stdin.readlines() if x.strip()):
	tab_id = re.search('(?<=[:,\\[])[0-9]*(?=\\])', line).group(0)
	tab_ids.append(tab_id)
print('\n'.join(sorted(tab_ids)))
