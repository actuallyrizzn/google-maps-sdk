"""
Basic usage examples for Google Maps Platform Python SDK
"""

from google_maps_sdk import GoogleMapsClient

# Replace with your actual API key
API_KEY = "YOUR_API_KEY"


def example_routes_api():
    """Example: Using Routes API"""
    client = GoogleMapsClient(api_key=API_KEY)
    
    origin = {
        "location": {
            "latLng": {
                "latitude": 37.419734,
                "longitude": -122.0827784
            }
        }
    }
    
    destination = {
        "location": {
            "latLng": {
                "latitude": 37.417670,
                "longitude": -122.079595
            }
        }
    }
    
    # Compute route with traffic-aware routing
    route = client.routes.compute_routes(
        origin=origin,
        destination=destination,
        routing_preference="TRAFFIC_AWARE",
        departure_time="now",
        compute_alternative_routes=True
    )
    
    print("Route computed successfully!")
    print(f"Routes found: {len(route.get('routes', []))}")
    
    client.close()


def example_directions_api():
    """Example: Using Directions API (Legacy)"""
    client = GoogleMapsClient(api_key=API_KEY)
    
    # Get directions
    result = client.directions.get_directions(
        origin="Toronto",
        destination="Montreal",
        mode="driving",
        departure_time="now",
        traffic_model="best_guess"
    )
    
    if result.get("status") == "OK":
        routes = result.get("routes", [])
        if routes:
            route = routes[0]
            legs = route.get("legs", [])
            if legs:
                leg = legs[0]
                print(f"Distance: {leg['distance']['text']}")
                print(f"Duration: {leg['duration']['text']}")
                if 'duration_in_traffic' in leg:
                    print(f"Duration in traffic: {leg['duration_in_traffic']['text']}")
    
    client.close()


def example_roads_api():
    """Example: Using Roads API"""
    client = GoogleMapsClient(api_key=API_KEY)
    
    # GPS path
    path = [
        (60.170880, 24.942795),
        (60.170879, 24.942796),
        (60.170877, 24.942796)
    ]
    
    # Snap to roads
    result = client.roads.snap_to_roads(path, interpolate=True)
    
    snapped_points = result.get("snappedPoints", [])
    print(f"Snapped {len(snapped_points)} points to roads")
    
    # Get speed limits
    if snapped_points:
        place_ids = [point["placeId"] for point in snapped_points if "placeId" in point]
        if place_ids:
            speed_limits = client.roads.speed_limits(place_ids=place_ids)
            print(f"Retrieved speed limits for {len(speed_limits.get('speedLimits', []))} segments")
    
    client.close()


def example_context_manager():
    """Example: Using context manager"""
    with GoogleMapsClient(api_key=API_KEY) as client:
        # All APIs available
        route = client.routes.compute_routes(
            origin={"location": {"latLng": {"latitude": 37.419734, "longitude": -122.0827784}}},
            destination={"location": {"latLng": {"latitude": 37.417670, "longitude": -122.079595}}}
        )
        print("Route computed using context manager")


def example_error_handling():
    """Example: Error handling"""
    from google_maps_sdk import (
        InvalidRequestError,
        PermissionDeniedError,
        QuotaExceededError,
        GoogleMapsAPIError,
    )
    
    client = GoogleMapsClient(api_key=API_KEY)
    
    try:
        route = client.routes.compute_routes(
            origin={"location": {"latLng": {"latitude": 37.419734, "longitude": -122.0827784}}},
            destination={"location": {"latLng": {"latitude": 37.417670, "longitude": -122.079595}}}
        )
    except InvalidRequestError as e:
        print(f"Invalid request: {e.message}")
    except PermissionDeniedError as e:
        print(f"Permission denied: {e.message}")
    except QuotaExceededError as e:
        print(f"Quota exceeded: {e.message}")
    except GoogleMapsAPIError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


if __name__ == "__main__":
    print("Google Maps Platform Python SDK Examples")
    print("=" * 50)
    
    # Uncomment to run examples
    # example_routes_api()
    # example_directions_api()
    # example_roads_api()
    # example_context_manager()
    # example_error_handling()
    
    print("\nNote: Replace API_KEY with your actual Google Maps Platform API key")

