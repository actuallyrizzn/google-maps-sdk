# Roads API Endpoints

## Overview

The Roads API is a service that accepts HTTPS requests with latitude/longitude coordinates and returns road-related data including snapped coordinates, nearest roads, and speed limits.

**Base URL**: `https://roads.googleapis.com/v1`

**Status**: Active

## Endpoints

### 1. Snap to Roads

Snaps a GPS path to the most likely roads the vehicle was traveling along. Returns up to 100 GPS points from a route with road-snapped coordinates and place IDs.

**Endpoint**: `/snapToRoads`

**Full URL**: `https://roads.googleapis.com/v1/snapToRoads`

**HTTP Method**: `GET`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to snap (pipe-separated lat/lng pairs: `lat1,lng1\|lat2,lng2\|...`) |
| `interpolate` | boolean | No | Interpolate path to include all points forming full road geometry (default: `false`) |
| `key` | string | Yes | Your API key |

#### Example Request

```bash
curl 'https://roads.googleapis.com/v1/snapToRoads?path=60.170880,24.942795|60.170879,24.942796|60.170877,24.942796&key=YOUR_API_KEY'
```

#### Example with Interpolation

```bash
curl 'https://roads.googleapis.com/v1/snapToRoads?path=60.170880,24.942795|60.170879,24.942796|60.170877,24.942796&interpolate=true&key=YOUR_API_KEY'
```

#### Response Format

```json
{
  "snappedPoints": [
    {
      "location": {
        "latitude": 60.170877,
        "longitude": 24.942796
      },
      "originalIndex": 0,
      "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE"
    },
    {
      "location": {
        "latitude": 60.170879,
        "longitude": 24.942796
      },
      "originalIndex": 1,
      "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE"
    },
    {
      "location": {
        "latitude": 60.170877,
        "longitude": 24.942796
      },
      "originalIndex": 2,
      "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE"
    }
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `snappedPoints[]` | array | Array of snapped points |
| `snappedPoints[].location` | object | Snapped latitude/longitude |
| `snappedPoints[].originalIndex` | integer | Index of original point in request |
| `snappedPoints[].placeId` | string | Place ID of the road segment |

#### Limits

- Maximum 100 GPS points per request
- Points should represent a continuous path
- Interpolation can add additional points to the response

---

### 2. Nearest Roads

Identifies the nearest road segments for a set of GPS points. Points don't need to be part of a continuous path.

**Endpoint**: `/nearestRoads`

**Full URL**: `https://roads.googleapis.com/v1/nearestRoads`

**HTTP Method**: `GET`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `points` | string | Yes | Points to find nearest roads for (pipe-separated lat/lng pairs) |
| `key` | string | Yes | Your API key |

#### Example Request

```bash
curl 'https://roads.googleapis.com/v1/nearestRoads?points=60.170880,24.942795|60.170879,24.942796|60.170877,24.942796&key=YOUR_API_KEY'
```

#### Response Format

```json
{
  "snappedPoints": [
    {
      "location": {
        "latitude": 60.170877,
        "longitude": 24.942796
      },
      "originalIndex": 0,
      "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE"
    },
    {
      "location": {
        "latitude": 60.170879,
        "longitude": 24.942796
      },
      "originalIndex": 1,
      "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE"
    },
    {
      "location": {
        "latitude": 60.170877,
        "longitude": 24.942796
      },
      "originalIndex": 2,
      "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE"
    }
  ]
}
```

#### Response Fields

Same as Snap to Roads endpoint.

#### Differences from Snap to Roads

- Points don't need to form a continuous path
- No interpolation option
- Each point is independently snapped to nearest road

---

### 3. Speed Limits

Returns the posted speed limits for road segments. Available to all customers with an Asset Tracking license.

**Endpoint**: `/speedLimits`

**Full URL**: `https://roads.googleapis.com/v1/speedLimits`

**HTTP Method**: `GET`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | No* | Path of road segments (pipe-separated lat/lng pairs) |
| `placeId` | string | No* | Comma-separated list of Place IDs representing road segments |
| `key` | string | Yes | Your API key |

*Either `path` or `placeId` must be provided, but not both.

#### Example Request with Path

```bash
curl 'https://roads.googleapis.com/v1/speedLimits?path=60.170880,24.942795|60.170879,24.942796|60.170877,24.942796&key=YOUR_API_KEY'
```

#### Example Request with Place IDs

```bash
curl 'https://roads.googleapis.com/v1/speedLimits?placeId=ChIJ685WIFYViEgRHlHvBbiD5nE,ChIJA01I-8YVhkgRGJb0fW4UX7Y&key=YOUR_API_KEY'
```

#### Response Format

```json
{
  "speedLimits": [
    {
      "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE",
      "speedLimit": 60,
      "units": "KPH"
    },
    {
      "placeId": "ChIJA01I-8YVhkgRGJb0fW4UX7Y",
      "speedLimit": 50,
      "units": "KPH"
    }
  ],
  "snappedPoints": [
    {
      "location": {
        "latitude": 60.170877,
        "longitude": 24.942796
      },
      "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE",
      "originalIndex": 0
    }
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `speedLimits[]` | array | Array of speed limit data |
| `speedLimits[].placeId` | string | Place ID of the road segment |
| `speedLimits[].speedLimit` | integer | Speed limit value |
| `speedLimits[].units` | string | Units: `KPH` (kilometers per hour) or `MPH` (miles per hour) |
| `snappedPoints[]` | array | Snapped points (when using `path` parameter) |

#### Speed Limit Units

- `KPH`: Kilometers per hour (metric)
- `MPH`: Miles per hour (imperial)

Units are determined automatically based on the region.

#### Limits

- Maximum 100 points or place IDs per request
- Speed limit data availability varies by region

## Common Usage Patterns

### 1. Snap GPS Track to Roads

```bash
# Step 1: Snap path to roads
curl 'https://roads.googleapis.com/v1/snapToRoads?path=60.170880,24.942795|60.170879,24.942796&interpolate=true&key=YOUR_API_KEY'

# Step 2: Get speed limits for snapped path
# Extract place IDs from step 1, then:
curl 'https://roads.googleapis.com/v1/speedLimits?placeId=ChIJ685WIFYViEgRHlHvBbiD5nE,ChIJA01I-8YVhkgRGJb0fW4UX7Y&key=YOUR_API_KEY'
```

### 2. Find Nearest Road for GPS Points

```bash
curl 'https://roads.googleapis.com/v1/nearestRoads?points=60.170880,24.942795|60.170879,24.942796&key=YOUR_API_KEY'
```

### 3. Get Speed Limits Along a Route

```bash
# Using path directly
curl 'https://roads.googleapis.com/v1/speedLimits?path=60.170880,24.942795|60.170879,24.942796|60.170877,24.942796&key=YOUR_API_KEY'
```

## Processing Long Paths

For paths with more than 100 points:

1. Split the path into chunks of 100 points
2. Make separate requests for each chunk
3. Combine the results
4. Use interpolation to smooth the combined path

## Error Handling

### Common Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `INVALID_ARGUMENT` | Invalid path format | Check lat/lng format |
| `PERMISSION_DENIED` | Invalid API key | Verify API key |
| `NOT_FOUND` | No roads found | Check coordinates are valid |
| `RESOURCE_EXHAUSTED` | Quota exceeded | Check usage limits |

## Authentication

All requests require an API key passed as the `key` query parameter.

## Rate Limits

- Standard quotas apply based on your Google Cloud project
- See Google Cloud Console for specific limits
- Speed Limits endpoint requires Asset Tracking license

## References

- [Roads API Documentation](https://developers.google.com/maps/documentation/roads)
- [Roads API Overview](https://developers.google.com/maps/documentation/roads/overview)
- [Snap to Roads Guide](https://developers.google.com/maps/documentation/roads/snap-to-roads)
- [Nearest Roads Guide](https://developers.google.com/maps/documentation/roads/nearest-roads)
- [Speed Limits Guide](https://developers.google.com/maps/documentation/roads/speed-limits)

