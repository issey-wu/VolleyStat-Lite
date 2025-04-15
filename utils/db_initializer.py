"""
VolleyStat Lite - Database Initializer
This module handles the initialization of the database schema.
"""

def initialize_database(db_adapter):
    """Set up the database tables if they don't exist."""
    # Create players table
    db_adapter.write_data("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            position VARCHAR(50),
            team_id INTEGER
        );
    """)
    
    # Create teams table
    db_adapter.write_data("""
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        );
    """)
    
    # Create matches table
    db_adapter.write_data("""
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
    db_adapter.write_data("""
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
    db_adapter.write_data("""
        CREATE TABLE IF NOT EXISTS training_sessions (
            id SERIAL PRIMARY KEY,
            team_id INTEGER,
            session_type VARCHAR(50),
            session_date DATE,
            duration INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );
    """)