"""
VolleyStat Lite - Observer Pattern Implementation
This module implements the Observer pattern for notifications.
"""

from abc import ABC, abstractmethod

class Subject:
    """Subject interface for the Observer pattern."""
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        """Add an observer to the subscription."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        """Remove an observer from the subscription."""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self, message):
        """Notify all observers with the given message."""
        for observer in self._observers:
            observer.update(message)

class Observer(ABC):
    """Observer interface for the Observer pattern."""
    @abstractmethod
    def update(self, message):
        """Receive update from subject."""
        pass

class Coach(Observer):
    """Coach observer implementation."""
    def __init__(self, name):
        self.name = name
    
    def update(self, message):
        print(f"Coach {self.name} received notification: {message}")

class Player(Observer):
    """Player observer implementation."""
    def __init__(self, name, position):
        self.name = name
        self.position = position
    
    def update(self, message):
        print(f"Player {self.name} ({self.position}) received notification: {message}")

class TeamAnalyst(Observer):
    """Team Analyst observer implementation."""
    def __init__(self, name):
        self.name = name
    
    def update(self, message):
        print(f"Analyst {self.name} received notification: {message}")