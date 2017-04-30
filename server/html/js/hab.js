

// Icon to use for hab marker
var habMarkerIcon = L.icon({
  iconUrl: '/img/hab.png',
  iconSize: [40, 40],
});

// Icon to use for 'me' marker
var meMarkerIcon = L.icon({
  iconUrl: '/img/me.png',
  iconSize: [40, 40],
});

// Map
var mymap = L.map('mapid', {
  center: [53.287239, -6.215481],
  zoom: 18,
  }),
  realtime = L.realtime({
    url: 'https://hab.chrskly.com/api/telemetry',
    crossOrigin: true,
    type: 'json',
  }, {
    interval: 3 * 1000,
    pointToLayer: function (feature, latlng) {
      return L.marker(latlng, {
        'icon': L.icon({
            iconUrl: '/img/hab.png',
            iconSize: [40, 40],
        })
    });
  }
}).addTo(mymap);

//L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpandmbXliNDBjZWd2M2x6bDk3c2ZtOTkifQ._QA7i5Mpkd_m30IGElHziw', {
    attribution: '',
    id: 'mapbox.streets'
}).addTo(mymap);

// Poll API to fetch HAB location
realtime.on('update', function(e) {
    var coordPart = function(v, dirs) {
        return dirs.charAt(v >= 0 ? 0 : 1) +
            (Math.round(Math.abs(v) * 100) / 100).toString();
    },
    popupContent = function(fId) {
        var feature = e.features[fId],
            c = feature.geometry.coordinates;
        console.log('asdf ' + c);
        return 'Lat, Lng ' + coordPart(c[1], 'NS') + ', ' + coordPart(c[0], 'EW');

    },
    bindFeaturePopup = function(fId) {
        realtime.getLayer(fId).bindPopup(popupContent(fId));
    },
    updateFeaturePopup = function(fId) {
        realtime.getLayer(fId).getPopup().setContent(popupContent(fId));
    };

    //mymap.fitBounds(realtime.getBounds(), {maxZoom: 3});

    Object.keys(e.enter).forEach(bindFeaturePopup);
    Object.keys(e.update).forEach(updateFeaturePopup);

    // make a call to update our location
    mymap.locate();
});

// hab marker
//hab = L.marker([53.287239, -6.215481], {icon: habMarkerIcon}).addTo(mymap).bindPopup("<b>HAB</b>");

// marker for our location
me = L.marker([53.287239, -6.215581], {icon: meMarkerIcon}).addTo(mymap).bindPopup("<b>YOU</b>");

// Marker to show our location
function onLocationFound(e) {
  me.setLatLng(e.latlng);
  console.log("Updating 'me' location to " + e.latlng);
}

mymap.on('locationfound', onLocationFound);

