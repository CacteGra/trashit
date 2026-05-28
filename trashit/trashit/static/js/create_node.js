document.addEventListener('DOMContentLoaded', function() {
  const addMenuBtn = document.getElementById('record');
  const createPanel = document.getElementById('create-mode-panel');
  const validateBtn = document.getElementById('validate-bin-btn');
  const cancelBtn = document.getElementById('cancel-create-btn');
  const typeSelect = document.getElementById('bin-type-select');

  let isCreateMode = false;
  let createMarker = null;

  // Safely retrieve Leaflet map instance
  const getMap = () => window.map;

  function getCsrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function enterCreateMode() {
    if (!map) return;

    isCreateMode = true;
    if (createMarker) map.removeLayer(createMarker);

    // Place draggable marker at current view center
    createMarker = L.marker(map.getCenter(), {
      draggable: true,
      icon: L.icon({
        iconUrl: '/static/leaflet/images/marker-icon.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34]
      })
    }).addTo(map);

    createPanel.classList.remove('d-none');
    addMenuBtn.classList.add('active-mode');
    addMenuBtn.title = 'Exit Create Mode';
  }

  function exitCreateMode() {
    isCreateMode = false;
    if (createMarker) {
      map.removeLayer(createMarker);
      createMarker = null;
    }
    createPanel.classList.add('d-none');
    addMenuBtn.classList.remove('active-mode');
    addMenuBtn.title = '';
    typeSelect.value = '';
  }

  // Toggle create mode on button click
  addMenuBtn.addEventListener('click', function(e) {
    e.preventDefault();
    if (!isCreateMode) enterCreateMode();
    else exitCreateMode();
  });

  cancelBtn.addEventListener('click', exitCreateMode);

  // Validate & send to Django
  validateBtn.addEventListener('click', function() {
    const map = getMap();
    if (!createMarker || !map) return;

    const selectedType = typeSelect.value;
    if (!selectedType) {
      alert('Please select a trash bin type before validating.');
      return;
    }

    const coords = createMarker.getLatLng();
    const payload = {
      lat: coords.lat,
      lng: coords.lng,
      type: selectedType
    };

    // 🔧 REPLACE WITH YOUR ACTUAL DJANGO URL NAME/PATH
    const endpoint = 'create-trash/';

    fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify(payload)
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (data.success) {
        alert('✅ Trash bin location validated successfully!');
        exitCreateMode();
        // Optional: Reload map markers or fetch updated data
        // location.reload();
      } else {
        alert('❌ Validation failed: ' + (data.error || 'Unknown error'));
      }
    })
    .catch(error => {
      console.error('Validation error:', error);
      alert('Network or server error. Please try again.');
    });
  });
});