#!/bin/bash

original_name="$1"
new_name="$2"

profile_path="$HOME/Library/Application Support/Google/Chrome"

if [[ -d "$profile_path/$original_name" ]]; then
	mv "$profile_path/$original_name" "$profile_path/$new_name"
elif [[ ! -d "$profile_path/$new_name" ]]; then
	echo "ERROR: Profile Directory Not Found "
	exit 1
fi

rm -f "$profile_path/Local State"
cd "$profile_path/$new_name"
LC_ALL=C find . -type f -exec sed -i '' "s/$original_name/$new_name/g" {} +

