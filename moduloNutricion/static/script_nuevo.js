let map;
let service; // <-- Will be our PlacesService instance
let autocomplete;
const tableContainer = document.getElementById('tableContainer');
let table;
let tbody;

// Array to hold markers for easy clearing
let markers = [];

// Array de Coordenadas de los negocios (currently unused, but kept from original)
var destinos = [];
// Array con los nombres de los negocios (currently unused)
var negocios = [];
// Array con las distancias entre el origen y el negocio (currently unused)
var distancias = [];

function initMap() {
    const Mochis = { lat: 25.7690852, lng: -108.9888047 };

    map = new google.maps.Map(document.getElementById('map'), {
        center: Mochis,
        zoom: 15
    });

    // Initialize the PlacesService
    service = new google.maps.places.PlacesService(map); // <-- MODIFIED: Initialize service

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

function searchNearby(location) {
    console.log("Entro a buscar negocios cercanos");
    // Using nearbySearch which is standard.
    // You can use types: ['restaurant', 'cafe', 'bakery', 'meal_takeaway'] for more specific categories
    // or keyword for a broader search.
    const request = {
        location: location,
        radius: 500, // MODIFIED: Increased radius to 1.5km for more results
        keyword: 'comida OR restaurante OR cafe OR panaderia OR para llevar' // MODIFIED: Using keyword for a broader search in Spanish
        // Alternatively, for more specific types:
        // types: ['restaurant', 'cafe', 'bakery', 'meal_takeaway', 'food']
    };

    service.nearbySearch(request, (results, status) => { // MODIFIED: Using service.nearbySearch
        console.log("nearbySearch results:", results, "status:", status);
        if (status === google.maps.places.PlacesServiceStatus.OK && results) {
            // clearResults(); // Moved to before createMarker for the primary location
            createTable();
            console.log("buscando....");
            results.forEach(place => {
                createMarker(place); // Create marker for each nearby place
                addResultToTable(place);
                console.log("lugar", place);
            });
            console.log("resultados", results);
        } else {
            console.log('Error en la busqueda de lugares cercanos:', status);
            // Optional: If no results, clear table or show a message
            if (!results || results.length === 0) {
                clearResults(); // Clear table if it was created
                createTable(); // Create empty table header
                const row = tBody.insertRow();
                const cell = row.insertCell();
                cell.colSpan = 2; // Span across both columns
                cell.textContent = 'No se encontraron negocios cercanos con los criterios especificados.';
                cell.style.textAlign = 'center';
            }
        }
    });
}

function createMarker(place, isPrimary = false) { // Added isPrimary flag
    if (!place.geometry || !place.geometry.location) {
        console.log("Cannot create marker, place has no geometry:", place);
        return;
    }
    const marker = new google.maps.Marker({
        map: map,
        position: place.geometry.location,
        title: place.name,
        icon: isPrimary ? { // Optional: Different icon/color for primary marker
            url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
        } : null
    });

    markers.push(marker); // MODIFIED: Add marker to array for clearing

    const infowindow = new google.maps.InfoWindow();
    google.maps.event.addListener(marker, 'click', () => {
        // Request details for the infowindow
        // MODIFIED: Using the global 'service' and requesting all necessary fields
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
                // Fallback if getDetails fails or placeDetails is null
                infowindow.setContent(`<h3>${place.name || 'N/A'}</h3><p>No se pudieron obtener más detalles.</p>`);
                infowindow.open(map, marker);
                console.log('Error al obtener detalles del lugar:', status);
            }
        });
    });
}

function createTable() {
    // Clear existing table content first if any
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
    if (!tBody) { // Ensure tbody exists
        createTable();
    }
    const origin = map.getCenter(); // Usamos el centro del mapa (ubicación buscada) como origen
    const destination = place.geometry.location;
    const distance = calculateDistance(origin.lat(), origin.lng(), destination.lat(), destination.lng());

    const row = tBody.insertRow();
    const nameCell = row.insertCell();
    nameCell.textContent = place.name;
    const distanceCell = row.insertCell();
    distanceCell.textContent = `${distance.toFixed(2)} Metros`;
}

function clearResults() {
    // Eliminar marcadores existentes
    markers.forEach(marker => marker.setMap(null));
    markers = []; // Limpiar el array de marcadores

    // Limpiar la tabla de resultados
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

// Ensure initMap is called after the Google Maps API script has loaded
// The "callback=initMap" in your script tag handles this.