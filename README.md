Burwell Cycle Club Ride Database
================================

This is the code behind the database of cycleroutes which can be found at [burwellcycleclub.uk](http://burwellcycleclub.uk)

It takes in a collection of GPX files from the rides, collates them to find duplicates and then uploads them into a mongodb database.

On the front end it then uses a JQuery based framework to allow querying and sorting by length, elevation etc.  The routes are displayed using the [OpenLayers](https://openlayers.org/) API.
