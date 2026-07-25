# Automatic Schedule Manager Compatible with Google Calendar

## Quickstart

1. Download the Client File from [GoogleDrive](https://drive.google.com/file/d/1iDPacNqcaTpMkE6K7dp0rpfvlEDfF_y9/view?usp=drive_link)
2. Run the Installer:
```
git clone https://github.com/GinoP123/ScheduleManager.git
cd ScheduleManager
./installer.sh
mv $HOME/Downloads/gcal_client_secret_file.json json_files
```
3. Check that the Google Calendar parsing works:
```
./get_gcal_data.py
```
