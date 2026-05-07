// --- Utility Functions ---

/**
 * Retrieves a specific cookie value.
 * @param {string} name
 * @returns {string | null}
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getBrowserLanguage() {
    if (navigator.languages && navigator.languages.length > 0) {
        return navigator.languages[0];
    } else if (navigator.language) {
        return navigator.language;
    } else if (navigator.userLanguage) {
        return navigator.userLanguage;
    } else {
        return 'en-US';
    }
}

// --- Garbage Collection ---

function garbageCollect() {
    if (!window.oldLatLng) return;
    const lat = window.oldLatLng.lat;
    const lng = window.oldLatLng.lng;
  
    $.get("{% url 'garbage_collection' %}", { lat, lng })
            .done(function (response) {
                $replaceCollection.innerHTML = response.map(r => r.html).join('');
                $('#collectionModal').modal('toggle');
            });
}

// --- Photo Modal Handlers (Camera/Reporting) ---

let stream = null;
let isStreaming = false;

function getMedia() {
    const video = document.getElementById(`${id}video`);
    const camera = document.getElementById(`camera ${id}`);
    
    if (!video || !camera) return;

    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        .then(s => {
            stream = s;
            video.srcObject = s;
            video.play();
            camera.style.display = 'none';
            isStreaming = true;
        })
        .catch(err => console.error('Error accessing camera:', err));
}

function stopMedia() {
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        stream = null;
        isStreaming = false;
    }
}

function clearPhoto() {
    const canvas = document.getElementById(`${id}canvas`);
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#AAA';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    document.getElementById(`${id}photo`).src = canvas.toDataURL('image/png');
}

function takePicture() {
    const video = document.getElementById(`${id}video`);
    const canvas = document.getElementById(`${id}canvas`);
    const photo = document.getElementById(`${id}photo`);
    const output = document.getElementById(`output ${id}`);
    const camera = document.getElementById(`camera ${id}`);

    if (video && canvas && photo) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        photo.src = canvas.toDataURL('image/png');
        camera.style.display = 'none';
        output.style.display = 'block';
        stopMedia();
    } else {
        clearPhoto();
    }
}

function retakePicture() {
    const camera = document.getElementById(`camera ${id}`);
    const output = document.getElementById(`output ${id}`);
    
    if (camera && output) {
        camera.style.display = 'block';
        output.style.display = 'none';
        clearPhoto();
        getMedia();
    }
}

function sendPicture() {
    const canvas = document.getElementById(`${id}canvas`);
    const modal = document.getElementById(`${id}photo-modal`);
    
    if (!canvas) return;

    const patch = "{% url 'report_trash' %}";
    const data = canvas.toDataURL('image/png');

    $.ajax({
        method: 'POST',
        url: patch,
        data: { imageBase64: data, id },
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function (res) {
            if (modal) modal.innerHTML = res.status;
        }
    });
}


// --- Main Event Handlers ---

/**
 * Initializes the photo modal camera stream and handlers.
 * @param {string} id
 */
window.initPhotoModal = function(id) {
    // Global scope used by helper functions (e.g., takePicture)
    window.id = id; 

    const modalContent = document.getElementById(`modal content ${id}`);
    const video = document.getElementById(`${id}video`);
    const canvas = document.getElementById(`${id}canvas`);
    const photo = document.getElementById(`${id}photo`);
    const camera = document.getElementById(`camera ${id}`);
    const output = document.getElementById(`output ${id}`);
    const startBtn = document.getElementById(`${id}startbutton`);
    const retakeBtn = document.getElementById(`${id}retake picture`);
    const reportBtn = document.getElementById(`${id}report trash`);
    const closeBtn = document.getElementById(`${id}close`);
    
    if (!startBtn || !video || !canvas) return;

    // Set up handlers
    startBtn.onclick = () => takePicture();
    retakeBtn.onclick = () => retakePicture();
    reportBtn.onclick = () => sendPicture();
    closeBtn.onclick = () => stopMedia();

    // Init
    getMedia();
}

/**
 * Handles the reporting/notification menu button.
 * @param {Event} event
 */
function handleReportMenuClick(event) {
    if (!window.localEmail) return;
    
    const targetButton = event.target.parentNode;
    
    if (targetButton.className.includes("report trash")) {
        href = `mailto:${window.localEmail}?subject={% trans "Trash diposal issue" %}&body={% trans "Hi, there is a trash disposal issue at this location." %} ${window.oldLatLng.lat}%2C%20${window.oldLatLng.lng}.`;
        notifInfo = "{% trans 'Write an email to notify of a diposal issue.' %}";
    } else if (targetButton.className.includes("reporting dump")) {
        href = `mailto:${window.localEmail}?subject={% trans "Unauthorized dump" %}&body={% trans "Hi, I found this unauthorized dumping at" %} ${window.oldLatLng.lat}%2C%20${window.oldLatLng.lng}.`;
        notifInfo = "{% trans 'Write an email to notify of an unauthorized dumping.' %}";
    }
    
    const notif = document.getElementById('dumping-notif');
    if (notif) {
        notif.href = href;
        notif.innerHTML = notifInfo;
    }
    $('#add-trash-modal').modal('toggle');
}

// --- Initialization Logic (Run on document ready) ---

$(document).ready(function() {
    // 1. Attach Map/UI Button Handlers
    document.getElementById('garbage-collection').onclick = garbageCollect;
    document.getElementById('scan-wrapper').onclick = scanWrapper;
    
    // 2. Event Delegation for Trash Marker Reporting
    document.addEventListener('click', (e) => {
        if (e.target.closest('.reporting') && e.target.closest('.report trash')) {
            const targetId = e.target.closest('.report trash').id.replace('report ', '');
            initPhotoModal(targetId);
        }
    });
    
    // 3. Attach Report Menu Handler
    document.getElementById('add-menu').onclick = handleReportMenuClick;
});