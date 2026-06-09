document.addEventListener('DOMContentLoaded', function() {
  const addMenuBtn = document.getElementById('record');
  const lockLocBtn = null;
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
    var popup = L.popup()
    .setContent("<b>Click to record trash location</b>");
    popup.options.closeOnClick = false;
    createMarker.bindPopup(popup).openPopup();
      createMarker.on('dragend', () => {
        createMarker.openPopup(); // ensure it remains open after move
      });
    addMenuBtn.classList.add('active-mode');
    addMenuBtn.title = 'Exit Create Mode';
    addMenuBtn.innerHTML = `<i class="bi bi-x-circle" style="font-size: 35px;"></i> Exit record trash`;
    popupWrapper = document.getElementsByClassName("leaflet-popup-content-wrapper")[0];
    popupWrapper.addEventListener('click', function(e) {
      e.preventDefault();
      lockLoc();
    });
  }

  function lockLoc() {
    createPanel.classList.remove('d-none');
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
    addMenuBtn.innerHTML = `<i class="bi bi-plus-circle" style="font-size: 35px;"></i> Record trash`;
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
    $.ajax({
        type: 'POST',
        url: createNodeUrl,
        data: payload,
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function (res) {
          if (data.success) {
            alert('✅ Trash bin location validated successfully!');
            exitCreateMode();
            // Optional: Reload map markers or fetch updated data
            // location.reload();
          }
        }
    });
  });
});