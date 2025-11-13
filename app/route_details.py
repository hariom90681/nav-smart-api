import requests
import polyline

def get_all_stop_points(start, stop, api_key):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": start,
        "destination": stop,
        "mode": "driving",
        "key": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "OK":
        print("Error:", data["status"])
        return []

    route = data["routes"][0]
    leg = route["legs"][0]

    print(f"From: {leg['start_address']}")
    print(f"To: {leg['end_address']}")
    print(f"Distance: {leg['distance']['text']}")
    print(f"Duration: {leg['duration']['text']}")
    print("Extracting all stop points...")

    poly_points = polyline.decode(route["overview_polyline"]["points"])

    for i, (lat, lng) in enumerate(poly_points):
        print(f"{i+1}. ({lat}, {lng})")

    return poly_points

api_key = "AIzaSyDDgJKSce1dwXMTZ886PDMqjaJrF9z1ErA"
points = get_all_stop_points("Kolkata,IN", "Delhi,IN", api_key)
