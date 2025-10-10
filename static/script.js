let map, directionsService, directionsRenderer, transcriptionDiv;

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
    };

    recognition.onerror = (event) => {
        transcriptionDiv.textContent = `Error: ${event.error}`;
    };
}

function getCleanMessage() {
    return transcriptionDiv.textContent.replace('You said: "', '').replace('"', '');
}

async function fetchRoute(message) {
    try {
        const response = await fetch('/location/get-route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        displayRoute(data);
    } catch (error) {
        transcriptionDiv.textContent = `Route error: ${error.message}`;
    }
}

function displayRoute(data) {
    const start = data.start;
    const end = data.end;

    if (start.error || end.error) {
        let errorMessage = "Could not plot route. ";
        if (start.error) errorMessage += `Start location error: ${start.error}. `;
        if (end.error) errorMessage += `End location error: ${end.error}.`;
        alert(errorMessage);
        return;
    }

    const startLatLng = new google.maps.LatLng(start.latitude, start.longitude);
    const endLatLng = new google.maps.LatLng(end.latitude, end.longitude);

    directionsService.route({
        origin: startLatLng,
        destination: endLatLng,
        travelMode: google.maps.TravelMode.DRIVING,
    }, (response, status) => {
        if (status === 'OK') {
            directionsRenderer.setDirections(response);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
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
