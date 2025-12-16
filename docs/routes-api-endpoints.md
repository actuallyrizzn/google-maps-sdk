# Routes API Endpoints

## Overview

The Routes API is Google's modern routing service that provides advanced routing capabilities including traffic-aware routing, route optimization, and detailed route information.

**Base URL**: `https://routes.googleapis.com`

**Discovery Document**: `https://routes.googleapis.com/$discovery/rest?version=v2`

**Status**: Active (Recommended - Use this instead of Directions API for new projects)

## Endpoints

### 1. Compute Routes

Calculates a route between an origin and destination, returning detailed route information including optional alternate routes.

**Endpoint**: `POST /directions/v2:computeRoutes`

**Full URL**: `https://routes.googleapis.com/directions/v2:computeRoutes`

**HTTP Method**: `POST`

**Content-Type**: `application/json`

#### Request Body

```json
{
  "origin": {
    "location": {
      "latLng": {
        "latitude": 37.419734,
        "longitude": -122.0827784
      }
    }
  },
  "destination": {
    "location": {
      "latLng": {
        "latitude": 37.417670,
        "longitude": -122.079595
      }
    }
  },
  "travelMode": "DRIVE",
  "routingPreference": "TRAFFIC_AWARE",
  "computeAlternativeRoutes": true,
  "routeModifiers": {
    "avoidTolls": false,
    "avoidHighways": false,
    "avoidFerries": false
  },
  "languageCode": "en-US",
  "units": "IMPERIAL"
}
```

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | Waypoint | Yes | Origin location (lat/lng, place ID, or address) |
| `destination` | Waypoint | Yes | Destination location |
| `intermediates` | Waypoint[] | No | Intermediate waypoints |
| `travelMode` | TravelMode | No | DRIVE, WALK, BICYCLE, TRANSIT (default: DRIVE) |
| `routingPreference` | RoutingPreference | No | TRAFFIC_AWARE, TRAFFIC_AWARE_OPTIMAL, ROUTE_PREFERENCE_UNSPECIFIED |
| `polylineQuality` | PolylineQuality | No | HIGH_QUALITY, OVERVIEW |
| `polylineEncoding` | PolylineEncoding | No | ENCODED_POLYLINE, GEO_JSON_LINESTRING |
| `departureTime` | Timestamp | No | Departure time for traffic calculations |
| `computeAlternativeRoutes` | boolean | No | Return alternative routes |
| `routeModifiers` | RouteModifiers | No | Avoid tolls, highways, ferries |
| `languageCode` | string | No | Language for response (e.g., "en-US") |
| `units` | Units | No | IMPERIAL or METRIC |
| `optimizeWaypointOrder` | boolean | No | Optimize waypoint order |
| `requestedReferenceRoutes` | ReferenceRoute[] | No | Requested reference routes |
| `extraComputations` | ExtraComputation[] | No | Additional computations (TOLLS, FUEL_CONSUMPTION, etc.) |

#### Response

Returns a `ComputeRoutesResponse` object containing:
- `routes[]`: Array of Route objects
- `fallbackInfo`: Information about fallback routing
- `geocodingResults`: Geocoding results for waypoints

#### Example Request

```bash
curl -X POST \
  'https://routes.googleapis.com/directions/v2:computeRoutes?key=YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -H 'X-Goog-FieldMask: routes.duration,routes.distanceMeters,routes.polyline' \
  -d '{
    "origin": {
      "location": {
        "latLng": {
          "latitude": 37.419734,
          "longitude": -122.0827784
        }
      }
    },
    "destination": {
      "location": {
        "latLng": {
          "latitude": 37.417670,
          "longitude": -122.079595
        }
      }
    },
    "travelMode": "DRIVE",
    "routingPreference": "TRAFFIC_AWARE"
  }'
```

---

### 2. Compute Route Matrix

Computes travel times and distances for a matrix of origin and destination pairs, accounting for traffic conditions.

**Endpoint**: `POST /distanceMatrix/v2:computeRouteMatrix`

**Full URL**: `https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix`

**HTTP Method**: `POST`

**Content-Type**: `application/json`

#### Request Body

```json
{
  "origins": [
    {
      "location": {
        "latLng": {
          "latitude": 37.419734,
          "longitude": -122.0827784
        }
      }
    }
  ],
  "destinations": [
    {
      "location": {
        "latLng": {
          "latitude": 37.417670,
          "longitude": -122.079595
        }
      }
    }
  ],
  "travelMode": "DRIVE",
  "routingPreference": "TRAFFIC_AWARE"
}
```

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origins` | Waypoint[] | Yes | Array of origin locations |
| `destinations` | Waypoint[] | Yes | Array of destination locations |
| `travelMode` | TravelMode | No | DRIVE, WALK, BICYCLE, TRANSIT |
| `routingPreference` | RoutingPreference | No | Traffic-aware routing preference |
| `departureTime` | Timestamp | No | Departure time for traffic calculations |
| `languageCode` | string | No | Response language |
| `units` | Units | No | IMPERIAL or METRIC |
| `extraComputations` | ExtraComputation[] | No | Additional computations |

#### Response

Returns a stream of `RouteMatrixElement` objects, one for each origin-destination pair.

#### Example Request

```bash
curl -X POST \
  'https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix?key=YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -H 'X-Goog-FieldMask: originIndex,destinationIndex,duration,distanceMeters,status' \
  -d '{
    "origins": [
      {
        "location": {
          "latLng": {
            "latitude": 37.419734,
            "longitude": -122.0827784
          }
        }
      }
    ],
    "destinations": [
      {
        "location": {
          "latLng": {
            "latitude": 37.417670,
            "longitude": -122.079595
          }
        }
      }
    ],
    "travelMode": "DRIVE"
  }'
```

## Authentication

All requests require authentication via:
- **API Key**: Pass as `key` query parameter
- **OAuth 2.0**: Include access token in `Authorization` header

## Field Masks

Use the `X-Goog-FieldMask` header to specify which fields to return in the response. This reduces response size and improves performance.

Example:
```
X-Goog-FieldMask: routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline
```

## Rate Limits

- Standard quotas apply based on your Google Cloud project
- See Google Cloud Console for your specific limits

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_ARGUMENT` | Invalid request parameters |
| `PERMISSION_DENIED` | API key invalid or insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `RESOURCE_EXHAUSTED` | Quota exceeded |
| `INTERNAL` | Internal server error |

## References

- [Routes API Documentation](https://developers.google.com/maps/documentation/routes)
- [REST Reference](https://developers.google.com/maps/documentation/routes/reference/rest)

