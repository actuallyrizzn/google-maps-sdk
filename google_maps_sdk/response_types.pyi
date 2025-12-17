"""
Type stubs for response_types module (issue #46)
"""

from typing import Dict, Any

class XMLResponse:
    text: str
    status_code: int
    
    def __init__(self, text: str, status_code: int = ...) -> None: ...
    @property
    def parsed(self) -> Any: ...
    def to_dict(self) -> Dict[str, Any]: ...

class NonJSONResponse:
    text: str
    content_type: str
    status_code: int
    
    def __init__(
        self,
        text: str,
        content_type: str = ...,
        status_code: int = ...,
    ) -> None: ...
    def to_dict(self) -> Dict[str, Any]: ...
