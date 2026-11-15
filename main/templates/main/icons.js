// ----- crime marker icons (Leaflet version)
// Names are kept the same as the old Google Maps version, because
// each crime in the database stores the icon name (e.g. "GUN_ICON").

var G_DEFAULT_ICON = new L.Icon.Default();

function makeCrimeIcon(folder) {
    return L.icon({
        iconUrl:      '{{ MEDIA_URL }}images/icons/' + folder + '/image.png',
        shadowUrl:    '{{ MEDIA_URL }}images/icons/' + folder + '/shadow.png',
        iconSize:     [39, 39],
        shadowSize:   [59, 39],
        iconAnchor:   [20, 39],
        shadowAnchor: [20, 39],
        popupAnchor:  [0, -39]
    });
}

var REMPIT_ICON = makeCrimeIcon('rempit');
var GUN_ICON    = makeCrimeIcon('gun');
var SKULL_ICON  = makeCrimeIcon('skull');
var PARANG_ICON = makeCrimeIcon('parang');
var RAPE_ICON   = makeCrimeIcon('rape');