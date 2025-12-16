# Directions API (Legacy) Endpoints

## Overview

The Directions API (Legacy) is a web service that calculates directions between locations. This API is in **Legacy status** - Google recommends migrating to the Routes API for new projects.

**Base URL**: `https://maps.googleapis.com/maps/api/directions`

**Status**: Legacy (Consider migrating to Routes API)

## Endpoints

### 1. Get Directions (JSON)

Returns directions in JSON format.

**Endpoint**: `/json`

**Full URL**: `https://maps.googleapis.com/maps/api/directions/json`

**HTTP Method**: `GET`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | string | Yes | Origin location (address, place ID, or lat/lng) |
| `destination` | string | Yes | Destination location |
| `key` | string | Yes | Your API key |
| `mode` | string | No | Travel mode: `driving`, `walking`, `bicycling`, `transit` (default: `driving`) |
| `waypoints` | string | No | Intermediate locations (pipe-separated: `\|`) |
| `alternatives` | boolean | No | Return alternative routes (default: `false`) |
| `avoid` | string | No | Avoid features: `tolls`, `highways`, `ferries`, `indoor` (comma-separated) |
| `language` | string | No | Response language (e.g., `en`, `es`) |
| `units` | string | No | Unit system: `metric` or `imperial` (default: `metric`) |
| `region` | string | No | Region code (e.g., `us`, `gb`) |
| `departure_time` | integer | No | Desired departure time (Unix timestamp) |
| `arrival_time` | integer | No | Desired arrival time (Unix timestamp) |
| `traffic_model` | string | No | Traffic model: `best_guess`, `pessimistic`, `optimistic` |
| `transit_mode` | string | No | Transit modes: `bus`, `subway`, `train`, `tram`, `rail` |
| `transit_routing_preference` | string | No | Transit routing: `less_walking`, `fewer_transfers` |

#### Example Request

```bash
curl 'https://maps.googleapis.com/maps/api/directions/json?origin=Toronto&destination=Montreal&key=YOUR_API_KEY'
```

#### Example with Waypoints

```bash
curl 'https://maps.googleapis.com/maps/api/directions/json?origin=Chicago,IL&destination=Los+Angeles,CA&waypoints=Joplin,MO|Oklahoma+City,OK&key=YOUR_API_KEY'
```

#### Example with Traffic-Aware Routing

```bash
curl 'https://maps.googleapis.com/maps/api/directions/json?origin=Toronto&destination=Montreal&departure_time=now&traffic_model=best_guess&key=YOUR_API_KEY'
```

#### Example with Place IDs

```bash
curl 'https://maps.googleapis.com/maps/api/directions/json?origin=place_id:ChIJ685WIFYViEgRHlHvBbiD5nE&destination=place_id:ChIJA01I-8YVhkgRGJb0fW4UX7Y&key=YOUR_API_KEY'
```

#### Example with Location Modifiers

**Side of Road**:
```bash
curl 'https://maps.googleapis.com/maps/api/directions/json?origin=37.7680296,-122.4375126&destination=side_of_road:37.7663444,-122.4412006&key=YOUR_API_KEY'
```

**Heading**:
```bash
curl 'https://maps.googleapis.com/maps/api/directions/json?origin=heading=90:37.773279,-122.468780&destination=37.773245,-122.469502&key=YOUR_API_KEY'
```

#### Example with Optimized Waypoints

```bash
curl 'https://maps.googleapis.com/maps/api/directions/json?origin=Adelaide,SA&destination=Adelaide,SA&waypoints=optimize:true|Barossa+Valley,SA|Clare,SA|Connawarra,SA|McLaren+Vale,SA&key=YOUR_API_KEY'
```

#### Response Format

```json
{
  "geocoded_waypoints": [
    {
      "geocoder_status": "OK",
      "place_id": "ChIJ...",
      "types": ["street_address"]
    }
  ],
  "routes": [
    {
      "bounds": {
        "northeast": {
          "lat": 45.501712,
          "lng": -73.567256
        },
        "southwest": {
          "lat": 43.653226,
          "lng": -79.383184
        }
      },
      "copyrights": "Map data ©2020",
      "legs": [
        {
          "distance": {
            "text": "542 km",
            "value": 542000
          },
          "duration": {
            "text": "5 hours 46 mins",
            "value": 20760
          },
          "duration_in_traffic": {
            "text": "6 hours 12 mins",
            "value": 22320
          },
          "end_address": "Montreal, QC, Canada",
          "end_location": {
            "lat": 45.501712,
            "lng": -73.567256
          },
          "start_address": "Toronto, ON, Canada",
          "start_location": {
            "lat": 43.653226,
            "lng": -79.383184
          },
          "steps": [...],
          "traffic_speed_entry": [...],
          "via_waypoint": [...]
        }
      ],
      "overview_polyline": {
        "points": "encoded_polyline_string"
      },
      "summary": "ON-401 E",
      "warnings": [],
      "waypoint_order": []
    }
  ],
  "status": "OK"
}
```

#### Response Status Codes

| Status | Description |
|--------|-------------|
| `OK` | Request successful |
| `NOT_FOUND` | Origin/destination not found |
| `ZERO_RESULTS` | No route found |
| `MAX_WAYPOINTS_EXCEEDED` | Too many waypoints (max 25) |
| `INVALID_REQUEST` | Invalid request parameters |
| `OVER_QUERY_LIMIT` | Quota exceeded |
| `REQUEST_DENIED` | Request denied (check API key) |
| `UNKNOWN_ERROR` | Server error |

---

### 2. Get Directions (XML)

Returns directions in XML format.

**Endpoint**: `/xml`

**Full URL**: `https://maps.googleapis.com/maps/api/directions/xml`

**HTTP Method**: `GET`

**Parameters**: Same as JSON endpoint

#### Example Request

```bash
curl 'https://maps.googleapis.com/maps/api/directions/xml?origin=Toronto&destination=Montreal&key=YOUR_API_KEY'
```

#### Response Format

```xml
<DirectionsResponse>
  <status>OK</status>
  <route>
    <summary>ON-401 E</summary>
    <leg>
      <step>
        <html_instructions>Head <b>north</b> on <b>Yonge St</b></html_instructions>
        <distance>
          <value>100</value>
          <text>100 m</text>
        </distance>
        <duration>
          <value>30</value>
          <text>1 min</text>
        </duration>
        <start_location>
          <lat>43.653226</lat>
          <lng>-79.383184</lng>
        </start_location>
        <end_location>
          <lat>43.654226</lat>
          <lng>-79.383184</lng>
        </end_location>
        <polyline>
          <points>encoded_polyline</points>
        </polyline>
        <travel_mode>DRIVING</travel_mode>
      </step>
    </leg>
  </route>
</DirectionsResponse>
```

## Waypoint Types

### Stopover Waypoints
Waypoints where the route must stop:
```
waypoints=Charlestown,MA|Lexington,MA
```

### Pass-Through Waypoints
Waypoints that influence the route but don't require stopping:
```
waypoints=via:Charlestown,MA|via:Lexington,MA
```

### Optimized Waypoints
Optimize the order of waypoints:
```
waypoints=optimize:true|Barossa+Valley,SA|Clare,SA|Connawarra,SA
```

## Location Formats

### Address
```
origin=24+Sussex+Drive+Ottawa+ON
```

### Place ID
```
origin=place_id:ChIJ3S-JXmauEmsRUcIaWtf4MzE
```

### Coordinates
```
origin=41.43206,-81.38992
```

### Plus Code
```
origin=849VCWC8%2BR9
```

## Traffic Information

To get traffic-aware routing:
1. Include `departure_time=now` or a future timestamp
2. Specify `traffic_model` (optional)
3. Response includes `duration_in_traffic` field

## Restrictions

- Maximum 25 waypoints per request
- URLs limited to 16,384 characters
- Transit mode requires `departure_time` or `arrival_time`
- Some features may not be available in all regions

## Migration to Routes API

Google recommends migrating to the Routes API for:
- Better performance
- More features
- Active development
- Better traffic modeling

See [Routes API Documentation](./routes-api-endpoints.md) for migration guide.

## References

- [Directions API Documentation](https://developers.google.com/maps/documentation/directions)
- [Get Directions Guide](https://developers.google.com/maps/documentation/directions/get-directions)

