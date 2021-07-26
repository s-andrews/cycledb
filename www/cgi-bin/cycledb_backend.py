#!/usr/bin/env python3
import json
from pymongo import MongoClient
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

    if not "action" in form:
        print("Content-type: text/plain; charset=utf-8\n\nNo action")
        return

    if form["action"].value == "gpx":
        get_gpx(form["id"].value)

    elif form["action"].value == "routes":
        get_routes(form)


def get_routes(form):
    routes_data = []
    route_list = routes.find()

    for route in route_list:
        route.pop("gpx") # Don't send gpx back with the original request
        route["_id"] = str(route["_id"])
        route["dates"] = [str(x) for x in route["dates"]]
        routes_data.append(route)

        if len(routes_data) == 10:
            break

    print("Content-type: application/json\n")
    print(json.dumps(routes_data))

def get_gpx(id):
    pass


if __name__ == "__main__":
    main()