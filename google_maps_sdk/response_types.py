"""
Response type classes for different response formats (issue #29)
"""

from typing import Optional, Dict, Any
import xml.etree.ElementTree as ET


class XMLResponse:
    """
    Response wrapper for XML responses (issue #29)
    
    Provides structured access to XML response data.
    """
    
    def __init__(self, xml_text: str, status_code: int = 200):
        """
        Initialize XML response
        
        Args:
            xml_text: Raw XML text
            status_code: HTTP status code
        """
        self.xml = xml_text
        self.status_code = status_code
        self._parsed: Optional[ET.Element] = None
    
    @property
    def parsed(self) -> ET.Element:
        """
        Parse XML and return ElementTree Element
        
        Returns:
            Parsed XML ElementTree Element
            
        Raises:
            ValueError: If XML is invalid
        """
        if self._parsed is None:
            try:
                self._parsed = ET.fromstring(self.xml)
            except ET.ParseError as e:
                raise ValueError(f"Invalid XML response: {e}") from e
        return self._parsed
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert XML to dictionary representation
        
        Returns:
            Dictionary representation of XML
        """
        def element_to_dict(element: ET.Element) -> Dict[str, Any]:
            result = {}
            if element.attrib:
                result['@attributes'] = element.attrib
            if element.text and element.text.strip():
                if len(element) == 0:
                    return element.text.strip()
                result['#text'] = element.text.strip()
            for child in element:
                child_dict = element_to_dict(child)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = child_dict
            return result if result else None
        
        return element_to_dict(self.parsed)
    
    def __repr__(self) -> str:
        return f"XMLResponse(status_code={self.status_code}, xml_length={len(self.xml)})"


class NonJSONResponse:
    """
    Response wrapper for non-JSON responses (issue #29)
    
    Handles responses that are not JSON (e.g., plain text, HTML, etc.)
    """
    
    def __init__(self, text: str, content_type: Optional[str] = None, status_code: int = 200):
        """
        Initialize non-JSON response
        
        Args:
            text: Response text
            content_type: Content-Type header value
            status_code: HTTP status code
        """
        self.text = text
        self.content_type = content_type
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format for consistency
        
        Returns:
            Dictionary with response data
        """
        return {
            "status": "OK",
            "content_type": self.content_type,
            "text": self.text,
            "raw": self.text
        }
    
    def __repr__(self) -> str:
        return f"NonJSONResponse(status_code={self.status_code}, content_type={self.content_type}, text_length={len(self.text)})"
