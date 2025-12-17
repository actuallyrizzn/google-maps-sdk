"""
Utility functions for validation and sanitization
"""

import re
import hashlib
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any, Union


# Constants for validation
MIN_API_KEY_LENGTH = 20
API_KEY_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')


def validate_api_key(api_key: str) -> str:
    """
    Validate API key format
    
    Args:
        api_key: API key to validate
        
    Returns:
        Stripped API key
        
    Raises:
        TypeError: If API key is not a string
        ValueError: If API key is invalid format
    """
    if not isinstance(api_key, str):
        raise TypeError("API key must be a non-empty string")
    
    if not api_key:
        raise ValueError("API key is required")
    
    api_key = api_key.strip()
    
    if not api_key:
        raise ValueError("API key cannot be whitespace-only")
    
    if len(api_key) < MIN_API_KEY_LENGTH:
        raise ValueError(
            f"API key appears to be invalid (too short: {len(api_key)} chars, "
            f"minimum: {MIN_API_KEY_LENGTH})"
        )
    
    if not API_KEY_PATTERN.match(api_key):
        raise ValueError("API key contains invalid characters (only alphanumeric, underscore, and hyphen allowed)")
    
    return api_key


def sanitize_api_key_for_logging(text: str, api_key: str) -> str:
    """
    Remove API key from log messages to prevent exposure
    
    Args:
        text: Text that may contain API key
        api_key: API key to sanitize
        
    Returns:
        Text with API key replaced by placeholder
    """
    if not api_key or not text:
        return text
    
    # Replace API key with placeholder
    sanitized = re.sub(
        re.escape(api_key),
        "[API_KEY_REDACTED]",
        text,
        flags=re.IGNORECASE
    )
    
    return sanitized


def hash_api_key(api_key: str, length: int = 16) -> str:
    """
    Create a hash of API key for safe logging/display
    
    Args:
        api_key: API key to hash
        length: Length of hash prefix to return
        
    Returns:
        First N characters of SHA256 hash
    """
    if not api_key:
        return ""
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:length]
    return key_hash


def validate_base_url(base_url: str) -> str:
    """
    Validate base URL format
    
    Args:
        base_url: Base URL to validate
        
    Returns:
        Validated and normalized base URL
        
    Raises:
        TypeError: If base_url is not a string
        ValueError: If base_url is invalid format
    """
    if not isinstance(base_url, str):
        raise TypeError("Base URL must be a string")
    
    if not base_url:
        raise ValueError("Base URL is required")
    
    base_url = base_url.strip()
    
    if not base_url:
        raise ValueError("Base URL cannot be whitespace-only")
    
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'  # domain name
        r'(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*'  # domain parts
        r'(:[0-9]{1,5})?'  # optional port
        r'(/.*)?$'  # optional path
    )
    
    if not url_pattern.match(base_url):
        raise ValueError(f"Invalid base URL format: {base_url}")
    
    return base_url.rstrip("/")


def validate_timeout(timeout: Optional[int]) -> int:
    """
    Validate timeout value
    
    Args:
        timeout: Timeout value in seconds
        
    Returns:
        Validated timeout value
        
    Raises:
        TypeError: If timeout is not an integer
        ValueError: If timeout is invalid
    """
    if timeout is None:
        return 30  # Default timeout
    
    if not isinstance(timeout, (int, float)):
        raise TypeError("Timeout must be a number")
    
    timeout = int(timeout)
    
    if timeout < 1:
        raise ValueError("Timeout must be at least 1 second")
    
    if timeout > 300:  # 5 minutes max
        raise ValueError("Timeout cannot exceed 300 seconds (5 minutes)")
    
    return timeout


def validate_non_empty_string(value: str, field_name: str = "value") -> str:
    """
    Validate that a string is not empty or whitespace-only
    
    Args:
        value: String to validate
        field_name: Name of the field for error messages
        
    Returns:
        Stripped string
        
    Raises:
        TypeError: If value is not a string
        ValueError: If value is empty or whitespace-only
    """
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty or whitespace-only")
    
    return value.strip()


# Constants for validation
MAX_WAYPOINTS = 25  # Google Maps API limit
MAX_ROUTE_MATRIX_ORIGINS = 50
MAX_ROUTE_MATRIX_DESTINATIONS = 50
MAX_ROADS_POINTS = 100
MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0

# Valid enum values
VALID_TRAVEL_MODES = {"DRIVE", "WALK", "BICYCLE", "TRANSIT", "driving", "walking", "bicycling", "transit"}
VALID_ROUTING_PREFERENCES = {"TRAFFIC_AWARE", "TRAFFIC_AWARE_OPTIMAL"}
VALID_UNITS = {"IMPERIAL", "METRIC", "imperial", "metric"}
VALID_POLYLINE_QUALITY = {"HIGH_QUALITY", "OVERVIEW"}
VALID_POLYLINE_ENCODING = {"ENCODED_POLYLINE", "GEO_JSON_LINESTRING"}


def validate_coordinate(latitude: float, longitude: float) -> Tuple[float, float]:
    """
    Validate coordinate values (issue #9)
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        Tuple of (latitude, longitude)
        
    Raises:
        TypeError: If coordinates are not numbers
        ValueError: If coordinates are out of valid range
    """
    if not isinstance(latitude, (int, float)):
        raise TypeError("Latitude must be a number")
    if not isinstance(longitude, (int, float)):
        raise TypeError("Longitude must be a number")
    
    lat = float(latitude)
    lng = float(longitude)
    
    if not (MIN_LATITUDE <= lat <= MAX_LATITUDE):
        raise ValueError(f"Latitude must be between {MIN_LATITUDE} and {MAX_LATITUDE}, got {lat}")
    
    if not (MIN_LONGITUDE <= lng <= MAX_LONGITUDE):
        raise ValueError(f"Longitude must be between {MIN_LONGITUDE} and {MAX_LONGITUDE}, got {lng}")
    
    return lat, lng


def format_coordinate(latitude: float, longitude: float, precision: int = 7) -> str:
    """
    Format coordinate as string with specified precision (issue #10)
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        precision: Decimal precision (default 7 for ~1cm accuracy)
        
    Returns:
        Formatted coordinate string "lat,lng"
    """
    lat, lng = validate_coordinate(latitude, longitude)
    return f"{lat:.{precision}f},{lng:.{precision}f}"


def validate_coordinate_tuple(coord: Tuple[float, float]) -> Tuple[float, float]:
    """
    Validate coordinate tuple format (issue #23)
    
    Args:
        coord: Tuple of (latitude, longitude)
        
    Returns:
        Validated tuple
        
    Raises:
        TypeError: If not a tuple or wrong length
        ValueError: If coordinates are invalid
    """
    if not isinstance(coord, tuple):
        raise TypeError("Coordinate must be a tuple")
    
    if len(coord) != 2:
        raise ValueError(f"Coordinate tuple must have exactly 2 elements, got {len(coord)}")
    
    return validate_coordinate(coord[0], coord[1])


def validate_waypoint_count(waypoints: Optional[List[Any]], max_waypoints: int = MAX_WAYPOINTS) -> None:
    """
    Validate waypoint count (issue #16)
    
    Args:
        waypoints: List of waypoints
        max_waypoints: Maximum allowed waypoints
        
    Raises:
        ValueError: If waypoint count exceeds limit
    """
    if waypoints is None:
        return
    
    if not isinstance(waypoints, list):
        raise TypeError("Waypoints must be a list")
    
    if len(waypoints) > max_waypoints:
        raise ValueError(f"Maximum {max_waypoints} waypoints allowed, got {len(waypoints)}")


def validate_route_matrix_size(origins: List[Any], destinations: List[Any]) -> None:
    """
    Validate route matrix size (issue #22)
    
    Args:
        origins: List of origin waypoints
        destinations: List of destination waypoints
        
    Raises:
        ValueError: If matrix size exceeds limits
    """
    if not isinstance(origins, list):
        raise TypeError("Origins must be a list")
    
    if not isinstance(destinations, list):
        raise TypeError("Destinations must be a list")
    
    if len(origins) == 0:
        raise ValueError("Origins list cannot be empty")
    
    if len(destinations) == 0:
        raise ValueError("Destinations list cannot be empty")
    
    if len(origins) > MAX_ROUTE_MATRIX_ORIGINS:
        raise ValueError(f"Maximum {MAX_ROUTE_MATRIX_ORIGINS} origins allowed, got {len(origins)}")
    
    if len(destinations) > MAX_ROUTE_MATRIX_DESTINATIONS:
        raise ValueError(f"Maximum {MAX_ROUTE_MATRIX_DESTINATIONS} destinations allowed, got {len(destinations)}")


def validate_path_or_points(path: Optional[List[Tuple[float, float]]], points: Optional[List[Tuple[float, float]]], max_points: int = MAX_ROADS_POINTS) -> None:
    """
    Validate path or points list (issue #20)
    
    Args:
        path: Optional path list
        points: Optional points list
        max_points: Maximum allowed points
        
    Raises:
        ValueError: If validation fails
    """
    if path is not None:
        if not isinstance(path, list):
            raise TypeError("Path must be a list")
        if len(path) == 0:
            raise ValueError("Path cannot be empty")
        if len(path) > max_points:
            raise ValueError(f"Maximum {max_points} points allowed in path, got {len(path)}")
        # Validate each coordinate tuple
        for i, coord in enumerate(path):
            try:
                validate_coordinate_tuple(coord)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid coordinate at index {i}: {e}") from e
    
    if points is not None:
        if not isinstance(points, list):
            raise TypeError("Points must be a list")
        if len(points) == 0:
            raise ValueError("Points cannot be empty")
        if len(points) > max_points:
            raise ValueError(f"Maximum {max_points} points allowed, got {len(points)}")
        # Validate each coordinate tuple
        for i, coord in enumerate(points):
            try:
                validate_coordinate_tuple(coord)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid coordinate at index {i}: {e}") from e


def validate_enum_value(value: str, valid_values: set, field_name: str = "value", normalize_case: bool = True) -> str:
    """
    Validate enum-like parameter (issue #15)
    
    Args:
        value: Value to validate
        valid_values: Set of valid values
        field_name: Name of the field for error messages
        normalize_case: If True, normalize to match valid_values case; if False, preserve original case
        
    Returns:
        Validated value (normalized or original case)
        
    Raises:
        TypeError: If value is not a string
        ValueError: If value is not in valid set
    """
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    
    value_upper = value.upper()
    valid_upper = {v.upper() for v in valid_values}
    
    if value_upper not in valid_upper:
        raise ValueError(f"{field_name} must be one of {sorted(valid_values)}, got {value}")
    
    if normalize_case:
        # Find matching value from valid_values and return it (preserving its case)
        for valid_val in valid_values:
            if valid_val.upper() == value_upper:
                return valid_val
        # Fallback: return uppercase if no match found (shouldn't happen)
        return value_upper
    
    # Return original value if normalize_case is False
    return value


def validate_language_code(language_code: Optional[str]) -> Optional[str]:
    """
    Validate language code format (issue #43)
    
    Args:
        language_code: Language code (e.g., "en", "en-US")
        
    Returns:
        Validated language code
        
    Raises:
        ValueError: If language code format is invalid
    """
    if language_code is None:
        return None
    
    if not isinstance(language_code, str):
        raise TypeError("Language code must be a string")
    
    language_code = language_code.strip()
    
    if not language_code:
        raise ValueError("Language code cannot be empty or whitespace-only")
    
    # Basic format: 2-5 characters, optionally with hyphen and region code
    lang_pattern = re.compile(r'^[a-z]{2}(-[A-Z]{2,3})?$', re.IGNORECASE)
    
    if not lang_pattern.match(language_code):
        raise ValueError(f"Invalid language code format: {language_code}. Expected format: 'en' or 'en-US'")
    
    return language_code


def validate_api_version(api_version: Optional[str]) -> Optional[str]:
    """
    Validate API version format (issue #76)
    
    Args:
        api_version: API version string (e.g., "v1", "v2")
        
    Returns:
        Validated API version string
        
    Raises:
        ValueError: If API version format is invalid
    """
    if api_version is None:
        return None
    
    if not isinstance(api_version, str):
        raise TypeError("API version must be a string")
    
    api_version = api_version.strip()
    
    if not api_version:
        raise ValueError("API version cannot be empty or whitespace-only")
    
    # Validate format: should start with 'v' followed by digits
    import re
    version_pattern = re.compile(r'^v\d+$', re.IGNORECASE)
    
    if not version_pattern.match(api_version):
        raise ValueError(f"Invalid API version format: {api_version}. Expected format: 'v1', 'v2', 'v3', etc.")
    
    return api_version.lower()  # Normalize to lowercase


def validate_region(region: Optional[str]) -> Optional[str]:
    """
    Validate Google Cloud region format (issue #77)
    
    Args:
        region: Region string (e.g., "us-central1", "europe-west1", "asia-east1")
        
    Returns:
        Validated region string (lowercase)
        
    Raises:
        ValueError: If region format is invalid
    """
    if region is None:
        return None
    
    if not isinstance(region, str):
        raise TypeError("Region must be a string")
    
    region = region.strip().lower()
    
    if not region:
        raise ValueError("Region cannot be empty or whitespace-only")
    
    # Validate format: should match Google Cloud region pattern
    # Format: {location}-{number} (e.g., us-central1, europe-west1)
    region_pattern = re.compile(r'^[a-z]+-[a-z0-9]+[0-9]+$')
    
    if not region_pattern.match(region):
        raise ValueError(
            f"Invalid region format: {region}. "
            f"Expected format: 'us-central1', 'europe-west1', 'asia-east1', etc."
        )
    
    return region


def validate_units(units: Optional[str]) -> Optional[str]:
    """
    Validate units parameter (issue #44)
    
    Args:
        units: Units value (IMPERIAL or METRIC)
        
    Returns:
        Validated units value
        
    Raises:
        ValueError: If units is invalid
    """
    if units is None:
        return None
    
    return validate_enum_value(units, VALID_UNITS, "units")


def validate_departure_time(departure_time: Optional[Union[str, int]]) -> Optional[str]:
    """
    Validate departure time format (issue #25)
    
    Args:
        departure_time: Departure time ("now", ISO 8601 string, or Unix timestamp)
        
    Returns:
        Validated departure time string
        
    Raises:
        ValueError: If departure time format is invalid
    """
    if departure_time is None:
        return None
    
    if isinstance(departure_time, int):
        # Unix timestamp
        if departure_time < 0:
            raise ValueError("Departure time timestamp cannot be negative")
        return str(departure_time)
    
    if not isinstance(departure_time, str):
        raise TypeError("Departure time must be a string or integer")
    
    departure_time = departure_time.strip()
    
    if departure_time.lower() == "now":
        return "now"
    
    # Try to parse as ISO 8601
    try:
        datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
        return departure_time
    except ValueError:
        # Try as Unix timestamp string
        try:
            ts = int(departure_time)
            if ts < 0:
                raise ValueError("Departure time timestamp cannot be negative")
            return str(ts)
        except ValueError:
            raise ValueError(f"Invalid departure time format: {departure_time}. Expected 'now', ISO 8601 string, or Unix timestamp")


def validate_field_mask(field_mask: Optional[str]) -> Optional[str]:
    """
    Validate field mask format (issue #34)
    
    Args:
        field_mask: Field mask string (comma-separated field paths)
        
    Returns:
        Validated and normalized field mask
        
    Raises:
        ValueError: If field mask format is invalid
    """
    if field_mask is None:
        return None
    
    if not isinstance(field_mask, str):
        raise TypeError("Field mask must be a string")
    
    field_mask = field_mask.strip()
    
    if not field_mask:
        raise ValueError("Field mask cannot be empty or whitespace-only")
    
    # Split by comma and validate each field
    fields = [f.strip() for f in field_mask.split(',')]
    
    if not fields:
        raise ValueError("Field mask must contain at least one field")
    
    # Validate each field path (should be dot-separated)
    for field in fields:
        if not field:
            raise ValueError("Field mask contains empty field")
        if '.' not in field:
            raise ValueError(f"Invalid field path: {field}. Must be dot-separated (e.g., 'routes.duration')")
    
    return ','.join(fields)


def sanitize_input(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize input string (issue #8)
    
    Args:
        value: Input string to sanitize
        max_length: Optional maximum length
        
    Returns:
        Sanitized string
        
    Raises:
        ValueError: If input is invalid
    """
    if not isinstance(value, str):
        raise TypeError("Input must be a string")
    
    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    if max_length and len(sanitized) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters")
    
    return sanitized
