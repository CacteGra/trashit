// Global variables needed across modules
let map;
let oldLatLng = null;
let userMarker = null;
let locFound = false;
let firstLoad = false;
let following = true;
let localEmail;
let href;
let notifInfo;

// Initialize Layers
let markersLayer = L.layerGroup();
let circlesLayer = L.layerGroup();
let polygonsLayer = L.layerGroup();

let selectedIcon = L.Icon.extend({
    options: {
        iconSize: [25, 41],
        shadowSize: [50, 64],
        iconAnchor: [13, 20],
        shadowAnchor: [14, 65],
        popupAnchor: [-3, -76]
    }
});

// Cached DOM elements
let trashList = document.querySelector('.trashList');
let reload = document.querySelector('.reload');
let scanResult = document.getElementById('scan-result');
let replaceCollection = document.getElementById('replaceCollection');
let requestLocalForm = document.getElementById('request-local-form');
let iconCache = new Map();

// --- Utility Functions ---

/**
 * Preloads icons to improve performance.
 * @param {string} iconUrl
 * @param {number[]} size
 * @returns {L.Icon}
 */
function createIcon(iconUrl, size) {
    if (iconCache.has(iconUrl)) {
        return iconCache.get(iconUrl);
    }
    const icon = L.icon({
        iconUrl: iconUrl,
        iconSize: size,
        iconAnchor: [size[0] / 2, size[1]],
        popupAnchor: [-3, -76]
    });
    iconCache.set(iconUrl, icon);
    return icon;
}

// --- Map Initialization & Setup ---

/**
 * Main Map Init Function (Called by {% leaflet_map "map" callback="mapInit" %})
 * @param {L.Map} mapInstance
 * @param {object} options
 */
function mapInit(mapInstance, options) {
    map = mapInstance;
    const browserLanguage = getBrowserLanguage();
    const languageOnly = browserLanguage.split('-')[0];

    const tileLayer = L.tileLayer(
        'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        {
            maxNativeZoom: 19,
            maxZoom: 25,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            headers: {
                'User-Agent': 'TrashIt/1.0 (https://trashit.click)',
                'Referer': window.location.origin
            }
        }
    );

    markersLayer.addTo(map);
    circlesLayer.addTo(map);
    polygonsLayer.addTo(map);

    // Remove default zoom control
    map.removeControl(map.zoomControl);
    const leafletControlContainers = document.querySelectorAll('.leaflet-control-container');
    leafletControlContainers.forEach(container => {
        container.style.display = 'none';
    });

    // Define icons
    const userIcon = L.icon({
        iconUrl: circleIconUrl,
        iconSize: [40, 40],
        shadowUrl: shadowUrl,
        shadowSize: [45, 45],
        shadowAnchor: [20, 20]
    });
    const defaultIcon = createIcon(defaultIconUrl, [25, 41]);

    // Attach listeners
    map.addLayer(tileLayer);
    map.on('locationfound', onLocationFound);
    map.on('locationerror', onLocationError);
    map.on('dragstart', function () {
        following = false;
    });
    
    // Zoom Controls
    document.getElementById('in').onclick = () => map.setZoom(map.getZoom() + 1);
    document.getElementById('out').onclick = () => map.setZoom(map.getZoom() - 1);
    document.getElementById('recenter').onclick = () => {
        following = true;
        if (oldLatLng) {
            map.setView(oldLatLng, 17);
        }
    };

    // Start location tracking
    if (window.navigator.geolocation) {
        map.locate({setView: true, maxZoom: 17});
    } else {
        console.error("Geolocation not supported by this browser.");
    }
}

// --- Location Handlers ---

/**
 * Event: Location Found
 * @param {GeolocationPosition} e
 */
function onLocationFound(e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;
    const newLatLng = e.latlng;

    if (userMarker === null) {
        userMarker = L.marker(e.latlng, { icon: L.icon({
            iconUrl: iconUrl,
            iconSize: [40, 40],
            shadowSize: [45, 45],
            shadowAnchor: [20, 20]
        }) }).addTo(map);
    } else {
        userMarker.setLatLng(e.latlng);
    }
    
    const checkLoc = oldLatLng;
    oldLatLng = newLatLng;

    if (!firstLoad || (JSON.stringify(Object.values(checkLoc)) !== JSON.stringify(Object.values(newLatLng)))) {
        // Show map controls and filter dropdown
        const mapInterface = document.querySelector('.leaflet-control-container.custom');
        if (mapInterface) mapInterface.style.display = 'block';
        const mapDropup = document.querySelector('.dropup-filter');
        if (mapDropup) mapDropup.style.display = 'block';

        // AJAX call to determine initial state (local/unauthorized)
        $.ajax({
            url: firstLoadUrl,
            data: { lat, lng, same_session: false, languageOnly: getBrowserLanguage().split('-')[0] },
            type: 'GET'
        }).done(function (response) {
            if (response.requestlocal) {
                if (document.getElementById('noData')) {
                    requestLocalForm.innerHTML = response.requestlocal;
                    $('#noData').modal('toggle');
                } else {
                    // Used for coordinate injection in other modules
                    window.requestCoords = document.getElementById("coordinates");
                    if (window.requestCoords) {
                        window.requestCoords.value = `SRID=4326;POINT (${lng} ${lat})`;
                    }
                }
            } else {
                if (document.getElementById('noData')) {
                    $('#noData').modal('hide');
                }
                localEmail = response.administration_email;
                
                // Populate filter dropdown
                const menu = document.querySelector('.filtering.dropdown-menu');
                menu.innerHTML = '';
                const select = document.querySelector('.form-select');
                select.innerHTML = "";
                
                // All filter button
                const liAll = document.createElement('li');
                const btnAll = document.createElement('button');
                btnAll.className = 'dropdown-item filter';
                btnAll.id = 'filter all';
                btnAll.name = '{% trans "All" %}';
                btnAll.textContent = '{% trans "All" %}';
                btnAll.onclick = function() { locationButtonClick(); };
                liAll.appendChild(btnAll);
                menu.appendChild(liAll);

                // Type filters
                for (const type of response.all_types) {
                    const li = document.createElement('li');
                    const btn = document.createElement('button');
                    btn.className = 'dropdown-item filter';
                    btn.id = `${type[0]}`;
                    btn.name = type[1];
                    btn.textContent = type[3];
                    // Use the filterTrash function from ui_handlers.js
                    btn.onclick = (e) => window.filterTrash(e); 
                    li.appendChild(btn);
                    menu.appendChild(li);
                    const option = document.createElement('option');
                    option.value = `${type[0]}`;
                    option.innerHTML = type[3];
                    select.appendChild(option);
                }

                // Render markers
                renderTrashMarkers(response.response);
            }
            firstLoad = true;
        });
    }

    if (following) {
        const currentZoom = map.getZoom();
        map.setView(oldLatLng, currentZoom);
    }
}

/**
 * Event: Location Error
 * @param {GeolocationPositionError} e
 */
function onLocationError(e) {
    if (!locFound) {
        locFound = true;
        map.locate({ setView: true, maxZoom: 17 });
    }
}

/**
 * Sets up continuous location checking.
 */
function startLocationPolling() {
    // Re-locate every 3s
    setInterval(() => {
        if (!locFound) {
            locFound = true;
            map.locate({ setView: true, maxZoom: 17 }).on('locationfound', onLocationFound);
        } else {
            map.locate().on('locationfound', onLocationFound);
        }
    }, 3000);
}

// --- Rendering Functions ---

/**
 * Renders trash markers and circles on the map.
 * @param {Array} data
 */
function renderTrashMarkers(data) {
    console.log(data);
    markersLayer.clearLayers();
    circlesLayer.clearLayers();
    
    // Update the HTML list view (using existing HTML from the data)
    const html = data.map(listItem => listItem.data_list.map(item => item.html).join('')).join('');
    trashList.innerHTML += html;

    data.forEach(item => {
        const latlng = L.latLng(item.lat, item.lng);
        const circle = L.circle(latlng, item.radius);
        circlesLayer.addLayer(circle);

        item.data_list.forEach(d => {
            if (d.reload) {
                reload.innerHTML = d.reload;
            }

            const latlng = L.latLng(d.lat, d.lng);
            const iconName = d.trash_icon || 'trash-icon';
            const iconUrl = `${iconFolderUrl}${iconName}.svg`;
            const trashIcon = new selectedIcon({ iconUrl });

            const marker = L.marker(latlng, {
                title: d.trash_type,
                alt: `${d.trash_id} ${d.trash_type}`,
                icon: trashIcon
            }).on('click', highlightTrash);

            markersLayer.addLayer(marker);
        });
    });
}

/**
 * Filters trash data based on type and rerenders map/list.
 * @param {Event} e
 */
window.filterTrash = function(e) {
    if (!oldLatLng) {
        console.error("Location not found.");
        return;
    }
    
    const lat = oldLatLng.lat;
    const lng = oldLatLng.lng;
    const typeId = e.target.id;

    markersLayer.clearLayers();
    circlesLayer.clearLayers();

    $.ajax({
        url: filterUrl,
        data: { lat, lng, typeId, languageOnly: getBrowserLanguage().split('-')[0] },
        type: 'GET'
    }).done(function (response) {
        const html = response.map(item => item.html).join('');
        trashList.innerHTML += html;
        renderTrashMarkers(response);
    });
}

/**
 * Handler for trash marker clicks (opens modal/reporting).
 * @param {Event} e
 */
function highlightTrash(e) {
    const id = e.target.options.alt;
    const modal = document.getElementById(`${id} modal`);
    const report = document.getElementById(`${id} report`);
    
    if (modal && report) {
        $(modal).modal('toggle');
        report.style.display = 'block';
    }
}