"""
Command-line interface for Google Maps Platform SDK
"""

import sys
import argparse
from . import __version__


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Google Maps Platform Python SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"google-maps-sdk {__version__}",
    )
    
    parser.add_argument(
        "--api-key",
        help="Google Maps Platform API key",
    )
    
    # For now, just show version and help
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if args.api_key:
            # Use hash instead of exposing API key (issue #3)
            from .utils import hash_api_key
            key_hash = hash_api_key(args.api_key)
            print(f"API key hash: {key_hash}...")
            print("Use the SDK in your Python code:")
            print("  from google_maps_sdk import GoogleMapsClient")
            print("  client = GoogleMapsClient(api_key='YOUR_KEY')")


if __name__ == "__main__":
    main()

