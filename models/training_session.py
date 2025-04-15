"""
VolleyStat Lite - Training Session Model
This module implements the Factory Method pattern for training sessions.
"""

from abc import ABC, abstractmethod

class TrainingSessionFactory:
    """Factory Method Pattern for creating different training session types."""
    @staticmethod
    def create_session(session_type, **kwargs):
        """
        Creates and returns a specific type of training session based on the session_type.
        
        Args:
            session_type (str): Type of training session to create
            **kwargs: Additional parameters needed for the specific session type
            
        Returns:
            TrainingSession: An instance of the appropriate training session subclass
        """
        if session_type.lower() == "serving":
            return ServingSession(**kwargs)
        elif session_type.lower() == "attacking":
            return AttackingSession(**kwargs)
        elif session_type.lower() == "blocking":
            return BlockingSession(**kwargs)
        else:
            raise ValueError(f"Unknown training session type: {session_type}")

class TrainingSession(ABC):
    """Abstract base class for all training sessions."""
    def __init__(self, date, players, duration):
        self.date = date
        self.players = players
        self.duration = duration
        self.stats = {}
        
    @abstractmethod
    def calculate_efficiency(self):
        """Calculate session efficiency metrics."""
        pass
    
    @abstractmethod
    def get_session_type(self):
        """Return the type of session."""
        pass
    
    def add_player_stat(self, player_id, stat_name, value):
        """Add a statistic for a player."""
        if player_id not in self.stats:
            self.stats[player_id] = {}
        self.stats[player_id][stat_name] = value

class ServingSession(TrainingSession):
    """Specific implementation for serving practice sessions."""
    def __init__(self, date, players, duration, target_zones=None):
        super().__init__(date, players, duration)
        self.target_zones = target_zones or ["Zone 1", "Zone 5", "Zone 6"]
        
    def calculate_efficiency(self):
        """Calculate serving efficiency."""
        total_attempts = sum(stats.get("attempts", 0) for stats in self.stats.values())
        total_aces = sum(stats.get("aces", 0) for stats in self.stats.values())
        
        if total_attempts == 0:
            return 0
        return (total_aces / total_attempts) * 100
    
    def get_session_type(self):
        return "serving"

class AttackingSession(TrainingSession):
    """Specific implementation for attacking practice sessions."""
    def __init__(self, date, players, duration, positions=None):
        super().__init__(date, players, duration)
        self.positions = positions or ["Position 2", "Position 4"]
        
    def calculate_efficiency(self):
        """Calculate hitting efficiency."""
        total_attempts = sum(stats.get("attempts", 0) for stats in self.stats.values())
        total_kills = sum(stats.get("kills", 0) for stats in self.stats.values())
        total_errors = sum(stats.get("errors", 0) for stats in self.stats.values())
        
        if total_attempts == 0:
            return 0
        return ((total_kills - total_errors) / total_attempts) * 100
    
    def get_session_type(self):
        return "attacking"

class BlockingSession(TrainingSession):
    """Specific implementation for blocking practice sessions."""
    def __init__(self, date, players, duration, block_types=None):
        super().__init__(date, players, duration)
        self.block_types = block_types or ["Solo", "Double"]
        
    def calculate_efficiency(self):
        """Calculate blocking efficiency."""
        total_attempts = sum(stats.get("attempts", 0) for stats in self.stats.values())
        total_blocks = sum(stats.get("blocks", 0) for stats in self.stats.values())
        
        if total_attempts == 0:
            return 0
        return (total_blocks / total_attempts) * 100
    
    def get_session_type(self):
        return "blocking"