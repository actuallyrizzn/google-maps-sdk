"""
Unit tests for __main__.py CLI module
"""

import pytest
import sys
from unittest.mock import patch
from io import StringIO


@pytest.mark.unit
class TestMainModule:
    """Test __main__.py CLI functionality"""

    def test_main_version(self):
        """Test --version flag"""
        from google_maps_sdk.__main__ import main
        
        with patch("sys.argv", ["google_maps_sdk", "--version"]):
            with patch("sys.exit") as mock_exit:
                with patch("sys.stdout", new=StringIO()):
                    try:
                        main()
                    except SystemExit:
                        pass
                    # argparse version action calls sys.exit(0)
                    assert mock_exit.called
                    assert mock_exit.call_args[0][0] == 0

    def test_main_with_api_key(self):
        """Test --api-key flag"""
        from google_maps_sdk.__main__ import main
        
        with patch("sys.argv", ["google_maps_sdk", "--api-key", "test_key_12345"]):
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "API key provided" in output
                assert "test_key_12345"[:10] in output
                assert "Use the SDK in your Python code" in output

    def test_main_no_args(self):
        """Test main with no arguments (shows help)"""
        from google_maps_sdk.__main__ import main
        
        with patch("sys.argv", ["google_maps_sdk"]):
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "Google Maps Platform Python SDK" in output
                assert "--version" in output
                assert "--api-key" in output

    def test_main_help(self):
        """Test --help flag"""
        from google_maps_sdk.__main__ import main
        
        with patch("sys.argv", ["google_maps_sdk", "--help"]):
            with patch("sys.exit") as mock_exit:
                with patch("sys.stdout", new=StringIO()) as mock_stdout:
                    try:
                        main()
                    except SystemExit:
                        pass
                    output = mock_stdout.getvalue()
                    assert "Google Maps Platform Python SDK" in output
                    # argparse help action calls sys.exit(0)
                    assert mock_exit.called
                    assert mock_exit.call_args[0][0] == 0

    def test_main_module_entry_point(self):
        """Test that main can be called directly"""
        from google_maps_sdk.__main__ import main
        
        # Should not raise any exceptions
        with patch("sys.argv", ["google_maps_sdk"]):
            with patch("sys.stdout", new=StringIO()):
                main()

    def test_main_api_key_truncation(self):
        """Test that API key is truncated in output"""
        from google_maps_sdk.__main__ import main
        
        with patch("sys.argv", ["google_maps_sdk", "--api-key", "very_long_api_key_that_should_be_truncated"]):
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                # Should show first 10 characters
                assert "very_long_" in output
                assert "..." in output

    def test_main_module_entry_point_if_name_main(self):
        """Test that __main__ block executes when __name__ == '__main__'"""
        import runpy
        
        # Use runpy to execute the module as if it were run with -m
        # This will trigger the if __name__ == "__main__" block
        with patch("sys.argv", ["google_maps_sdk"]):
            with patch("sys.stdout", new=StringIO()):
                # This executes the module and triggers the if __name__ == "__main__" block
                runpy.run_module("google_maps_sdk.__main__", run_name="__main__")
