#!/bin/bash

cd "$(dirname "$0")/.."

chrome_path=$(python3 -c "import settings; print(settings.CHROME_LOCATION)")
profile=$(python3 -c "import settings; profile_num=int(\"$2\") if \"$2\".isnumeric() else 0; print(settings.CHROME_PROFILES[profile_num])")

"$chrome_path" --args "$1" --profile-directory="$profile" &> /dev/null

