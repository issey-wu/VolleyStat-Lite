"""
VolleyStat Lite - Base Adapter
This module defines the base adapter interface for third-party services.
"""

from abc import ABC, abstractmethod

class ThirdPartyAdapter(ABC):
    """Abstract adapter for third-party services."""
    @abstractmethod
    def connect(self):
        """Establish connection to the third-party service."""
        pass
    
    @abstractmethod
    def read_data(self, identifier):
        """Read data from the third-party service."""
        pass
    
    @abstractmethod
    def write_data(self, identifier, data):
        """Write data to the third-party service."""
        pass