let map;
let service;
let autocomplete;
const tableContainer = document.getElementById('tableContainer');
let table;
let tbody;

let markers = [];
var destinos = [];
var negocios = [];
var distancias = [];

function initMap() {
    const Mochis = { lat: 25.7690852, lng: -108.9888047 };

    map = new google.maps.Map(document.getElementById('map'), {
        center: Mochis,
        zoom: 15
    });

    service = new google.maps.places.PlacesService(map);

    initAutoComplete();
}

function initAutoComplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete'),
        {
            componentRestrictions: { 'country': ['MX'] },
            fields: ['place_id', 'geometry', 'name', 'formatted_address']
        }
    );

    autocomplete.addListener('place_changed', () => {
        const place = autocomplete.getPlace();

        if (!place.geometry) {
            document.getElementById('autocomplete').placeholder = 'Ingrese una direccion';
            return;
        }

        map.setCenter(place.geometry.location);
        // Clear previous results and markers before adding new ones
        clearResults(); // <-- ADDED: Clear old results before new search
        createMarker(place, true); // <-- MODIFIED: Add marker for the searched location, true indicates it's the primary marker

        searchNearby(place.geometry.location);
    });
}


function executePlaceSearch(request) {
    return new Promise((resolve) => {
        service.nearbySearch(request, (results, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK || status === google.maps.places.PlacesServiceStatus.ZERO_RESULTS) {
                resolve(results || []);
            } else {
                console.error("API Search Error for keyword '", request.keyword, "': ", status);
                resolve([]);
            }
        });
    });
}

function deduplicatePlaces(placesArray) {
    const uniquePlaces = new Map();
    placesArray.forEach(place => {
        if (place && place.place_id && !uniquePlaces.has(place.place_id)) {
            uniquePlaces.set(place.place_id, place);
        }
    });
    return Array.from(uniquePlaces.values());
}

function searchNearby(location) {
    const radiusInputElement = document.getElementById('tb');
    let searchRadius = 300;

    if (radiusInputElement && radiusInputElement.value.trim() !== '') {
        const userInputRadius = parseInt(radiusInputElement.value, 10);
        if (!isNaN(userInputRadius) && userInputRadius > 0) {
            searchRadius = userInputRadius;
        } else {
            console.log("Valor de radio inválido, usando predeterminado de 300m.");
        }
    } else {
        console.log("Radio no especificado, usando predeterminado de 300m.");
    }
    console.log("Radio de búsqueda utilizado:", searchRadius, "metros");

    const foodKeyword = 'comida OR restaurante OR cafe OR panaderia OR "para llevar"';
    const storeKeyword = 'supermercado OR Walmart OR Oxxo OR "Super Ávila" OR Soriana OR abarrotes OR "tienda de conveniencia"';

    const foodRequest = {
        location: location,
        radius: searchRadius,
        keyword: foodKeyword
    };

    const storeRequest = {
        location: location,
        radius: searchRadius,
        keyword: storeKeyword
    };

    createTable();

    Promise.all([
        executePlaceSearch(foodRequest),
        executePlaceSearch(storeRequest)
    ])
    .then(([foodResults, storeResults]) => {
        console.log("Food results from API:", foodResults);
        console.log("Store results from API:", storeResults);

        const combinedResults = (foodResults || []).concat(storeResults || []);
        
        if (combinedResults.length === 0) {
            console.log("Ambas búsquedas no arrojaron resultados o tuvieron errores.");
            const row = tBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 2;
            cell.textContent = 'No se encontraron negocios con los criterios especificados.';
            cell.style.textAlign = 'center';
            return;
        }

        const uniqueResults = deduplicatePlaces(combinedResults);
        console.log("Resultados únicos combinados:", uniqueResults.length);

        const originForFiltering = map.getCenter();
        let placesFoundAndWithinRadius = 0;

        if (uniqueResults.length > 0) {
            uniqueResults.forEach(place => {
                if (place.geometry && place.geometry.location) {
                    const distanceToPlace = calculateDistance(
                        originForFiltering.lat(),
                        originForFiltering.lng(),
                        place.geometry.location.lat(),
                        place.geometry.location.lng()
                    );

                    if (distanceToPlace <= searchRadius) {
                        createMarker(place);
                        addResultToTable(place);
                        placesFoundAndWithinRadius++;
                    } else {
                         console.log("Lugar FUERA del radio (filtrado):", place.name, distanceToPlace.toFixed(0) + "m");
                    }
                }
            });
        }

        if (placesFoundAndWithinRadius === 0) {
            const row = tBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 2;
            cell.textContent = 'No se encontraron negocios dentro del radio especificado.';
            cell.style.textAlign = 'center';
        }
        console.log("Resultados finales mostrados (dentro del radio):", placesFoundAndWithinRadius);

    })
    .catch(error => {
        console.error("Error crítico al procesar búsquedas combinadas:", error);
        const row = tBody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 2;
        cell.textContent = 'Ocurrió un error inesperado al realizar la búsqueda.';
        cell.style.textAlign = 'center';
    });
}

function createMarker(place, isPrimary = false) {
    if (!place.geometry || !place.geometry.location) {
        console.log("Cannot create marker, place has no geometry:", place);
        return;
    }
    const marker = new google.maps.Marker({
        map: map,
        position: place.geometry.location,
        title: place.name,
        icon: isPrimary ? {
            url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
        } : null
    });

    markers.push(marker);

    const infowindow = new google.maps.InfoWindow();
    google.maps.event.addListener(marker, 'click', () => {
        service.getDetails({
            placeId: place.place_id,
            fields: ['name', 'formatted_address', 'rating', 'formatted_phone_number', 'website', 'opening_hours']
        }, (placeDetails, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && placeDetails) {
                let content = `<h3>${placeDetails.name || 'N/A'}</h3>`;
                content += `<p><strong>Dirección:</strong> ${placeDetails.formatted_address || 'N/A'}</p>`;
                if (placeDetails.rating) {
                    content += `<p><strong>Rating:</strong> ${placeDetails.rating} (${placeDetails.user_ratings_total || 0} reviews)</p>`;
                } else {
                    content += `<p><strong>Rating:</strong> N/A</p>`;
                }
                content += `<p><strong>Teléfono:</strong> ${placeDetails.formatted_phone_number || 'N/A'}</p>`;
                if (placeDetails.website) {
                    content += `<p><strong>Website:</strong> <a href="${placeDetails.website}" target="_blank">${placeDetails.website}</a></p>`;
                }
                if (placeDetails.opening_hours) {
                    content += `<p><strong>Horario:</strong> ${placeDetails.opening_hours.isOpen() ? 'Abierto ahora' : 'Cerrado ahora'}</p>`;
                    content += "<ul>";
                    placeDetails.opening_hours.weekday_text.forEach(day => {
                        content += `<li>${day}</li>`;
                    });
                    content += "</ul>";
                }
                infowindow.setContent(content);
                infowindow.open(map, marker);
            } else {
                infowindow.setContent(`<h3>${place.name || 'N/A'}</h3><p>No se pudieron obtener más detalles.</p>`);
                infowindow.open(map, marker);
                console.log('Error al obtener detalles del lugar:', status);
            }
        });
    });
}

function createTable() {
    while (tableContainer.firstChild) {
        tableContainer.removeChild(tableContainer.firstChild);
    }

    table = document.createElement('table');
    const tHead = table.createTHead();
    const headerRow = tHead.insertRow();
    const nameHeader = document.createElement('th');
    nameHeader.textContent = 'Negocio';
    const distanceHeader = document.createElement('th');
    distanceHeader.textContent = 'Distancia (aprox.)';
    headerRow.appendChild(nameHeader);
    headerRow.appendChild(distanceHeader);
    tBody = table.createTBody();
    tableContainer.appendChild(table);
}

function addResultToTable(place) {
    if (!tBody) {
        createTable();
    }
    const origin = map.getCenter();
    const destination = place.geometry.location;
    const distance = calculateDistance(origin.lat(), origin.lng(), destination.lat(), destination.lng());

    const row = tBody.insertRow();
    const nameCell = row.insertCell();
    nameCell.textContent = place.name;
    const distanceCell = row.insertCell();
    distanceCell.textContent = `${distance.toFixed(2)} Metros`;
}

function clearResults() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];

    if (tableContainer.firstChild) {
        tableContainer.removeChild(tableContainer.firstChild);
        table = null;
        tBody = null;
    }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radio de la Tierra en km
    const toRad = angle => angle * (Math.PI / 180);
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat / 2) ** 2 +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c * 1000; // Distancia en metros
}