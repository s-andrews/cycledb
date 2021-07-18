#!/usr/bin/env python3
import requests
import re

def main():
    suffolk_towns = get_suffolk_towns()

    for town in suffolk_towns:
        position = get_lon_lat_for_place(town[0])
        if position is not None:
            print(f"Town: {town[1]} Lon={position[0]} Lat={position[1]}")

def get_suffolk_towns():
    suffolk_html = requests.get("https://en.wikipedia.org/wiki/List_of_places_in_Suffolk")

    towns = []

    for hit in re.finditer("href=\"(/wiki/.*?)\" title=\"(.*?)\"",suffolk_html.text):
        towns.append(hit.groups())

    return towns


def get_lon_lat_for_place(url):
    place_html = requests.get("https://en.wikipedia.org"+url)


    coord_hit = re.search("\"coordinates\":\[([\d\.]+),([\d\.]+)\]",place_html.text)
    # coord_hit = re.search("\"coordinates\"",place_html.text)

    if coord_hit is not None:
        return([float(x) for x in coord_hit.groups()])

    else:
        return None

if __name__ == "__main__":
    main()