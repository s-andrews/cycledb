#!/usr/bin/env python3
import requests
import re
import sys

def main():

    known_towns = read_known_towns()

    # suffolk_towns = get_suffolk_towns()
    cambridgeshire_towns = get_cambridgeshire_towns()

    with open("places_db.txt","a") as outfile:

        for town in suffolk_towns:
            if town[1] in known_towns:
                continue

            position = get_lon_lat_for_place(town[0])
            if position is not None:
                print(f"{town[1]}\t{position[0]}\t{position[1]}",file=outfile, flush=True)

            else:
                print(f"Failed with: {town[1]}", file=sys.stderr)


def read_known_towns():
    names = set()

    with open("places_db.txt") as places:
        places.readline()
        for line in places:
            line = line.strip()
            
            if not line:
                continue

            town = line.split("\t")[0]
            names.add(town)
        
        return names


def get_suffolk_towns():
    suffolk_html = requests.get("https://en.wikipedia.org/wiki/List_of_places_in_Suffolk")

    towns = []

    for hit in re.finditer("href=\"(/wiki/[\w\s\.,-]+)\" title=\"([\w\s\.,-]+)\"",suffolk_html.text):
        towns.append(hit.groups())

    return towns


def get_lon_lat_for_place(url):

    place_html = requests.get("https://en.wikipedia.org"+url)

    place_html = place_html.text.replace("\n","")


    # Try a coordinate match first
    coord_hit = re.search("\"coordinates\":\[([\d\.]+),([\d\.]+)\]",place_html)

    if coord_hit is not None:
        return([float(x) for x in coord_hit.groups()])

    # Alternatively there's another pattern to try
    coord_hit = re.search("\"wgCoordinates\":\{\"lat\":([\d\.]+),\"lon\":([\d\.]+)\}",place_html)

    if coord_hit is not None:
        return([float(x) for x in coord_hit.groups()])

    return None

if __name__ == "__main__":
    main()