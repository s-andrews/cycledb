$( document ).ready(function() {
    update_routes()
})


function update_routes(){
    $.ajax(
        {
            url: "/cgi-bin/cycledb_backend.py",
            data: {
                action: "routes",
            },
            success: function(route_json) {
                show_routes(route_json)
            }
        });
}

function show_routes(routes){
    for (let i in routes) {
        let route = routes[i]

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
                                <li><strong>Goes via:</strong> ${route.places}</li>
                                <li><strong>Last ridden:</strong> ${route.dates[route.dates.length - 1]}</li>
                                <li><strong>Times ridden:</strong> ${route.dates.length}</li>
                            </ul>
                        </div>
                        <div class="col-md-7">
                            <div id="map${route._id}" class="map">
                            <a class="btn btn-dark btn-sm gpxdownload" href="/cgi-bin/cycledb_backend.py?action=gpx&route=${route._id}" role="button">Download GPX</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
        `)

    }
}