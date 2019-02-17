# weather-report
This script fetches information on the current temperature in your region from the website of the Austrian Central Institution for Meteorology ([ZAMG](https://www.zamg.ac.at/)). It tries to find the closest weather station to you based on your IP (only works in Austria).

The script uses [plyer](https://github.com/kivy/plyer) to output the temperature as a notification. If you're on Linux, it tries to use `mpv` to play a text-to-speech audio generated by [gTTS](https://github.com/pndurette/gTTS) (tested on Arch Linux).

## Requirements
* Python 3.7

* beautifulsoup4
* gTTS
* Pandas
* plyer
