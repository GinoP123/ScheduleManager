#!/bin/bash

export PATH="/opt/homebrew/bin:$PATH"

profile="$2"
if [[ $profile != '0' && $profile != '1' ]]; then
	profile=0
fi

other_profile=$((1-$profile))

folder=$(dirname "$0")
before_file="/tmp/before.txt"
after_file="/tmp/after.txt"

chrome-cli list tabs | "$folder/parse_tab_ids.py" > "$before_file"
"$folder/change_chrome_profile.sh" "$2"

chrome-cli list tabs | chrome-cli list tabs | "$folder/parse_tab_ids.py" > "$after_file"
new_tab=$(diff "$before_file" "$after_file" | tail -n 1 | cut -d' '  -f2)

rm -f "$before_file"
rm -f "$after_file"

# chrome-cli close -t "$new_tab" > /dev/null
chrome-cli open "$1" -t "$new_tab"

