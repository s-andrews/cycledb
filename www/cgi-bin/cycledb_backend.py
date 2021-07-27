#!/usr/bin/env python3
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from pathlib import Path
import cgi
import cgitb
cgitb.enable()


def main():
    # Make the database connections
    client = MongoClient()
    db = client.cycledb_database
    global routes
    routes = db.routes_collection

    form = cgi.FieldStorage()

    # Test whether this is a simple autocomplete first
    if "q" in form:
        autocomplete(form["q"].value)
        return

    if not "action" in form:
        print("Content-type: text/plain; charset=utf-8\n\nNo action")
        return

    if form["action"].value == "gpx":
        get_gpx(form["id"].value)

    elif form["action"].value == "routes":
        get_routes(form)


def autocomplete(query):

    query = query.lower()
    placefile = Path(__file__).parent.parent / "placenames.json"

    with open(placefile) as jin:
        all_places = json.load(jin)

        print("Content-type: application/json\n")
        print(json.dumps([x for x in all_places if query in x.lower()]))

def get_routes(form):
    routes_data = []

    # The filter values come in in miles/ft and the database is
    # in km/m.  We'll handle this properly eventually...

    route_limits = {
        "distance": {"$gt": float(form["min_len"].value)*1.61,"$lt": float(form["max_len"].value)*1.61},
        "elevation": {"$gt": float(form["min_ele"].value)*0.30,"$lt": float(form["max_ele"].value)*0.30}
    }

    # Add a place if there is one
    if "via" in form:
        route_limits["places"] = form["via"].value

    # Filter by date of last ride
    if "after" in form:
        y,m,d = [int(x) for x in form["after"].value.split("-")]
        date = datetime(y,m,d)
        route_limits["dates"] = {"$gt": date}

    if "before" in form:
        y,m,d = [int(x) for x in form["before"].value.split("-")]
        date = datetime(y,m,d)
        route_limits["dates"] = {"$not": {"$gt": date}}



    route_list = routes.find(route_limits,{"gpx":0})

    for route in route_list:
        route["_id"] = str(route["_id"])
        route["dates_text"] = [x.strftime("%d %b %Y") for x in route["dates"]]
        route["dates"] = [str(x) for x in route["dates"]]
        route["ridden"] = len(route["dates"])
        routes_data.append(route)

    routes_data.sort(key=lambda x: x["dates"][-1], reverse=True)


    print("Content-type: application/json\n")
    print(json.dumps(routes_data))

def get_gpx(id):
    route = routes.find_one({"_id": ObjectId(id)})
    if route is None:
        raise Exception("No route for "+id)
    print("Content-Disposition:attachment;filename=route.gpx")
    print("Content-type: application/gpx+xml\n")
    print(route["gpx"])



if __name__ == "__main__":
    main()