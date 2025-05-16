var autocomplete;
//Array de Coordenadas de los negocios
var destinos = [];

//Array con los nombres de los negocios
var negocios = [];

//Array con las distancias entre el origen y el negocio
var distancias = [];

var origin;
var destination;
var map; // Declaramos la variable map aquí para que sea accesible globalmente dentro de este scope
var table = document.createElement('table');
var tBody = table.createTBody();
var tHeader = table.createTHead();
let th = document.createElement('th');
let th2 = document.createElement('th');
th2.innerText = "Distancia";

th.innerText = "Negocios";
tHeader.appendChild(th);
tHeader.appendChild(th2);

function iniciarMap() {
    var coord = { lat: 25.7690852, lng: -108.9888047 };

    var styles = [
        { featureType: "all", elementType: "labels", stylers: [{ visibility: "off" }] },
        { featureType: "road", elementType: "all", stylers: [{ visibility: "on" }] },
        { featureType: "poi", elementType: "all", stylers: [{ visibility: "off" }] },
        { featureType: "transit", elementType: "all", stylers: [{ visibility: "off" }] },
        { featureType: "water", elementType: "all", stylers: [{ visibility: "on" }, { color: "#46bcec" }] },
        { featureType: "landscape", elementType: "all", stylers: [{ visibility: "on" }, { color: "#f2f2f2" }] }
    ];

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 18,
        center: coord,
        styles: styles
    });

    var marker = new google.maps.Marker({
        position: coord,
        map: map,
        title: "Mi Ubicación",
        // Para un icono predeterminado con un color diferente, puedes usar símbolos:
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: "blue",
            fillOpacity: 0.8,
            strokeWeight: 1,
            strokeColor: "black",
        }
    });

    var service = new google.maps.places.PlacesService(map);

    //Peticion a la API
    var request = {
        location: coord,
        radius: 1000,
        type: ['restaurant', 'cafe', 'bakery', 'meal_takeaway'],
        keyword: 'food'
    };

    service.nearbySearch(request, function (results, status) {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                createMarker(results[i]);
            }
        }
    });

    function createMarker(place) {
        var marker = new google.maps.Marker({
            position: place.geometry.location,
            map: map,
            title: place.name
        });

        service.getDetails({ placeId: place.place_id }, function (details, status) {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                var infowindow = new google.maps.InfoWindow({
                    content: '<h3>' + details.name + '</h3>' +
                        '<p>' + details.formatted_address + '</p>' +
                        '<p>Rating: ' + (details.rating || 'N/A') + '</p>' +
                        '<p>Telefono: ' + (details.formatted_phone_number || 'N/A') + '</p>'
                });

                marker.addListener('click', function () {
                    infowindow.open(map, marker);
                });
            }
        });
    }
}

function initAutoComplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete'),
        {
            componentRestrictions:
            { 'country': ['MX'] },
            fields: ['place_id', 'geometry', 'name', 'formatted_address']
        }
    );

    autocomplete.addListener('place_changed', function () {
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            document.getElementById('autocomplete').placeholder
                = 'Ingrese una direccion';
            return;
        }

        document.getElementById('details').innerHTML = place.formatted_address;
        const lat = place.geometry.location.lat();
        const lng = place.geometry.location.lng();
        iniciarMap2(lat, lng);
        console.log(lat);
        console.log(lng);
    });
}

function iniciarMap2(latitud, longitud) {
    var coord = { lat: latitud, lng: longitud };
    var styles = [
        { featureType: "all", elementType: "labels", stylers: [{ visibility: "off" }] },
        { featureType: "road", elementType: "all", stylers: [{ visibility: "on" }] },
        { featureType: "poi", elementType: "all", stylers: [{ visibility: "off" }] },
        { featureType: "transit", elementType: "all", stylers: [{ visibility: "off" }] },
        { featureType: "water", elementType: "all", stylers: [{ visibility: "on" }, { color: "#46bcec" }] },
        { featureType: "landscape", elementType: "all", stylers: [{ visibility: "on" }, { color: "#f2f2f2" }] }
    ];
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 18,
        center: coord,
        styles: styles
    });


    //Creamos Marker de la ubicación actual de una persona
    var marker = new google.maps.Marker({
        position: coord,
        map: map,
        title: "Mi Ubicación",
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: "red",
            fillOpacity: 0.8,
            strokeWeight: 1,
            strokeColor: "black",
        }
    });

    var service = new google.maps.places.PlacesService(map);

    //Peticion a la API
    var request = {
        location: coord,
        radius: 100,
        type: ['restaurant', 'cafe', 'bakery', 'meal_takeaway'],
        keyword: 'food'
    };

    tBody.innerHTML = '';
    service.nearbySearch(request, function (results, status) {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                createMarker(results[i], latitud, longitud); // Pasamos latitud y longitud a createMarker
            }
        }
    });

    function createMarker(place, origenLat, origenLng) {
        var marker = new google.maps.Marker({
            position: place.geometry.location,
            map: map,
            title: place.name
        });
        negocios = [];
        service.getDetails({ placeId: place.place_id }, function (details, status) {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                negocios.push(details.name);
                let row = tBody.insertRow();
                let cell = row.insertCell(0);
                cell.textContent = details.name;

                var origin = { lat: origenLat, lng: origenLng };
                var destination = { lat: place.geometry.location.lat(), lng: place.geometry.location.lng() };
                let distancia = calcularDistancia(origin.lat, origin.lng, destination.lat, destination.lng);
                let cell2 = row.insertCell(1);
                cell2.textContent = distancia.toFixed(2) + " Metros";
                tBody.appendChild(row);

                var infowindow = new google.maps.InfoWindow({
                    content: '<h3>' + details.name + '</h3>' +
                        '<p>' + details.formatted_address + '</p>' +
                        '<p>Rating: ' + (details.rating || 'N/A') + '</p>' +
                        '<p>Telefono: ' + (details.formatted_phone_number || 'N/A') + '</p>'
                });
                console.log(negocios);
                marker.addListener('click', function () {
                    infowindow.open(map, marker);
                });
            }
        });
        let tableContainer = document.getElementById('tableContainer');
        tableContainer.appendChild(table);
    }
}

function calcularDistancia(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const toRad = angle => angle * (Math.PI / 180);

    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);

    const a = Math.sin(dLat / 2) ** 2 +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    const distancia = R * c * 1000; //Para obtenerla en metros

    return distancia;
}

// La función centerMapOnPlace ya no es necesaria en este flujo,
// ya que la centrado del mapa y la búsqueda se realizan en iniciarMap2
// function centerMapOnPlace(lat, lng) { ... }

// Inicializar el autocompletado al cargar la página
function initMap() { // Renombramos initMap para evitar confusiones con iniciarMap
    iniciarMap();
    initAutoComplete();
}