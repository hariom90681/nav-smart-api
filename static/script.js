let map, directionsService, directionsRenderer, transcriptionDiv;
let chatSocket;
let lastAssistantEl;

function initMap() {
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();

    const initialLocation = { lat: 22.5726, lng: 88.3638 }; // Kolkata
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 7,
        center: initialLocation,
    });
    directionsRenderer.setMap(map);
}

window.initMap = initMap;

document.addEventListener('DOMContentLoaded', () => {
  const waitForGoogle = setInterval(() => {
    if (window.google && google.maps) {
      clearInterval(waitForGoogle);
      initMap(); // Safe to call now
    }
  }, 100);
});

document.addEventListener('DOMContentLoaded', () => {
    transcriptionDiv = document.getElementById('transcription');
    setupChatSocket();
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    if (sendBtn) sendBtn.addEventListener('click', sendChatMessage);
    if (chatInput) chatInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendChatMessage(); });

    document.getElementById('micBtn').addEventListener('click', startVoiceRecognition);
    document.getElementById('itineraryBtn').addEventListener('click', () => {
        const message = getCleanMessage();
        fetchItinerary(message);
    });
});

function startVoiceRecognition() {
    transcriptionDiv.textContent = '🎙️ Listening...';

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();

    recognition.onresult = async (event) => {
        const spokenText = event.results[0][0].transcript;
        transcriptionDiv.textContent = `You said: "${spokenText}"`;
        fetchRoute(spokenText);
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            appendMessage('You', spokenText);
            lastAssistantEl = appendMessage('Assistant', '');
            chatSocket.send(spokenText);
        }
    };

    recognition.onerror = (event) => {
        transcriptionDiv.textContent = `Error: ${event.error}`;
    };
}

function getCleanMessage() {
    return transcriptionDiv.textContent.replace('You said: "', '').replace('"', '');
}

function setupChatSocket() {
    const wsUrl = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/ollama';
    chatSocket = new WebSocket(wsUrl);
    chatSocket.onopen = () => { appendMessage('System', 'Connected to chat'); };
    chatSocket.onerror = () => { appendMessage('System', 'Chat connection error'); };
    chatSocket.onclose = () => { setTimeout(setupChatSocket, 1500); };
    chatSocket.onmessage = (evt) => {
        if (!lastAssistantEl) { lastAssistantEl = appendMessage('Assistant', ''); }
        lastAssistantEl.textContent += evt.data;
    };
}

function appendMessage(role, text) {
    const container = document.getElementById('messages') || document.getElementById('chatContent');
    const p = document.createElement('p');
    p.className = role.toLowerCase();
    p.textContent = `${role}: ${text}`;
    container.appendChild(p);
    container.scrollTop = container.scrollHeight;
    return p;
}

function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const text = input ? input.value.trim() : '';
    if (!text) return;
    appendMessage('You', text);
    lastAssistantEl = appendMessage('Assistant', '');
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(text);
    } else {
        fetch('/chat/ollama', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        }).then(r => r.json()).then(data => {
            lastAssistantEl.textContent += (data.reply || data.error || '');
        }).catch(() => {
            lastAssistantEl.textContent += ' (failed to reach chat server)';
        });
    }
    if (input) input.value = '';
}

async function fetchRoute(message) {
    try {
        transcriptionDiv.textContent = "Fetching route...";

        const response = await fetch('/location/get-details-route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        if (!Array.isArray(data) || data.length === 0) {
            transcriptionDiv.textContent = "No route found or invalid response.";
            return;
        }

        drawRoutePolyline(data);

    } catch (error) {
        transcriptionDiv.textContent = `Route error: ${error.message}`;
    }
}

function drawRoutePolyline(points) {
    const path = points.map(([lat, lng]) => ({ lat, lng }));

    // Center the map
    if (path.length > 0) {
        map.setCenter(path[0]);
    }

    // Clear old route
    directionsRenderer.setMap(null);

    // Draw polyline
    new google.maps.Polyline({
        path: path,
        geodesic: true,
        strokeColor: "#007bff",
        strokeOpacity: 1.0,
        strokeWeight: 4,
        map: map
    });

    transcriptionDiv.textContent = "✅ Route plotted.";
}


async function fetchItinerary(message) {
    try {
        const response = await fetch('/location/get-itinerary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        if (data.itinerary && Array.isArray(data.itinerary)) {
            data.itinerary.forEach(day => {
                displayItinerary(data);
                addItineraryMarkers(data.itinerary);
            });
        } else {
            transcriptionDiv.textContent = 'Could not generate itinerary.';
        }
    } catch (error) {
        transcriptionDiv.textContent = `Itinerary error: ${error.message}`;
    }
}

function displayItinerary(data) {
    const itineraryList = document.getElementById('itineraryList');
    itineraryList.innerHTML = ''; // Clear previous

    if (data.itinerary) {
        data.itinerary.forEach(day => {
            const item = document.createElement('li');
            item.innerHTML = `<strong>${day.day} - ${day.location}</strong><br>${day.activities.join(', ')}`;
            itineraryList.appendChild(item);
        });

        transcriptionDiv.textContent = data.reply;
    } else {
        transcriptionDiv.textContent = 'Could not generate itinerary.';
    }
}

function addItineraryMarkers(itinerary) {
    const geocoder = new google.maps.Geocoder();

    itinerary.forEach(day => {
        geocoder.geocode({ address: day.location }, (results, status) => {
            if (status === 'OK') {
                new google.maps.Marker({
                    map: map,
                    position: results[0].geometry.location,
                    title: `${day.day}: ${day.location}`
                });
            }
        });
    });
}
