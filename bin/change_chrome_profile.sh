#!/bin/bash

if [[ "$1" == "1" ]]; then
	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --profile-directory="Profile 6" &> /dev/null
elif [[ "$1" == "2" ]]; then
	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --profile-directory="Profile 8" &> /dev/null
else
	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --profile-directory="Default" &> /dev/null
fi


