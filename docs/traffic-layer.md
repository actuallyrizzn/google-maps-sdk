# Traffic Layer Documentation

## Overview

The Traffic Layer is a feature of the Maps JavaScript API that allows you to display real-time traffic conditions on your maps. This is **not a REST API endpoint** but rather a JavaScript API feature.

**Type**: JavaScript API (Client-side)

**Status**: Active

**Availability**: Select regions only

## Implementation

### Basic Traffic Layer

Add a traffic layer to display real-time traffic conditions:

```javascript
function initMap() {
  const map = new google.maps.Map(
    document.getElementById("map"),
    {
      zoom: 13,
      center: { lat: 34.04924594193164, lng: -118.24104309082031 },
    }
  );

  const trafficLayer = new google.maps.TrafficLayer();
  trafficLayer.setMap(map);
}
```

### TypeScript Example

```typescript
function initMap(): void {
  const map = new google.maps.Map(
    document.getElementById("map") as HTMLElement,
    {
      zoom: 13,
      center: { lat: 34.04924594193164, lng: -118.24104309082031 },
    }
  );

  const trafficLayer = new google.maps.TrafficLayer();
  trafficLayer.setMap(map);
}

declare global {
  interface Window {
    initMap: () => void;
  }
}
window.initMap = initMap;
```

## TrafficLayer Object

### Constructor

```javascript
new google.maps.TrafficLayer(options?)
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `autoRefresh` | boolean | Automatically refresh traffic data (default: `true`) |

### Methods

#### `setMap(map)`

Sets the map on which to display the traffic layer.

**Parameters**:
- `map`: `google.maps.Map` - The map object

**Example**:
```javascript
const trafficLayer = new google.maps.TrafficLayer();
trafficLayer.setMap(map);
```

#### `getMap()`

Returns the map on which the traffic layer is displayed.

**Returns**: `google.maps.Map` or `null`

**Example**:
```javascript
const map = trafficLayer.getMap();
```

## Traffic Display

The Traffic Layer displays traffic conditions using color-coded lines:

- **Green**: No traffic delays
- **Yellow**: Moderate traffic
- **Orange**: Heavy traffic
- **Red**: Severe traffic delays

Traffic information is refreshed frequently, but not instantly. Rapid consecutive requests for the same area are unlikely to yield different results.

## Complete Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>Traffic Layer Example</title>
  <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap" async defer></script>
  <style>
    #map {
      height: 100%;
    }
    html, body {
      height: 100%;
      margin: 0;
      padding: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    function initMap() {
      const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: { lat: 34.04924594193164, lng: -118.24104309082031 },
      });

      const trafficLayer = new google.maps.TrafficLayer();
      trafficLayer.setMap(map);
    }
  </script>
</body>
</html>
```

## Toggling Traffic Layer

You can toggle the traffic layer on and off:

```javascript
let trafficLayer = null;
let isTrafficVisible = false;

function toggleTraffic() {
  if (!trafficLayer) {
    trafficLayer = new google.maps.TrafficLayer();
  }
  
  if (isTrafficVisible) {
    trafficLayer.setMap(null);
    isTrafficVisible = false;
  } else {
    trafficLayer.setMap(map);
    isTrafficVisible = true;
  }
}
```

## Related Layers

### Transit Layer

Display public transit networks:

```javascript
const transitLayer = new google.maps.TransitLayer();
transitLayer.setMap(map);
```

### Bicycling Layer

Display bicycle routes:

```javascript
const bicyclingLayer = new google.maps.BicyclingLayer();
bicyclingLayer.setMap(map);
```

## Limitations

1. **Regional Availability**: Traffic data is only available in select regions
2. **Refresh Rate**: Traffic information is not updated in real-time
3. **No REST API**: This is a client-side JavaScript feature only
4. **No Programmatic Access**: Traffic incident data is not exposed as separate API endpoints

## Traffic Incident Data

**Important**: The Traffic Layer does **not** provide programmatic access to traffic incident data. Traffic incidents are displayed visually on the map but cannot be accessed via API endpoints.

If you need programmatic access to traffic data:
- Use the **Routes API** with traffic-aware routing
- Use the **Directions API** with `departure_time` and `traffic_model` parameters
- Traffic conditions are reflected in route duration estimates

## Integration with Routes API

While the Traffic Layer is visual-only, you can combine it with the Routes API for comprehensive traffic-aware routing:

```javascript
// 1. Get route with traffic data using Routes API
const route = await computeRoute(origin, destination, {
  routingPreference: 'TRAFFIC_AWARE',
  departureTime: new Date()
});

// 2. Display route on map
const routePolyline = new google.maps.Polyline({
  path: route.polyline,
  map: map
});

// 3. Add traffic layer for visual context
const trafficLayer = new google.maps.TrafficLayer();
trafficLayer.setMap(map);
```

## Best Practices

1. **Check Availability**: Verify traffic data is available in your target region
2. **Combine with Routing**: Use Routes API for traffic-aware routing, Traffic Layer for visualization
3. **User Control**: Provide UI controls to toggle traffic layer on/off
4. **Performance**: Traffic layer adds network requests; consider lazy loading
5. **Mobile Optimization**: Traffic layer can impact mobile performance

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers supported
- Requires JavaScript enabled

## API Key Requirements

- Valid Google Maps JavaScript API key
- Maps JavaScript API must be enabled in Google Cloud Console
- No additional API enablement required for Traffic Layer

## References

- [Traffic Layer Documentation](https://developers.google.com/maps/documentation/javascript/trafficlayer)
- [Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)
- [Routes API](./routes-api-endpoints.md) - For traffic-aware routing

