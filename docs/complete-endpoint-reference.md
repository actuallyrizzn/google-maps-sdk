# Complete Google Maps Platform Endpoint Reference

## Quick Reference Table

| API | Base URL | Endpoints | Status | Recommended |
|-----|----------|-----------|--------|-------------|
| Routes API | `https://routes.googleapis.com` | 2 | Active | ✅ Yes |
| Directions API (Legacy) | `https://maps.googleapis.com/maps/api/directions` | 2 | Legacy | ⚠️ Migrate |
| Roads API | `https://roads.googleapis.com/v1` | 3 | Active | ✅ Yes |
| Traffic Layer | JavaScript API | N/A | Active | ✅ Yes |

## All Endpoints Summary

### Routes API

1. **POST** `/directions/v2:computeRoutes`
   - Calculate routes with traffic-aware routing
   - Full URL: `https://routes.googleapis.com/directions/v2:computeRoutes`

2. **POST** `/distanceMatrix/v2:computeRouteMatrix`
   - Compute route matrix for multiple origins/destinations
   - Full URL: `https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix`

### Directions API (Legacy)

1. **GET** `/json`
   - Get directions in JSON format
   - Full URL: `https://maps.googleapis.com/maps/api/directions/json`

2. **GET** `/xml`
   - Get directions in XML format
   - Full URL: `https://maps.googleapis.com/maps/api/directions/xml`

### Roads API

1. **GET** `/snapToRoads`
   - Snap GPS path to roads
   - Full URL: `https://roads.googleapis.com/v1/snapToRoads`

2. **GET** `/nearestRoads`
   - Find nearest roads for GPS points
   - Full URL: `https://roads.googleapis.com/v1/nearestRoads`

3. **GET** `/speedLimits`
   - Get speed limits for road segments
   - Full URL: `https://roads.googleapis.com/v1/speedLimits`

### Traffic Layer

- **JavaScript API** (not REST)
- Class: `google.maps.TrafficLayer`
- No REST endpoints available

## Endpoint Details

### Routes API Endpoints

#### 1. Compute Routes
```
POST https://routes.googleapis.com/directions/v2:computeRoutes
Content-Type: application/json
X-Goog-FieldMask: routes.duration,routes.distanceMeters,routes.polyline

{
  "origin": { "location": { "latLng": { "latitude": 37.419734, "longitude": -122.0827784 } } },
  "destination": { "location": { "latLng": { "latitude": 37.417670, "longitude": -122.079595 } } },
  "travelMode": "DRIVE",
  "routingPreference": "TRAFFIC_AWARE"
}
```

#### 2. Compute Route Matrix
```
POST https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix
Content-Type: application/json
X-Goog-FieldMask: originIndex,destinationIndex,duration,distanceMeters

{
  "origins": [{ "location": { "latLng": { "latitude": 37.419734, "longitude": -122.0827784 } } }],
  "destinations": [{ "location": { "latLng": { "latitude": 37.417670, "longitude": -122.079595 } } }],
  "travelMode": "DRIVE"
}
```

### Directions API (Legacy) Endpoints

#### 1. Get Directions (JSON)
```
GET https://maps.googleapis.com/maps/api/directions/json?origin=Toronto&destination=Montreal&key=YOUR_API_KEY
```

#### 2. Get Directions (XML)
```
GET https://maps.googleapis.com/maps/api/directions/xml?origin=Toronto&destination=Montreal&key=YOUR_API_KEY
```

### Roads API Endpoints

#### 1. Snap to Roads
```
GET https://roads.googleapis.com/v1/snapToRoads?path=60.170880,24.942795|60.170879,24.942796&key=YOUR_API_KEY
```

#### 2. Nearest Roads
```
GET https://roads.googleapis.com/v1/nearestRoads?points=60.170880,24.942795|60.170879,24.942796&key=YOUR_API_KEY
```

#### 3. Speed Limits
```
GET https://roads.googleapis.com/v1/speedLimits?path=60.170880,24.942795|60.170879,24.942796&key=YOUR_API_KEY
```

## Authentication

All REST endpoints require authentication:

1. **API Key** (Query Parameter)
   ```
   ?key=YOUR_API_KEY
   ```

2. **OAuth 2.0** (Header)
   ```
   Authorization: Bearer YOUR_ACCESS_TOKEN
   ```

## Common Parameters

### Location Formats

All APIs accept locations in multiple formats:

1. **Coordinates**: `latitude,longitude`
   ```
   origin=37.419734,-122.0827784
   ```

2. **Place ID**: `place_id:PLACE_ID`
   ```
   origin=place_id:ChIJ685WIFYViEgRHlHvBbiD5nE
   ```

3. **Address**: URL-encoded address
   ```
   origin=24+Sussex+Drive+Ottawa+ON
   ```

4. **Plus Code**: URL-encoded plus code
   ```
   origin=849VCWC8%2BR9
   ```

## Traffic-Aware Routing

### Routes API (Recommended)
```json
{
  "routingPreference": "TRAFFIC_AWARE",
  "departureTime": "2025-12-15T10:00:00Z"
}
```

### Directions API (Legacy)
```
?departure_time=now&traffic_model=best_guess
```

## Response Formats

### JSON (Default)
- Routes API: Always JSON
- Directions API: `/json` endpoint
- Roads API: Always JSON

### XML
- Directions API: `/xml` endpoint only

## Rate Limits

All APIs have rate limits based on:
- Google Cloud project quotas
- API-specific limits
- Billing tier

Check Google Cloud Console for your specific limits.

## Error Codes

Common error codes across all APIs:

| Code | Description |
|------|-------------|
| `INVALID_ARGUMENT` | Invalid request parameters |
| `PERMISSION_DENIED` | Invalid API key or insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `RESOURCE_EXHAUSTED` | Quota exceeded |
| `INTERNAL` | Internal server error |

## Migration Guide

### From Directions API to Routes API

**Old (Directions API)**:
```
GET /maps/api/directions/json?origin=Toronto&destination=Montreal&key=KEY
```

**New (Routes API)**:
```
POST /directions/v2:computeRoutes
{
  "origin": { "location": { "address": "Toronto" } },
  "destination": { "location": { "address": "Montreal" } }
}
```

## Best Practices

1. **Use Routes API** for new projects (not Directions API)
2. **Use Place IDs** instead of addresses when possible
3. **Implement field masks** for Routes API to reduce response size
4. **Cache responses** when appropriate
5. **Handle errors gracefully** with retry logic
6. **Monitor quota usage** in Google Cloud Console

## Related Documentation

- [Routes API Endpoints](./routes-api-endpoints.md)
- [Directions API Endpoints](./directions-api-endpoints.md)
- [Roads API Endpoints](./roads-api-endpoints.md)
- [Traffic Layer Documentation](./traffic-layer.md)

## Support

- [Google Maps Platform Support](https://developers.google.com/maps/support)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-maps)
- [Issue Tracker](https://issuetracker.google.com/issues?q=componentid:188323)

