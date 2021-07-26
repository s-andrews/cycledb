#!/usr/bin/env python3
import sys
import xml.dom.minidom
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
from math import cos, asin, sqrt, pi


def main(folder):
    # Make the database connections
    client = MongoClient()
    db = client.cycledb_database
    global routes
    routes = db.routes_collection

    global places
    places = read_places()

    files = Path(folder).glob("*gpx")

    for file in files:

        print(f"Processing {file}")
        year,month,day,strava,name = file.name.split("-",maxsplit=4)

        # Read the gpx
        with open(file) as gpxf:
            gpx_data = gpxf.read()
            gpx_id = get_gpx_id(strava, name, gpx_data)
            add_new_date(int(year),int(month),int(day),gpx_id)


def add_new_date(year,month,day,gpx_id):
    date = datetime(year,month,day)
    routes.update({"_id":gpx_id},{"$push": {"dates": date}})


def get_gpx_id(strava, name, gpx_data):
    # Before we create a new entry we'll try to match
    # this to an existing gpx

    # Find a match to the strava id
    existing_route = routes.find_one({"strava":strava})
    if existing_route is not None:
        print(f"Found existing route {existing_route['_id']}")
        return existing_route["_id"]

    # TODO: Find a match to the exact gpx data

    # TODO: Find a highly similar gpx route

    # No matches found, create a new entry
    lat, lon, distance, elevation = get_stats_for_gpx(gpx_data)

    gpx_entry = {
        "name": name,
        "strava": strava,
        "gpx": gpx_data,
        "lat": lat,
        "lon": lon,
        "distance": distance,
        "elevation": elevation,
        "dates": [],
        "places":list_places_for_gpx(gpx_data)
    }

    print("Created new route")

    return routes.insert_one(gpx_entry).inserted_id


def get_stats_for_gpx(gpx_data):
    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parseString(gpx_data)
    collection = DOMTree.documentElement

    points = collection.getElementsByTagName("trkpt")

    lat_max = 0
    lat_min = 0
    lon_max = 0
    lon_min = 0

    last_lat = 0
    last_lon = 0

    distance = 0

    # Our elevation calculation is pretty crude.  We're just
    # using the elevation markers in the GPS file, which isn't 
    # ideal but is the best we can do without additional external
    # information.
    elevation = 0

    last_elevation = 0

    for i,point in enumerate(points):
        this_lat = float(point.getAttribute("lat"))
        this_lon = float(point.getAttribute("lon"))
        this_elevation = float(point.getElementsByTagName("ele")[0].firstChild.data)


        if i==0:
            lat_max = this_lat
            lat_min = this_lat
            lon_max = this_lon
            lon_min = this_lon

        else:
            if this_lat > lat_max:
                lat_max = this_lat
            if this_lat < lat_min:
                lat_min = this_lat
            if this_lon > lon_max:
                lon_max = this_lon
            if this_lon < lon_min:
                lon_min = this_lon

            # Calculate the distance from the last
            # point to this one
            p = pi/180
            a = 0.5 - cos((this_lat-last_lat)*p)/2 + cos(last_lat*p) * cos(this_lat*p) * (1-cos((this_lon-last_lon)*p))/2
            distance += 12742 * asin(sqrt(a))

            
            # Add any elevation change
            if this_elevation > last_elevation:
                elevation += this_elevation - last_elevation


        last_lat = this_lat
        last_lon = this_lon
        last_elevation = this_elevation


    mid_lat = (lat_min+lat_max)/2
    mid_lon = (lon_min+lon_max)/2


    return(mid_lat,mid_lon,distance, elevation)


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


def list_places_for_gpx(gpx_data):

    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parseString(gpx_data)
    collection = DOMTree.documentElement

    points = collection.getElementsByTagName("trkpt")

    place_hits = []

    for point in points:
        this_lat = float(point.getAttribute("lat"))
        this_lon = float(point.getAttribute("lon"))

        for place in places:
            if place["name"] in place_hits:
                continue

            if (abs(this_lat - place["lat"]) < 0.01) and (abs(this_lon - place["lon"]) < 0.01):
                place_hits.append(place["name"])                


    return place_hits


if __name__ == "__main__":
    main(sys.argv[1])