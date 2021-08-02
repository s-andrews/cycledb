$( document ).ready(function() {

    routes = []

    $(".filter_slider").slider({tooltip_split: 1})

    $("#filter_place").autoComplete({
      resolverSettings: {
        url: "cgi-bin/cycledb_backend.py"
      }
    })

    update_routes()
    $("#apply_filter").click(update_routes)

    $("#morebutton").click(more_routes)

    $("#sortby").change(sort_routes)
  })


function update_routes(){

  // Close the filter drawer if it's open
  $("#filterdrawer").drawer("hide")

  // Get the values from the filters
  let length_limits = $("#filter_length").val().split(",")
  let elevation_limits = $("#filter_elevation").val().split(",")


  let form_data = {
    "action": "routes",
    "min_len": length_limits[0],
    "max_len": length_limits[1],
    "min_ele": elevation_limits[0],
    "max_ele": elevation_limits[1]
  }

  if ($("#filter_place").val()) {
    form_data["via"] = $("#filter_place").val()
  }

  if ($("#filter_date").val()) {
    console.log("Fitlering by date")
    if ($("#filter_beforeafter").val() == "Before") {
      console.log("before")
      form_data["before"] = $("#filter_date").val()
    }
    else {
      console.log("after")
      form_data["after"] = $("#filter_date").val()
    }
  }

  console.log(form_data)

  $.ajax(
      {
          url: "/cgi-bin/cycledb_backend.py",
          data: form_data,
          success: function(route_json) {
              show_routes(route_json)
          }
      });
}

function show_routes(routes_json){

    // Save the results globally so we can sort and add 
    // more if we need.

    routes = routes_json
    sort_routes()
}

function more_routes() {
  let new_max = Math.min(route_position + 5, routes.length)

  for (;route_position < new_max;route_position++) {
    append_route(routes[route_position])
  }

  if (route_position == routes.length) {
    $("#more").hide()
  }
  else {
    $("#more").show()
  }
}

function sort_routes() {

  route_position = 0
  $("#routes").html("")
  $("#routes").append(`<h2>Found ${routes.length} routes`)

  switch($("#sortby").val()) {
    case "long":
      routes.sort(function(a,b){
        return b["distance"]-a["distance"]
      })
      break;
    case "short":
      routes.sort(function(a,b){
        return a["distance"]-b["distance"]
      })
      break;
    case "low":
      routes.sort(function(a,b){
        return a["elevation"]-b["elevation"]
      })
      break;
    case "high":
      routes.sort(function(a,b){
        return b["elevation"]-a["elevation"]
      })
      break;
    case "pop":
      routes.sort(function(a,b){
        return b["ridden"]-a["ridden"]
      })
      break;
    case "date":
      routes.sort(function(a,b){
        return a["dates"][a["ridden"]-1] <  b["dates"][a["ridden"]-1]
      })
      break;
      
      default:
      // code block
  } 

  more_routes()

}



function append_route(route) {
  $("#routes").append(`
  <div class="row">
  <div class="col-lg-12">
      <div class="card">
          <div class="card-body">
              <div class="row">
                  <div class="col-md-5">
                      <h3 class="card-title">${route.name}</h3>
                      <ul>
                          <li><strong>Distance:</strong> <span class="metric">${parseFloat(route.distance).toFixed(1)} km</span><span class="imperial">${(parseFloat(route.distance) * 0.62).toFixed(1)} miles</span></li>
                          <li><strong>Elevation:</strong> <span class="metric">${parseFloat(route.elevation).toFixed(1)} meters</span><span class="imperial">${(parseFloat(route.elevation) * 3.28).toFixed(1)} feet</span></li>
                          <li><strong>Goes via:</strong> ${route.places.join(", ")}</li>
                          <li><strong>Last ridden:</strong> ${route.dates_text[route.dates_text.length - 1]}</li>
                          <li><strong>Times ridden:</strong> ${route.dates.length}</li>
                          <li><strong>Strava route:</strong> <a href="https://strava.com/routes/${route.strava}">Route ${route.strava}</a></li>
                      </ul>
                  </div>
                  <div class="col-md-7">
                      <div id="map${route._id}" class="map">
                      <a class="btn btn-dark btn-sm gpxdownload" href="/cgi-bin/cycledb_backend.py?action=gpx&id=${route._id}" role="button">Download GPX</a>
                      </div>
                  </div>
              </div>
          </div>
      </div>
  </div>
</div>
  `)
  load_map(route._id, route.lat, route.lon)

}

function load_map(id, lat, lon) {

    let style = {
        'MultiLineString': new ol.style.Style({
          stroke: new ol.style.Stroke({
            color: '#a00',
            width: 4
          })
        })
      };

    let vector = new ol.layer.Vector({
        source: new ol.source.Vector({
          url: "/cgi-bin/cycledb_backend.py?action=gpx&id="+id,
          format: new ol.format.GPX()
        }),
        style: function(feature) {
          return style[feature.getGeometry().getType()];
        }
      });

    new ol.Map({
        target: "map"+id,
        layers: [
          new ol.layer.Tile({
            source: new ol.source.OSM()
          }),
          vector
        ],
        view: new ol.View({
          center: ol.proj.fromLonLat([lon, lat]),
          zoom: 10
        })
    })
}