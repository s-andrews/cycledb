#!/usr/bin/env python3
import sys
import xml.dom.minidom
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
from math import cos, asin, sqrt, pi
import json


def main(folder):
    # Make the database connections
    client = MongoClient()
    db = client.cycledb_database
    global routes
    routes = db.routes_collection

    # Be careful enabling this!
    routes.delete_many({})

    global places
    places = read_places()

    files = Path(folder).glob("*gpx")

    for file in files:

        print(f"Processing {file}")
        year,month,day,strava,name = file.name.split("-",maxsplit=4)

        # Take the extension off the end
        name = name.replace(".gpx","")

        # Remove the club name from the start
        if name.lower().startswith("bcc") or name.lower().startswith("bbc"):
            name = name[4:]

        # Read the gpx
        with open(file) as gpxf:
            gpx_data = gpxf.read()
            gpx_id = get_gpx_id(strava, name, gpx_data)
            add_new_date(int(year),int(month),int(day),gpx_id)

    collate_place_names()

def collate_place_names():
    # Collate place names
    all_place_names = set()

    place_results = routes.find({},{"places":1})

    for places in place_results:
        for place in places["places"]:
            all_place_names.add(place)

    all_place_names = list(all_place_names)
    all_place_names.sort()

    suggestfile = Path(__file__).parent.parent / "www/placenames.json"
    with open(suggestfile,"w") as json_out:
        print(json.dumps(all_place_names),file=json_out)


def add_new_date(year,month,day,gpx_id):
    date = datetime(year,month,day)
    routes.update_one({"_id":gpx_id},{"$push": {"dates": date}})


def get_gpx_id(strava, name, gpx_data):
    # Before we create a new entry we'll try to match
    # this to an existing gpx

    # Find a match to the strava id
    existing_route = routes.find_one({"strava":strava})
    if existing_route is not None:
        print(f"Found existing route {existing_route['_id']}")
        return existing_route["_id"]


    # We'll now get the details for the GPX
    places = list_places_for_gpx(gpx_data)
    lat, lon, distance, elevation = get_stats_for_gpx(gpx_data)

    # We'll still try to find an existing route match by looking
    # for an existing route which has the same list of places in 
    # the same order, and a total distance within 1 mile of the
    # existing route.

    existing_routes = routes.find({"places": places},{"_id":1, "distance":1})
    for route in existing_routes:
        if (abs(distance-route["distance"]) <= 1):
            # Where we have a similar route we'll always keep the
            # newer version of the gpx in case problems with the
            # route have been fixed.
            routes.update_one({"_id":route["_id"]},{"$set": {"gpx": gpx_data}})
            print(f"Found similar route {route['_id']}")
            return route["_id"]


    # No matches found, create a new entry

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
                "name": sections[0].split(",")[0],
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