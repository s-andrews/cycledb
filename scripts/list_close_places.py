#!/usr/bin/env python3
import sys
import xml.dom.minidom
from pathlib import Path

def main():
    places = read_places()
    place_hits = list_places_for_gpx(sys.argv[1], places)

    for place in sorted(place_hits):
        print(place)

def read_places():
    with open(Path(__file__).parent/"places_db.txt") as infile:
        infile.readline()

        places = []

        for line in infile:
            line = line.strip()
            sections = line.split("\t")
            places.append({
                "name": sections[0],
                "lon": float(sections[2]),
                "lat": float(sections[1])
            })
        
        return places


def list_places_for_gpx(file, places):
    with open(file) as gpxf:
        gpx_data = gpxf.read()

    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parseString(gpx_data)
    collection = DOMTree.documentElement

    points = collection.getElementsByTagName("trkpt")

    place_hits = set()

    for point in points:
        this_lat = float(point.getAttribute("lat"))
        this_lon = float(point.getAttribute("lon"))

        for place in places:
            if place["name"] in place_hits:
                continue

            if (abs(this_lat - place["lat"]) < 0.005) and (abs(this_lon - place["lon"]) < 0.005):
                place_hits.add(place["name"])                


    return place_hits

if __name__ == "__main__":
    main()