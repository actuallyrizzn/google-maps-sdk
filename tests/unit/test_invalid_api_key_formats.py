"""
Unit tests for invalid API key formats (issue #262 / #64)
"""

import pytest
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.directions import DirectionsClient
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.client import GoogleMapsClient


@pytest.mark.unit
class TestInvalidAPIKeyFormats:
    """Test invalid API key format validation"""

    def test_whitespace_only_api_key(self):
        """Test whitespace-only API key is rejected"""
        with pytest.raises(ValueError, match="API key cannot be whitespace-only"):
            BaseClient("   ", "https://example.com")
        
        with pytest.raises(ValueError, match="API key cannot be whitespace-only"):
            BaseClient("\t", "https://example.com")
        
        with pytest.raises(ValueError, match="API key cannot be whitespace-only"):
            BaseClient("\n", "https://example.com")
        
        with pytest.raises(ValueError, match="API key cannot be whitespace-only"):
            BaseClient("\r\n", "https://example.com")
        
        with pytest.raises(ValueError, match="API key cannot be whitespace-only"):
            BaseClient(" \t\n\r ", "https://example.com")

    def test_too_short_api_key(self):
        """Test API key that is too short is rejected"""
        # Google Maps API keys are typically 39+ characters
        # But validation might have a minimum length requirement
        short_keys = [
            "a",
            "ab",
            "abc",
            "short",
            "1234567890123456789",  # 19 characters
        ]
        
        for short_key in short_keys:
            with pytest.raises((ValueError, TypeError)):
                BaseClient(short_key, "https://example.com")

    def test_api_key_with_invalid_characters(self):
        """Test API key with invalid characters"""
        # Test various invalid characters
        invalid_keys = [
            "test_key_with_newline\ninvalid",
            "test_key_with_tab\tinvalid",
            "test_key_with_null\0invalid",
            "test_key_with_unicode_control\u0001",
        ]
        
        for invalid_key in invalid_keys:
            # Some may pass validation but fail at API level
            # Test that they at least don't crash the client
            try:
                client = BaseClient(invalid_key, "https://example.com")
                client.close()
            except (ValueError, TypeError):
                # Expected - validation should reject
                pass

    def test_api_key_with_special_characters(self):
        """Test API key with special characters"""
        # Some special characters might be valid in API keys
        # Test that they don't cause crashes
        special_char_keys = [
            "test_key_with_underscore_123",
            "test-key-with-dashes-123",
            "test.key.with.dots.123",
            "test+key+with+plus+123",
        ]
        
        for special_key in special_char_keys:
            # These might be valid or invalid depending on Google's format
            # Test that client creation doesn't crash
            try:
                client = BaseClient(special_key, "https://example.com")
                client.close()
            except (ValueError, TypeError):
                # Expected if validation rejects
                pass

    def test_api_key_with_unicode_characters(self):
        """Test API key with Unicode characters"""
        unicode_keys = [
            "test_key_中文",
            "test_key_🚀",
            "test_key_émoji",
            "test_key_αβγ",
        ]
        
        for unicode_key in unicode_keys:
            # Unicode characters are likely invalid in API keys
            try:
                client = BaseClient(unicode_key, "https://example.com")
                client.close()
            except (ValueError, TypeError):
                # Expected - API keys should be ASCII
                pass

    def test_api_key_with_leading_trailing_whitespace(self):
        """Test API key with leading/trailing whitespace"""
        # Keys with whitespace should be stripped or rejected
        whitespace_keys = [
            " test_key_12345678901234567890",
            "test_key_12345678901234567890 ",
            "  test_key_12345678901234567890  ",
            "\ttest_key_12345678901234567890\t",
        ]
        
        for ws_key in whitespace_keys:
            # Validation might strip whitespace or reject
            try:
                client = BaseClient(ws_key, "https://example.com")
                # If it works, verify whitespace was handled
                assert client._api_key == ws_key.strip() or client._api_key == ws_key
                client.close()
            except (ValueError, TypeError):
                # Expected if validation rejects whitespace
                pass

    def test_api_key_with_only_numbers(self):
        """Test API key with only numbers"""
        numeric_key = "123456789012345678901234567890123456789"
        # This might be valid or invalid - test it doesn't crash
        try:
            client = BaseClient(numeric_key, "https://example.com")
            client.close()
        except (ValueError, TypeError):
            pass

    def test_api_key_with_only_letters(self):
        """Test API key with only letters"""
        letter_key = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # This might be valid or invalid - test it doesn't crash
        try:
            client = BaseClient(letter_key, "https://example.com")
            client.close()
        except (ValueError, TypeError):
            pass

    def test_api_key_with_mixed_case(self):
        """Test API key with mixed case"""
        mixed_key = "TestKey123456789012345678901234567890"
        # Mixed case should be fine
        try:
            client = BaseClient(mixed_key, "https://example.com")
            client.close()
        except (ValueError, TypeError):
            pass

    def test_api_key_with_very_long_string(self):
        """Test API key that is very long"""
        # Very long key (1000+ characters)
        long_key = "a" * 1000
        try:
            client = BaseClient(long_key, "https://example.com")
            client.close()
        except (ValueError, TypeError):
            # Might be rejected if there's a max length
            pass

    def test_api_key_with_null_bytes(self):
        """Test API key with null bytes"""
        null_key = "test_key\0invalid"
        with pytest.raises((ValueError, TypeError)):
            BaseClient(null_key, "https://example.com")

    def test_api_key_with_control_characters(self):
        """Test API key with control characters"""
        control_chars = [
            "\x00",  # NULL
            "\x01",  # SOH
            "\x1F",  # Unit separator
            "\x7F",  # DEL
        ]
        
        for control_char in control_chars:
            invalid_key = f"test_key{control_char}invalid"
            with pytest.raises((ValueError, TypeError)):
                BaseClient(invalid_key, "https://example.com")

    def test_routes_client_invalid_api_key(self):
        """Test RoutesClient with invalid API key formats"""
        invalid_keys = ["", "   ", "\t", "short"]
        
        for invalid_key in invalid_keys:
            with pytest.raises((ValueError, TypeError)):
                RoutesClient(invalid_key)

    def test_directions_client_invalid_api_key(self):
        """Test DirectionsClient with invalid API key formats"""
        invalid_keys = ["", "   ", "\t", "short"]
        
        for invalid_key in invalid_keys:
            with pytest.raises((ValueError, TypeError)):
                DirectionsClient(invalid_key)

    def test_roads_client_invalid_api_key(self):
        """Test RoadsClient with invalid API key formats"""
        invalid_keys = ["", "   ", "\t", "short"]
        
        for invalid_key in invalid_keys:
            with pytest.raises((ValueError, TypeError)):
                RoadsClient(invalid_key)

    def test_google_maps_client_invalid_api_key(self):
        """Test GoogleMapsClient with invalid API key formats"""
        invalid_keys = ["", "   ", "\t", "short"]
        
        for invalid_key in invalid_keys:
            with pytest.raises((ValueError, TypeError)):
                GoogleMapsClient(invalid_key)

    def test_api_key_with_quotes(self):
        """Test API key with quotes"""
        quote_keys = [
            '"test_key_12345678901234567890"',
            "'test_key_12345678901234567890'",
            "test_key_'12345678901234567890'",
        ]
        
        for quote_key in quote_keys:
            # Quotes might be part of the key or invalid
            try:
                client = BaseClient(quote_key, "https://example.com")
                client.close()
            except (ValueError, TypeError):
                pass

    def test_api_key_with_backslashes(self):
        """Test API key with backslashes"""
        backslash_key = "test_key\\12345678901234567890"
        try:
            client = BaseClient(backslash_key, "https://example.com")
            client.close()
        except (ValueError, TypeError):
            pass

    def test_api_key_with_forward_slashes(self):
        """Test API key with forward slashes"""
        slash_key = "test/key/12345678901234567890"
        try:
            client = BaseClient(slash_key, "https://example.com")
            client.close()
        except (ValueError, TypeError):
            pass

    def test_api_key_with_spaces_in_middle(self):
        """Test API key with spaces in the middle"""
        space_key = "test key 12345678901234567890"
        # Spaces in middle might be invalid
        try:
            client = BaseClient(space_key, "https://example.com")
            client.close()
        except (ValueError, TypeError):
            # Expected - spaces likely invalid
            pass

    def test_api_key_type_validation(self):
        """Test API key type validation"""
        # Test non-string types
        with pytest.raises(TypeError):
            BaseClient(123, "https://example.com")
        
        with pytest.raises(TypeError):
            BaseClient([], "https://example.com")
        
        with pytest.raises(TypeError):
            BaseClient({}, "https://example.com")
        
        with pytest.raises(TypeError):
            BaseClient(True, "https://example.com")
        
        with pytest.raises(TypeError):
            BaseClient(object(), "https://example.com")

    def test_api_key_validation_consistency(self):
        """Test that API key validation is consistent across clients"""
        invalid_keys = ["", "   ", None]
        
        for invalid_key in invalid_keys:
            # All clients should reject the same invalid keys
            for client_class in [BaseClient, RoutesClient, DirectionsClient, RoadsClient]:
                try:
                    if invalid_key is None:
                        with pytest.raises(TypeError):
                            client_class(invalid_key, "https://example.com")
                    else:
                        with pytest.raises(ValueError):
                            client_class(invalid_key, "https://example.com")
                except Exception:
                    # If client doesn't take base_url, try without it
                    try:
                        if invalid_key is None:
                            with pytest.raises(TypeError):
                                client_class(invalid_key)
                        else:
                            with pytest.raises(ValueError):
                                client_class(invalid_key)
                    except Exception:
                        pass
