#!/usr/bin/env python3.7

import re
from difflib import get_close_matches
from subprocess import call
from sys import platform

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from gtts import gTTS
from plyer import notification

from stations import find_closest_station


def get_temp(region, closest_station):
    """
    Returns a tuple with a time stamp and an unformatted string
    with the temperature for the requested station looking like this: "25.0°"
    It uses BeautifulSoup to find the relevant information in the HTML.
    Unfortunately the names of the weather stations in "closest_station"
    do not always match the ones on the website perfectly.
    Therefore we have to try a bit of fuzzy matching using difflib.
    If this fails, we will calculate the average temperature for the region.
    """

    region_urls = {
        "BGL": "burgenland",
        "KNT": "kaernten",
        "NOE": "niederoesterreich",
        "OOE": "oberoesterreich",
        "SAL": "salzburg",
        "STMK": "steiermark",
        "TIR": "tirol",
        "VBG": "vorarlberg",
        "WIE": "wien",
    }

    url = (
        "https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/"
        + region_urls[region]
    )
    html = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(urlopen(html), "html.parser")
    time = soup.find(text=re.compile("Aktuelle Messwerte")).replace("\n", "")
    hour = [int(s) for s in time.split() if s.isdigit()][0]

    stations_html = soup.find_all("tr", {"class": re.compile("dynPageTableLine")})
    stations_web = []
    for s in stations_html:
        stations_web.append(s.find("a").string)
    stations_web_upper = [x.upper() for x in stations_web]
    station_names = get_close_matches(closest_station, stations_web_upper)

    if not station_names:
        temps = []
        for s in stations_html:
            t = s.find("td", {"class": "text_right wert selected"}).string
            temps.append(float(str.replace(t, "°", "")))
        average_temp = sum(temps) / len(temps)
        temp = "ca. " + str(average_temp) + "°"

        return hour, temp

    pos = stations_web_upper.index(station_names[0])
    temp = stations_html[pos].find("td", {"class": "text_right wert selected"}).string
    return hour, temp


def read_to_mp3(hour, temp, closest_station):
    """
    Text-to-speech function; saves an audio output of the current temperature
    to a temp file.
    """
    text = (
        "Um "
        + str(hour)
        + "Uhr wurden in "
        + closest_station.title()
        + temp
        + " gemessen."
    )
    tts = gTTS(text=text, lang="de")
    mp3_path = "/tmp/zamg.mp3"
    tts.save(mp3_path)
    return mp3_path


def main():
    region, closest_station = find_closest_station()
    hour, temp = get_temp(region, closest_station)
    mp3_path = read_to_mp3(hour, temp, closest_station)

    try:
        if platform == "linux":
            audio_exec = "mpv"
            call([audio_exec, mp3_path])
        elif platform == "darwin":
            audio_exec = "afplay"
            call([audio_exec, mp3_path])

    except FileNotFoundError:
        print(
            f"(Please install executable '{audio_exec}' to get "
            + "a text-to-speech output with the current temperature.)"
        )

    message = closest_station.title() + ": " + temp + "(um " + str(hour) + ":00h)"
    notification.notify(title="Current temperature:", message=message)

    print("-----------------------------------------------")
    print(message)
    print("-----------------------------------------------")


if __name__ == "__main__":
    main()
