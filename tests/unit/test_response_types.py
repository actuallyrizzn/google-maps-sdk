"""
Unit tests for response types (issue #29)
"""

import pytest
from google_maps_sdk.response_types import XMLResponse, NonJSONResponse
import xml.etree.ElementTree as ET


@pytest.mark.unit
class TestXMLResponse:
    """Test XMLResponse class"""

    def test_xml_response_init(self):
        """Test XMLResponse initialization"""
        xml_text = "<root><item>value</item></root>"
        response = XMLResponse(xml_text, status_code=200)
        
        assert response.xml == xml_text
        assert response.status_code == 200
        assert response._parsed is None

    def test_xml_response_parsed(self):
        """Test XML parsing"""
        xml_text = "<root><item>value</item></root>"
        response = XMLResponse(xml_text)
        
        parsed = response.parsed
        assert parsed is not None
        assert parsed.tag == "root"
        assert len(parsed) == 1
        assert parsed[0].tag == "item"
        assert parsed[0].text == "value"

    def test_xml_response_invalid(self):
        """Test XMLResponse with invalid XML"""
        xml_text = "<root><unclosed>"
        response = XMLResponse(xml_text)
        
        with pytest.raises(ValueError, match="Invalid XML"):
            _ = response.parsed

    def test_xml_response_to_dict(self):
        """Test XML to dictionary conversion"""
        xml_text = "<root><item>value</item><item>value2</item></root>"
        response = XMLResponse(xml_text)
        
        result = response.to_dict()
        # The root element's children become the top-level dict
        assert "item" in result
        assert isinstance(result["item"], list)
        assert len(result["item"]) == 2
        assert result["item"][0] == "value"
        assert result["item"][1] == "value2"


@pytest.mark.unit
class TestNonJSONResponse:
    """Test NonJSONResponse class"""

    def test_non_json_response_init(self):
        """Test NonJSONResponse initialization"""
        text = "Plain text response"
        response = NonJSONResponse(text, content_type="text/plain", status_code=200)
        
        assert response.text == text
        assert response.content_type == "text/plain"
        assert response.status_code == 200

    def test_non_json_response_to_dict(self):
        """Test NonJSONResponse to_dict"""
        text = "Plain text response"
        response = NonJSONResponse(text, content_type="text/plain")
        
        result = response.to_dict()
        assert result["status"] == "OK"
        assert result["content_type"] == "text/plain"
        assert result["text"] == text
        assert result["raw"] == text

    def test_non_json_response_repr(self):
        """Test NonJSONResponse string representation"""
        response = NonJSONResponse("test", "text/plain", 200)
        repr_str = repr(response)
        assert "NonJSONResponse" in repr_str
        assert "200" in repr_str
        assert "text/plain" in repr_str
