"""
VolleyStat Lite - Volleyball Performance Tracking System
Author: Issey Wu (400387909)
Date: April 8, 2025

This application tracks volleyball team and player performance, provides insights,
and integrates with PostgreSQL database and Google Sheets API.
"""

import os
import psycopg2
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import statistics
from abc import ABC, abstractmethod

# Design Pattern 1: Factory Method Pattern
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

# Design Pattern 2: Observer Pattern
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

# Design Pattern 3: Adapter Pattern
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

class GoogleSheetsAdapter(ThirdPartyAdapter):
    """Adapter for Google Sheets API."""
    def __init__(self, credentials_file, scopes=None):
        self.credentials_file = credentials_file
        self.scopes = scopes or ['https://www.googleapis.com/auth/spreadsheets']
        self.service = None
    
    def connect(self):
        """Connect to Google Sheets API."""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.scopes
            )
            self.service = build('sheets', 'v4', credentials=creds)
            return True
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            return False
    
    def read_data(self, spreadsheet_id, range_name="Sheet1!A1:Z1000"):
        """Read data from a Google Sheet."""
        if not self.service:
            if not self.connect():
                return None
                
        try:
            sheet = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            return sheet.get('values', [])
        except Exception as e:
            print(f"Error reading from Google Sheets: {e}")
            return None
    
    def write_data(self, spreadsheet_id, range_name, data):
        """Write data to a Google Sheet."""
        if not self.service:
            if not self.connect():
                return False
                
        try:
            body = {
                'values': data
            }
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return result.get('updatedCells', 0) > 0
        except Exception as e:
            print(f"Error writing to Google Sheets: {e}")
            return False

class PostgresAdapter(ThirdPartyAdapter):
    """Adapter for PostgreSQL database."""
    def __init__(self, host, dbname, user, password, port="5432"):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False
    
    def read_data(self, query, params=None):
        """Execute a SELECT query and return results."""
        if not self.conn or not self.cursor:
            if not self.connect():
                return None
                
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error reading from PostgreSQL: {e}")
            return None
    
    def write_data(self, query, params=None):
        """Execute an INSERT/UPDATE/DELETE query."""
        if not self.conn or not self.cursor:
            if not self.connect():
                return False
                
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error writing to PostgreSQL: {e}")
            self.conn.rollback()
            return False
    
    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

class VolleyStatSystem(Subject):
    """Main class for the VolleyStat Lite system."""
    def __init__(self, db_adapter, sheets_adapter=None):
        super().__init__()
        self.db_adapter = db_adapter
        self.sheets_adapter = sheets_adapter
        self.initialize_database()
    
    def initialize_database(self):
        """Set up the database tables if they don't exist."""
        # Create players table
        self.db_adapter.write_data("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                position VARCHAR(50),
                team_id INTEGER
            );
        """)
        
        # Create teams table
        self.db_adapter.write_data("""
            CREATE TABLE IF NOT EXISTS teams (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
        """)
        
        # Create matches table
        self.db_adapter.write_data("""
            CREATE TABLE IF NOT EXISTS matches (
                id SERIAL PRIMARY KEY,
                team_id INTEGER,
                opponent VARCHAR(100),
                match_date DATE,
                sets_won INTEGER,
                sets_lost INTEGER,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            );
        """)
        
        # Create player_stats table
        self.db_adapter.write_data("""
            CREATE TABLE IF NOT EXISTS player_stats (
                id SERIAL PRIMARY KEY,
                player_id INTEGER,
                match_id INTEGER,
                attacks INTEGER,
                kills INTEGER,
                errors INTEGER,
                blocks INTEGER,
                digs INTEGER,
                aces INTEGER,
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (match_id) REFERENCES matches(id)
            );
        """)
        
        # Create training_sessions table
        self.db_adapter.write_data("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                id SERIAL PRIMARY KEY,
                team_id INTEGER,
                session_type VARCHAR(50),
                session_date DATE,
                duration INTEGER,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            );
        """)
    
    def add_team(self, name):
        """Add a new team to the database."""
        query = "INSERT INTO teams (name) VALUES (%s) RETURNING id;"
        result = self.db_adapter.read_data(query, (name,))
        
        if result:
            team_id = result[0][0]
            self.notify(f"New team added: {name} (ID: {team_id})")
            return team_id
        return None
    
    def add_player(self, name, position, team_id):
        """Add a new player to the database."""
        query = "INSERT INTO players (name, position, team_id) VALUES (%s, %s, %s) RETURNING id;"
        result = self.db_adapter.read_data(query, (name, position, team_id))
        
        if result:
            player_id = result[0][0]
            self.notify(f"New player added: {name} ({position}) to team {team_id}")
            return player_id
        return None
    
    def record_match(self, team_id, opponent, match_date, sets_won, sets_lost):
        """Record a match in the database."""
        query = """
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        result = self.db_adapter.read_data(
            query, (team_id, opponent, match_date, sets_won, sets_lost)
        )
        
        if result:
            match_id = result[0][0]
            self.notify(f"New match recorded: against {opponent} on {match_date}")
            return match_id
        return None
    
    def record_player_stats(self, player_id, match_id, attacks, kills, errors, blocks, digs, aces):
        """Record player statistics for a match."""
        query = """
            INSERT INTO player_stats (player_id, match_id, attacks, kills, errors, blocks, digs, aces)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        result = self.db_adapter.read_data(
            query, (player_id, match_id, attacks, kills, errors, blocks, digs, aces)
        )
        
        if result:
            stat_id = result[0][0]
            self.notify(f"Player stats recorded for player {player_id} in match {match_id}")
            return stat_id
        return None
    
    def record_training_session(self, team_id, session_type, session_date, duration):
        """Record a training session in the database."""
        query = """
            INSERT INTO training_sessions (team_id, session_type, session_date, duration)
            VALUES (%s, %s, %s, %s) RETURNING id;
        """
        result = self.db_adapter.read_data(
            query, (team_id, session_type, session_date, duration)
        )
        
        if result:
            session_id = result[0][0]
            self.notify(f"New {session_type} training session recorded on {session_date}")
            return session_id
        return None
    
    def get_player_stats(self, player_id):
        """Get all stats for a player."""
        query = """
            SELECT ps.*, m.opponent, m.match_date
            FROM player_stats ps
            JOIN matches m ON ps.match_id = m.id
            WHERE ps.player_id = %s
            ORDER BY m.match_date DESC;
        """
        return self.db_adapter.read_data(query, (player_id,))
    
    def get_team_stats(self, team_id):
        """Get all match stats for a team."""
        query = """
            SELECT * FROM matches
            WHERE team_id = %s
            ORDER BY match_date DESC;
        """
        return self.db_adapter.read_data(query, (team_id,))
    
    def get_player_performance_metrics(self, player_id):
        """Calculate performance metrics for a player."""
        stats = self.get_player_stats(player_id)
        
        if not stats:
            return {
                "attacking_efficiency": 0,
                "blocking_average": 0,
                "serving_aces": 0
            }
        
        total_attacks = sum(stat[3] for stat in stats if stat[3] is not None)
        total_kills = sum(stat[4] for stat in stats if stat[4] is not None)
        total_errors = sum(stat[5] for stat in stats if stat[5] is not None)
        total_blocks = sum(stat[6] for stat in stats if stat[6] is not None)
        total_aces = sum(stat[8] for stat in stats if stat[8] is not None)
        
        attacking_efficiency = 0
        if total_attacks > 0:
            attacking_efficiency = ((total_kills - total_errors) / total_attacks) * 100
        
        blocking_average = 0
        if len(stats) > 0:
            blocking_average = total_blocks / len(stats)
        
        return {
            "attacking_efficiency": round(attacking_efficiency, 2),
            "blocking_average": round(blocking_average, 2),
            "serving_aces": total_aces
        }
    
    def get_team_performance_metrics(self, team_id):
        """Calculate performance metrics for a team."""
        matches = self.get_team_stats(team_id)
        
        if not matches:
            return {
                "matches_played": 0,
                "matches_won": 0,
                "win_percentage": 0,
                "set_win_percentage": 0
            }
        
        matches_played = len(matches)
        matches_won = sum(1 for match in matches if match[4] > match[5])
        total_sets_played = sum(match[4] + match[5] for match in matches)
        total_sets_won = sum(match[4] for match in matches)
        
        win_percentage = (matches_won / matches_played) * 100
        set_win_percentage = 0
        if total_sets_played > 0:
            set_win_percentage = (total_sets_won / total_sets_played) * 100
        
        return {
            "matches_played": matches_played,
            "matches_won": matches_won,
            "win_percentage": round(win_percentage, 2),
            "set_win_percentage": round(set_win_percentage, 2)
        }
    
    def generate_player_report(self, player_id):
        """Generate a report for a player."""
        # Get player info
        player_query = "SELECT name, position FROM players WHERE id = %s;"
        player_info = self.db_adapter.read_data(player_query, (player_id,))
        
        if not player_info:
            print("Player not found.")
            return
        
        player_name, player_position = player_info[0]
        
        # Get player metrics
        metrics = self.get_player_performance_metrics(player_id)
        
        # Get player stats for last 5 matches
        stats_query = """
            SELECT ps.*, m.opponent, m.match_date
            FROM player_stats ps
            JOIN matches m ON ps.match_id = m.id
            WHERE ps.player_id = %s
            ORDER BY m.match_date DESC
            LIMIT 5;
        """
        recent_stats = self.db_adapter.read_data(stats_query, (player_id,))
        
        # Print report
        print("\n" + "=" * 50)
        print(f"PLAYER REPORT: {player_name} ({player_position})")
        print("=" * 50)
        print("\nPERFORMANCE METRICS:")
        print(f"Attacking Efficiency: {metrics['attacking_efficiency']}%")
        print(f"Blocking Average: {metrics['blocking_average']} blocks per match")
        print(f"Total Serving Aces: {metrics['serving_aces']}")
        
        print("\nRECENT MATCH STATISTICS:")
        if recent_stats:
            for stat in recent_stats:
                print(f"\nMatch against {stat[10]} on {stat[11]}")
                print(f"Attacks: {stat[3]} | Kills: {stat[4]} | Errors: {stat[5]}")
                print(f"Blocks: {stat[6]} | Digs: {stat[7]} | Aces: {stat[8]}")
        else:
            print("No recent matches found.")
        
        print("\nTRAINING RECOMMENDATIONS:")
        if metrics['attacking_efficiency'] < 20:
            print("- Focus on attacking accuracy and shot selection")
        if metrics['blocking_average'] < 1:
            print("- Work on blocking technique and timing")
        if metrics['serving_aces'] < 3:
            print("- Practice aggressive serving with targeting")
        
        print("=" * 50 + "\n")
        
        # Export to Google Sheets if adapter is available
        if self.sheets_adapter:
            sheet_data = [
                ["PLAYER REPORT", player_name, player_position],
                [],
                ["PERFORMANCE METRICS"],
                ["Attacking Efficiency", f"{metrics['attacking_efficiency']}%"],
                ["Blocking Average", f"{metrics['blocking_average']} blocks per match"],
                ["Total Serving Aces", str(metrics['serving_aces'])],
                [],
                ["RECENT MATCH STATISTICS"]
            ]
            
            if recent_stats:
                sheet_data.append(["Date", "Opponent", "Attacks", "Kills", "Errors", "Blocks", "Digs", "Aces"])
                for stat in recent_stats:
                    sheet_data.append([
                        stat[11], stat[10], stat[3], stat[4], stat[5], stat[6], stat[7], stat[8]
                    ])
            
            sheet_data.extend([
                [],
                ["TRAINING RECOMMENDATIONS"]
            ])
            
            if metrics['attacking_efficiency'] < 20:
                sheet_data.append(["Focus on attacking accuracy and shot selection"])
            if metrics['blocking_average'] < 1:
                sheet_data.append(["Work on blocking technique and timing"])
            if metrics['serving_aces'] < 3:
                sheet_data.append(["Practice aggressive serving with targeting"])
            
            # Export to Google Sheets
            self.export_to_sheets("Player Reports", f"Player_{player_id}!A1", sheet_data)
    
    def generate_team_report(self, team_id):
        """Generate a report for a team."""
        # Get team info
        team_query = "SELECT name FROM teams WHERE id = %s;"
        team_info = self.db_adapter.read_data(team_query, (team_id,))
        
        if not team_info:
            print("Team not found.")
            return
        
        team_name = team_info[0][0]
        
        # Get team metrics
        metrics = self.get_team_performance_metrics(team_id)
        
        # Get team's recent matches
        matches_query = """
            SELECT * FROM matches
            WHERE team_id = %s
            ORDER BY match_date DESC
            LIMIT 5;
        """
        recent_matches = self.db_adapter.read_data(matches_query, (team_id,))
        
        # Get team's top performers
        top_performers_query = """
            SELECT p.name, p.position, 
                   SUM(ps.kills) as total_kills,
                   SUM(ps.blocks) as total_blocks,
                   SUM(ps.aces) as total_aces
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.id
            JOIN matches m ON ps.match_id = m.id
            WHERE p.team_id = %s
            GROUP BY p.id, p.name, p.position
            ORDER BY total_kills DESC
            LIMIT 3;
        """
        top_performers = self.db_adapter.read_data(top_performers_query, (team_id,))
        
        # Print report
        print("\n" + "=" * 50)
        print(f"TEAM REPORT: {team_name}")
        print("=" * 50)
        print("\nPERFORMANCE METRICS:")
        print(f"Matches Played: {metrics['matches_played']}")
        print(f"Matches Won: {metrics['matches_won']}")
        print(f"Win Percentage: {metrics['win_percentage']}%")
        print(f"Set Win Percentage: {metrics['set_win_percentage']}%")
        
        print("\nRECENT MATCHES:")
        if recent_matches:
            for match in recent_matches:
                result = "Won" if match[4] > match[5] else "Lost"
                print(f"{match[3]} vs {match[2]}: {result} ({match[4]}-{match[5]})")
        else:
            print("No recent matches found.")
        
        print("\nTOP PERFORMERS:")
        if top_performers:
            for i, player in enumerate(top_performers, 1):
                print(f"{i}. {player[0]} ({player[1]}) - Kills: {player[2]}, Blocks: {player[3]}, Aces: {player[4]}")
        else:
            print("No player statistics available.")
        
        print("\nTEAM RECOMMENDATIONS:")
        if metrics['win_percentage'] < 50:
            print("- Focus on overall team cohesion and communication")
        if metrics['set_win_percentage'] < 40:
            print("- Work on closing out sets and maintaining consistency")
        
        print("=" * 50 + "\n")
        
        # Export to Google Sheets if adapter is available
        if self.sheets_adapter:
            sheet_data = [
                ["TEAM REPORT", team_name],
                [],
                ["PERFORMANCE METRICS"],
                ["Matches Played", str(metrics['matches_played'])],
                ["Matches Won", str(metrics['matches_won'])],
                ["Win Percentage", f"{metrics['win_percentage']}%"],
                ["Set Win Percentage", f"{metrics['set_win_percentage']}%"],
                [],
                ["RECENT MATCHES"]
            ]
            
            if recent_matches:
                sheet_data.append(["Date", "Opponent", "Sets Won", "Sets Lost", "Result"])
                for match in recent_matches:
                    result = "Won" if match[4] > match[5] else "Lost"
                    sheet_data.append([
                        match[3], match[2], match[4], match[5], result
                    ])
            
            sheet_data.extend([
                [],
                ["TOP PERFORMERS"]
            ])
            
            if top_performers:
                sheet_data.append(["Name", "Position", "Total Kills", "Total Blocks", "Total Aces"])
                for player in top_performers:
                    sheet_data.append([
                        player[0], player[1], player[2], player[3], player[4]
                    ])
            
            sheet_data.extend([
                [],
                ["TEAM RECOMMENDATIONS"]
            ])
            
            if metrics['win_percentage'] < 50:
                sheet_data.append(["Focus on overall team cohesion and communication"])
            if metrics['set_win_percentage'] < 40:
                sheet_data.append(["Work on closing out sets and maintaining consistency"])
            
            # Export to Google Sheets
            self.export_to_sheets("Team Reports", f"Team_{team_id}!A1", sheet_data)
    
    def generate_training_recommendation(self, player_id=None, team_id=None):
        """Generate training recommendations based on performance data."""
        if player_id:
            # Get player info
            player_query = "SELECT name, position FROM players WHERE id = %s;"
            player_info = self.db_adapter.read_data(player_query, (player_id,))
            
            if not player_info:
                print("Player not found.")
                return
            
            player_name, player_position = player_info[0]
            
            # Get player metrics
            metrics = self.get_player_performance_metrics(player_id)
            
            # Determine weakest area
            areas = {
                "Attacking": metrics['attacking_efficiency'],
                "Blocking": metrics['blocking_average'] * 25,  # Scale to make comparable
                "Serving": metrics['serving_aces'] * 10  # Scale to make comparable
            }
            
            weakest_area = min(areas, key=areas.get)
            
            # Generate recommendation
            print("\n" + "=" * 50)
            print(f"TRAINING RECOMMENDATION FOR: {player_name} ({player_position})")
            print("=" * 50)
            print(f"\nWeakest category identified: {weakest_area}")
            
            if weakest_area == "Attacking":
                print("\nRecommended training focus:")
                print("1. Attacking precision exercises")
                print("2. Shot selection drills")
                print("3. Approach and timing practice")
                
                print("\nSpecific drills:")
                print("- Target hitting: Set up targets in different court positions")
                print("- Line vs cross shots: Practice both attack angles")
                print("- Quick attacks: Work on faster approaches and connection with setter")
            
            elif weakest_area == "Blocking":
                print("\nRecommended training focus:")
                print("1. Blocking positioning and footwork")
                print("2. Reading the opposing hitter")
                print("3. Block timing exercises")
                
                print("\nSpecific drills:")
                print("- Shadow blocking: Follow the attacker's movement without the ball")
                print("- Reaction drills: Quick lateral movement across the net")
                print("- Block touch training: Focus on proper hand position and penetration")
            
            else:  # Serving
                print("\nRecommended training focus:")
                print("1. Serve accuracy and consistency")
                print("2. Strategic serving to target zones")
                print("3. Adding more power or movement to serves")
                
                print("\nSpecific drills:")
                print("- Zone serving: Target specific areas of the court")
                print("- Pressure serving: Consecutive successful serves under pressure")
                print("- Service variation: Practice different types of serves")
            
            print("=" * 50 + "\n")
        
        elif team_id:
            # Get team info
            team_query = "SELECT name FROM teams WHERE id = %s;"
            team_info = self.db_adapter.read_data(team_query, (team_id,))
            
            if not team_info:
                print("Team not found.")
                return
            
            team_name = team_info[0][0]
            
            # Get team metrics
            metrics = self.get_team_performance_metrics(team_id)
            
            # Analyze team strengths and weaknesses
            matches = self.get_team_stats(team_id)
            
            total_sets_played = sum(match[4] + match[5] for match in matches)
            close_sets_lost = sum(1 for match in matches if match[5] > 0 and match[4] + 1 >= match[5])
            
            # Get team's average stats
            avg_stats_query = """
                SELECT AVG(ps.kills), AVG(ps.blocks), AVG(ps.aces), AVG(ps.digs)
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.id
                WHERE p.team_id = %s;
            """
            avg_stats = self.db_adapter.read_data(avg_stats_query, (team_id,))
            
            # Generate recommendation
            print("\n" + "=" * 50)
            print(f"TEAM TRAINING RECOMMENDATION FOR: {team_name}")
            print("=" * 50)
            
            if avg_stats and avg_stats[0][0] is not None:
                avg_kills, avg_blocks, avg_aces, avg_digs = avg_stats[0]
                
                weakest_area = min(
                    [("Attacking", avg_kills), 
                     ("Blocking", avg_blocks), 
                     ("Serving", avg_aces),
                     ("Defense", avg_digs)],
                    key=lambda x: x[1] if x[1] is not None else float('inf')
                )[0]
                
                print(f"\nTeam-wide weakness identified: {weakest_area}")
                
                if weakest_area == "Attacking":
                    print("\nRecommended team training focus:")
                    print("1. Offensive combinations and plays")
                    print("2. Setter-hitter connection drills")
                    print("3. Attack coverage exercises")
                
                elif weakest_area == "Blocking":
                    print("\nRecommended team training focus:")
                    print("1. Block timing and coordination")
                    print("2. Double block formation drills")
                    print("3. Block defense transition practice")
                
                elif weakest_area == "Serving":
                    print("\nRecommended team training focus:")
                    print("1. Targeted service practice to exploit opponent weaknesses")
                    print("2. Service pressure drills")
                    print("3. Service and reception coordination")
                
                else:  # Defense
                    print("\nRecommended team training focus:")
                    print("1. Team defense formation drills")
                    print("2. Dig to target exercises")
                    print("3. Transition from defense to offense practice")
            
            if close_sets_lost > 0 and total_sets_played > 0:
                close_set_ratio = close_sets_lost / total_sets_played
                if close_set_ratio > 0.3:
                    print("\nAdditional Focus Area: End-of-Set Performance")
                    print("Team is losing a significant number of close sets")
                    print("Recommended drills:")
                    print("1. Pressure situation training")
                    print("2. End-game scenarios (e.g., play from 20-20)")
                    print("3. Mental toughness exercises")
            
            print("=" * 50 + "\n")
    
    def export_to_sheets(self, spreadsheet_name, range_name, data):
        """Export data to Google Sheets."""
        if not self.sheets_adapter:
            print("Google Sheets adapter not available.")
            return False
        
        # For simplicity, assuming spreadsheet_name is the spreadsheet ID
        result = self.sheets_adapter.write_data(spreadsheet_name, range_name, data)
        
        if result:
            print(f"Data successfully exported to Google Sheets: {spreadsheet_name}")
            return True
        else:
            print(f"Failed to export data to Google Sheets: {spreadsheet_name}")
            return False

def main():
    """Main function to run the VolleyStat Lite application."""
    print("=" * 50)
    print("VOLLEYSTAT LITE - Volleyball Performance Tracking System")
    print("=" * 50)
    
    # Database connection details
    DB_HOST = "localhost"
    DB_NAME = "postgres"
    DB_USER = "***REMOVED***"
    DB_PASSWORD = "9055678820Iw"
    DB_PORT = "5432"
    
    # Google Sheets API details
    ***REMOVED***
    ***REMOVED***
    
    # Initialize database adapter
    db_adapter = PostgresAdapter(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    
    # Initialize Google Sheets adapter
    sheets_adapter = None
    try:
        sheets_adapter = GoogleSheetsAdapter(GOOGLE_CREDS_FILE)
        sheets_connected = sheets_adapter.connect()
        if sheets_connected:
            print("Connected to Google Sheets API.")
        else:
            print("Failed to connect to Google Sheets API. Sheet export will be unavailable.")
            sheets_adapter = None
    except Exception as e:
        print(f"Error setting up Google Sheets adapter: {e}")
        sheets_adapter = None
    
    # Initialize VolleyStat system
    system = VolleyStatSystem(db_adapter, sheets_adapter)
    
    # Create some observers
    coach = Coach("John Smith")
    player1 = Player("Michael Johnson", "Outside Hitter")
    player2 = Player("Emma Davis", "Setter")
    analyst = TeamAnalyst("Sarah Wilson")
    
    # Attach observers to the system
    system.attach(coach)
    system.attach(player1)
    system.attach(player2)
    system.attach(analyst)
    
    # Interactive menu
    while True:
        print("\nVOLLEYSTAT LITE - MAIN MENU")
        print("1. Team Management")
        print("2. Player Management")
        print("3. Match Management")
        print("4. Training Management")
        print("5. Reports and Analysis")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            # Team Management
            print("\nTEAM MANAGEMENT")
            print("1. Add Team")
            print("2. View Teams")
            print("3. Back to Main Menu")
            
            team_choice = input("\nEnter your choice (1-3): ")
            
            if team_choice == "1":
                team_name = input("Enter team name: ")
                team_id = system.add_team(team_name)
                if team_id:
                    print(f"Team added successfully with ID: {team_id}")
            
            elif team_choice == "2":
                teams = db_adapter.read_data("SELECT * FROM teams ORDER BY id;")
                if teams:
                    print("\nTEAMS:")
                    for team in teams:
                        print(f"ID: {team[0]}, Name: {team[1]}")
                else:
                    print("No teams found.")
        
        elif choice == "2":
            # Player Management
            print("\nPLAYER MANAGEMENT")
            print("1. Add Player")
            print("2. View Players")
            print("3. Back to Main Menu")
            
            player_choice = input("\nEnter your choice (1-3): ")
            
            if player_choice == "1":
                teams = db_adapter.read_data("SELECT * FROM teams ORDER BY id;")
                if not teams:
                    print("No teams available. Please add a team first.")
                    continue
                
                print("\nAvailable Teams:")
                for team in teams:
                    print(f"ID: {team[0]}, Name: {team[1]}")
                
                team_id = input("Enter team ID: ")
                player_name = input("Enter player name: ")
                player_position = input("Enter player position: ")
                
                player_id = system.add_player(player_name, player_position, team_id)
                if player_id:
                    print(f"Player added successfully with ID: {player_id}")
            
            elif player_choice == "2":
                players = db_adapter.read_data("""
                    SELECT p.id, p.name, p.position, t.name as team
                    FROM players p
                    JOIN teams t ON p.team_id = t.id
                    ORDER BY p.id;
                """)
                
                if players:
                    print("\nPLAYERS:")
                    for player in players:
                        print(f"ID: {player[0]}, Name: {player[1]}, Position: {player[2]}, Team: {player[3]}")
                else:
                    print("No players found.")
        
        elif choice == "3":
            # Match Management
            print("\nMATCH MANAGEMENT")
            print("1. Record Match")
            print("2. Record Player Stats")
            print("3. View Matches")
            print("4. Back to Main Menu")
            
            match_choice = input("\nEnter your choice (1-4): ")
            
            if match_choice == "1":
                teams = db_adapter.read_data("SELECT * FROM teams ORDER BY id;")
                if not teams:
                    print("No teams available. Please add a team first.")
                    continue
                
                print("\nAvailable Teams:")
                for team in teams:
                    print(f"ID: {team[0]}, Name: {team[1]}")
                
                team_id = input("Enter team ID: ")
                opponent = input("Enter opponent name: ")
                match_date = input("Enter match date (YYYY-MM-DD): ")
                sets_won = input("Enter sets won: ")
                sets_lost = input("Enter sets lost: ")
                
                match_id = system.record_match(team_id, opponent, match_date, sets_won, sets_lost)
                if match_id:
                    print(f"Match recorded successfully with ID: {match_id}")
            
            elif match_choice == "2":
                matches = db_adapter.read_data("""
                    SELECT m.id, t.name, m.opponent, m.match_date
                    FROM matches m
                    JOIN teams t ON m.team_id = t.id
                    ORDER BY m.match_date DESC;
                """)
                
                if not matches:
                    print("No matches available. Please record a match first.")
                    continue
                
                print("\nAvailable Matches:")
                for match in matches:
                    print(f"ID: {match[0]}, Team: {match[1]} vs {match[2]} on {match[3]}")
                
                match_id = input("Enter match ID: ")
                
                # Get players for the team of the selected match
                match_details = db_adapter.read_data("""
                    SELECT team_id FROM matches WHERE id = %s;
                """, (match_id,))
                
                if not match_details:
                    print("Match not found.")
                    continue
                
                team_id = match_details[0][0]
                
                players = db_adapter.read_data("""
                    SELECT id, name, position FROM players
                    WHERE team_id = %s
                    ORDER BY id;
                """, (team_id,))
                
                if not players:
                    print("No players available for this team.")
                    continue
                
                print("\nAvailable Players:")
                for player in players:
                    print(f"ID: {player[0]}, Name: {player[1]}, Position: {player[2]}")
                
                player_id = input("Enter player ID: ")
                attacks = input("Enter number of attacks: ")
                kills = input("Enter number of kills: ")
                errors = input("Enter number of errors: ")
                blocks = input("Enter number of blocks: ")
                digs = input("Enter number of digs: ")
                aces = input("Enter number of aces: ")
                
                stat_id = system.record_player_stats(
                    player_id, match_id, attacks, kills, errors, blocks, digs, aces
                )
                
                if stat_id:
                    print(f"Player stats recorded successfully with ID: {stat_id}")
            
            elif match_choice == "3":
                matches = db_adapter.read_data("""
                    SELECT m.id, t.name, m.opponent, m.match_date, m.sets_won, m.sets_lost
                    FROM matches m
                    JOIN teams t ON m.team_id = t.id
                    ORDER BY m.match_date DESC;
                """)
                
                if matches:
                    print("\nMATCHES:")
                    for match in matches:
                        result = "Won" if match[4] > match[5] else "Lost"
                        print(f"ID: {match[0]}, {match[1]} vs {match[2]} on {match[3]}: {result} ({match[4]}-{match[5]})")
                else:
                    print("No matches found.")
        
        elif choice == "4":
            # Training Management
            print("\nTRAINING MANAGEMENT")
            print("1. Create Training Session")
            print("2. View Training Sessions")
            print("3. Back to Main Menu")
            
            training_choice = input("\nEnter your choice (1-3): ")
            
            if training_choice == "1":
                teams = db_adapter.read_data("SELECT * FROM teams ORDER BY id;")
                if not teams:
                    print("No teams available. Please add a team first.")
                    continue
                
                print("\nAvailable Teams:")
                for team in teams:
                    print(f"ID: {team[0]}, Name: {team[1]}")
                
                team_id = input("Enter team ID: ")
                
                print("\nTraining Session Types:")
                print("1. Serving")
                print("2. Attacking")
                print("3. Blocking")
                
                session_type_choice = input("Enter session type (1-3): ")
                session_types = {
                    "1": "serving",
                    "2": "attacking",
                    "3": "blocking"
                }
                
                if session_type_choice not in session_types:
                    print("Invalid choice.")
                    continue
                
                session_type = session_types[session_type_choice]
                session_date = input("Enter session date (YYYY-MM-DD): ")
                duration = input("Enter duration in minutes: ")
                
                session_id = system.record_training_session(
                    team_id, session_type, session_date, duration
                )
                
                if session_id:
                    print(f"Training session recorded successfully with ID: {session_id}")
                    
                    # Demonstrate Factory Method pattern
                    players = db_adapter.read_data("""
                        SELECT id FROM players WHERE team_id = %s;
                    """, (team_id,))
                    
                    if players:
                        player_ids = [player[0] for player in players]
                        
                        print("\nCreating training session object using Factory Method pattern...")
                        session_obj = TrainingSessionFactory.create_session(
                            session_type,
                            date=session_date,
                            players=player_ids,
                            duration=int(duration)
                        )
                        
                        print(f"Created {session_obj.get_session_type()} session.")
                        print("Session can now be used for detailed training analysis.")
            
            elif training_choice == "2":
                sessions = db_adapter.read_data("""
                    SELECT ts.id, t.name, ts.session_type, ts.session_date, ts.duration
                    FROM training_sessions ts
                    JOIN teams t ON ts.team_id = t.id
                    ORDER BY ts.session_date DESC;
                """)
                
                if sessions:
                    print("\nTRAINING SESSIONS:")
                    for session in sessions:
                        print(f"ID: {session[0]}, Team: {session[1]}, Type: {session[2]}, Date: {session[3]}, Duration: {session[4]} minutes")
                else:
                    print("No training sessions found.")
        
        elif choice == "5":
            # Reports and Analysis
            print("\nREPORTS AND ANALYSIS")
            print("1. Player Report")
            print("2. Team Report")
            print("3. Training Recommendation")
            print("4. Export to Google Sheets")
            print("5. Back to Main Menu")
            
            report_choice = input("\nEnter your choice (1-5): ")
            
            if report_choice == "1":
                players = db_adapter.read_data("""
                    SELECT p.id, p.name, p.position, t.name as team
                    FROM players p
                    JOIN teams t ON p.team_id = t.id
                    ORDER BY p.id;
                """)
                
                if not players:
                    print("No players available.")
                    continue
                
                print("\nAvailable Players:")
                for player in players:
                    print(f"ID: {player[0]}, Name: {player[1]}, Position: {player[2]}, Team: {player[3]}")
                
                player_id = input("Enter player ID: ")
                system.generate_player_report(player_id)
            
            elif report_choice == "2":
                teams = db_adapter.read_data("SELECT * FROM teams ORDER BY id;")
                if not teams:
                    print("No teams available.")
                    continue
                
                print("\nAvailable Teams:")
                for team in teams:
                    print(f"ID: {team[0]}, Name: {team[1]}")
                
                team_id = input("Enter team ID: ")
                system.generate_team_report(team_id)
            
            elif report_choice == "3":
                print("\nTRAINING RECOMMENDATION")
                print("1. For Player")
                print("2. For Team")
                
                rec_choice = input("\nEnter your choice (1-2): ")
                
                if rec_choice == "1":
                    players = db_adapter.read_data("""
                        SELECT p.id, p.name, p.position, t.name as team
                        FROM players p
                        JOIN teams t ON p.team_id = t.id
                        ORDER BY p.id;
                    """)
                    
                    if not players:
                        print("No players available.")
                        continue
                    
                    print("\nAvailable Players:")
                    for player in players:
                        print(f"ID: {player[0]}, Name: {player[1]}, Position: {player[2]}, Team: {player[3]}")
                    
                    player_id = input("Enter player ID: ")
                    system.generate_training_recommendation(player_id=player_id)
                
                elif rec_choice == "2":
                    teams = db_adapter.read_data("SELECT * FROM teams ORDER BY id;")
                    if not teams:
                        print("No teams available.")
                        continue
                    
                    print("\nAvailable Teams:")
                    for team in teams:
                        print(f"ID: {team[0]}, Name: {team[1]}")
                    
                    team_id = input("Enter team ID: ")
                    system.generate_training_recommendation(team_id=team_id)
            
            elif report_choice == "4":
                if not sheets_adapter:
                    print("Google Sheets adapter not available.")
                    continue
                
                print("\nEXPORT TO GOOGLE SHEETS")
                print("1. Player Data")
                print("2. Team Data")
                
                export_choice = input("\nEnter your choice (1-2): ")
                
                if export_choice == "1":
                    players = db_adapter.read_data("""
                        SELECT p.id, p.name, p.position, t.name as team
                        FROM players p
                        JOIN teams t ON p.team_id = t.id
                        ORDER BY p.id;
                    """)
                    
                    if not players:
                        print("No players available.")
                        continue
                    
                    print("\nAvailable Players:")
                    for player in players:
                        print(f"ID: {player[0]}, Name: {player[1]}, Position: {player[2]}, Team: {player[3]}")
                    
                    player_id = input("Enter player ID: ")
                    
                    # Get player stats
                    player_stats = system.get_player_stats(player_id)
                    player_info = db_adapter.read_data("""
                        SELECT p.name, p.position, t.name
                        FROM players p
                        JOIN teams t ON p.team_id = t.id
                        WHERE p.id = %s;
                    """, (player_id,))
                    
                    if not player_info:
                        print("Player not found.")
                        continue
                    
                    player_name, player_position, team_name = player_info[0]
                    
                    # Format data for Google Sheets
                    sheet_data = [
                        ["Player Report", player_name, player_position, team_name],
                        [],
                        ["Match Date", "Opponent", "Attacks", "Kills", "Errors", "Blocks", "Digs", "Aces"]
                    ]
                    
                    if player_stats:
                        for stat in player_stats:
                            sheet_data.append([stat[11], stat[10], stat[3], stat[4], stat[5], stat[6], stat[7], stat[8]])
                    
                    # Export to Google Sheets
                    result = system.export_to_sheets(SAMPLE_SPREADSHEET_ID, "PlayerData!A1", sheet_data)
                    
                    if result:
                        print("Player data exported successfully.")
                
                elif export_choice == "2":
                    teams = db_adapter.read_data("SELECT * FROM teams ORDER BY id;")
                    if not teams:
                        print("No teams available.")
                        continue
                    
                    print("\nAvailable Teams:")
                    for team in teams:
                        print(f"ID: {team[0]}, Name: {team[1]}")
                    
                    team_id = input("Enter team ID: ")
                    
                    # Get team stats
                    team_matches = system.get_team_stats(team_id)
                    team_info = db_adapter.read_data("SELECT name FROM teams WHERE id = %s;", (team_id,))
                    
                    if not team_info:
                        print("Team not found.")
                        continue
                    
                    team_name = team_info[0][0]
                    
                    # Format data for Google Sheets
                    sheet_data = [
                        ["Team Report", team_name],
                        [],
                        ["Match Date", "Opponent", "Sets Won", "Sets Lost", "Result"]
                    ]
                    
                    if team_matches:
                        for match in team_matches:
                            result = "Won" if match[4] > match[5] else "Lost"
                            sheet_data.append([match[3], match[2], match[4], match[5], result])
                    
                    # Export to Google Sheets
                    result = system.export_to_sheets(SAMPLE_SPREADSHEET_ID, "TeamData!A1", sheet_data)
                    
                    if result:
                        print("Team data exported successfully.")
        
        elif choice == "6":
            # Exit
            print("\nThank you for using VolleyStat Lite!")
            if db_adapter:
                db_adapter.close()
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()