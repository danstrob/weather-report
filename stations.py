#!/usr/bin/env python3.7

import json
import pandas as pd
from math import asin, cos, sin, pi
from urllib.request import urlopen, URLError


def get_station_list(url):
    """
    Returns a pandas dataframe with a list of weather stations
    and their geographic coordinates as provided by the ZAMG website.
    """
    try:
        stat = pd.read_csv(url, encoding="ISO-8859-1", sep=";", decimal=",")
        stat["lat"] = stat["BREITE DEZI"]
        stat["long"] = stat["LÄNGE DEZI"]
        return stat

    except URLError as err:
        raise Exception(
            "Could not open URL to list of ZAMG weather stations: " + url
        ) from err


def get_current_location(ipinfo_url):
    """
    Fetch JSON with location information from ipinfo.io and
    return coordinates (tuple).
    """
    try:
        res = urlopen(ipinfo_url)
        loc_info = json.load(res)
    except URLError as err:
        raise Exception(f"Could not request your location from {ipinfo_url}.") from err

    if loc_info["country"] != "AT":
        raise Exception("This script only works with Austrian IP addresses.")

    loc_string = str.split(loc_info["loc"], ",")
    loc_info["lat_long"] = tuple([float(x) for x in loc_string])
    return loc_info["lat_long"]


def haversine(loc1, loc2):
    """
    Calculates approximate distance between two points (in Central Europe)
    based on their haversine distance
    (https://en.wikipedia.org/wiki/Haversine_formula).
    """
    lat1 = loc1[0] * pi / 180
    lat2 = loc2[0] * pi / 180
    long1 = loc1[1] * pi / 180
    long2 = loc2[1] * pi / 180

    h = (
        sin((lat2 - lat1) / 2) ** 2
        + cos(lat1) * cos(lat2) * sin((long2 - long1) / 2) ** 2
    ) ** 0.5
    return 2 * 6366 * asin(h)


def calculate_distance(station, location):
    return haversine((station.lat, station.long), location)


def find_closest_station():
    """
    Find name of closest weather station based on the current IP coordinates.
    Return abbreviated region and station as strings.
    """
    ipinfo_url = "http://ipinfo.io/json"
    stations_url = "https://www.zamg.ac.at/\
cms/de/dokumente/klima/dok_messnetze/\
zamg-stationsliste-als-csv"

    coordinates = get_current_location(ipinfo_url)
    station_list = get_station_list(stations_url)

    station_list["distance"] = station_list[["lat", "long"]].apply(
        lambda x: calculate_distance(x, coordinates), axis=1
    )
    closest_station = station_list["NAME"][station_list["distance"].idxmin()]
    region = station_list.loc[station_list["NAME"] == closest_station][
        "BUNDESLAND"
    ].iloc[0]

    return region, closest_station
