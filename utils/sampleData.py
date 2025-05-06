"""
Sample Data Population Script for VolleyStat Lite
Author: Issey Wu (400387909)
Date: April 8, 2025

This script populates the database with sample data for demonstration purposes.
"""
import sys
import os

# Add the parent directory to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # This gets the "VolleyStat Lite" directory
sys.path.append(parent_dir)

# Import from other modules
from adapters.postgres_adapter import PostgresAdapter

def populate_sample_data():
    """Populate the database with sample data."""
    print("Populating database with sample data...")
    
    # Database connection details
    DB_HOST = "localhost"
    DB_NAME = "postgres"
    DB_USER = "<your-username>"
    DB_PASSWORD = "<your-password>"
    DB_PORT = "5432"
    
    # Create a database adapter
    db_adapter = PostgresAdapter(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    
    try:
        # Connect to database
        if db_adapter.connect():
            print("Connected to database successfully")
        else:
            print("Failed to connect to database")
            return
        
        # Clean existing data
        print("Cleaning existing data...")
        db_adapter.write_data("DELETE FROM player_stats;")
        db_adapter.write_data("DELETE FROM matches;")
        db_adapter.write_data("DELETE FROM training_sessions;")
        db_adapter.write_data("DELETE FROM players;")
        db_adapter.write_data("DELETE FROM teams;")
        print("Existing data cleaned")
        
        # Add teams
        print("Adding teams...")
        result = db_adapter.read_data("INSERT INTO teams (name) VALUES ('McMaster Marauders') RETURNING id;")
        mcmaster_id = result[0][0]
        result = db_adapter.read_data("INSERT INTO teams (name) VALUES ('Western Mustangs') RETURNING id;")
        western_id = result[0][0]
        print(f"Teams added: McMaster (ID: {mcmaster_id}), Western (ID: {western_id})")
        
        # Add players to McMaster
        print("Adding players to McMaster...")
        result = db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Michael Johnson', 'Outside Hitter', %s) RETURNING id;", 
            (mcmaster_id,)
        )
        michael_id = result[0][0]
        
        result = db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Emma Davis', 'Setter', %s) RETURNING id;", 
            (mcmaster_id,)
        )
        emma_id = result[0][0]
        
        result = db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Brandon Chen', 'Middle Blocker', %s) RETURNING id;", 
            (mcmaster_id,)
        )
        brandon_id = result[0][0]
        
        result = db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Sophia Martinez', 'Libero', %s) RETURNING id;", 
            (mcmaster_id,)
        )
        sophia_id = result[0][0]
        
        result = db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Jacob Wilson', 'Opposite', %s) RETURNING id;", 
            (mcmaster_id,)
        )
        jacob_id = result[0][0]
        
        result = db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Olivia Brown', 'Middle Blocker', %s) RETURNING id;", 
            (mcmaster_id,)
        )
        olivia_id = result[0][0]
        
        # Add players to Western
        print("Adding players to Western...")
        db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Ethan Taylor', 'Outside Hitter', %s) RETURNING id;", 
            (western_id,)
        )
        db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Ava Roberts', 'Setter', %s) RETURNING id;", 
            (western_id,)
        )
        db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Liam Garcia', 'Middle Blocker', %s) RETURNING id;", 
            (western_id,)
        )
        db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Isabella Kim', 'Libero', %s) RETURNING id;", 
            (western_id,)
        )
        db_adapter.read_data(
            "INSERT INTO players (name, position, team_id) VALUES ('Noah Lewis', 'Opposite', %s) RETURNING id;", 
            (western_id,)
        )
        
        # Add matches for McMaster
        print("Adding matches for McMaster...")
        result = db_adapter.read_data("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Western Mustangs', '2025-03-01', 3, 1) RETURNING id;
        """, (mcmaster_id,))
        match1_id = result[0][0]
        
        result = db_adapter.read_data("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Queen''s Gaels', '2025-03-08', 3, 2) RETURNING id;
        """, (mcmaster_id,))
        match2_id = result[0][0]
        
        result = db_adapter.read_data("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Toronto Varsity Blues', '2025-03-15', 1, 3) RETURNING id;
        """, (mcmaster_id,))
        match3_id = result[0][0]
        
        result = db_adapter.read_data("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Waterloo Warriors', '2025-03-22', 3, 0) RETURNING id;
        """, (mcmaster_id,))
        match4_id = result[0][0]
        
        result = db_adapter.read_data("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Guelph Gryphons', '2025-03-29', 2, 3) RETURNING id;
        """, (mcmaster_id,))
        match5_id = result[0][0]
        
        # Add player stats for the matches
        print("Adding player stats...")
        # Match 1 stats
        db_adapter.write_data("""
            INSERT INTO player_stats (player_id, match_id, attacks, kills, errors, blocks, digs, aces)
            VALUES (%s, %s, 35, 15, 5, 2, 8, 3);
        """, (michael_id, match1_id))
        db_adapter.write_data("""
            INSERT INTO player_stats (player_id, match_id, attacks, kills, errors, blocks, digs, aces)
            VALUES (%s, %s, 5, 2, 1, 0, 10, 2);
        """, (emma_id, match1_id))
        # Add more stats for other players and matches...
        
        # Add training sessions
        print("Adding training sessions...")
        db_adapter.write_data("""
            INSERT INTO training_sessions (team_id, session_type, session_date, duration)
            VALUES (%s, 'serving', '2025-03-03', 90);
        """, (mcmaster_id,))
        db_adapter.write_data("""
            INSERT INTO training_sessions (team_id, session_type, session_date, duration)
            VALUES (%s, 'attacking', '2025-03-05', 120);
        """, (mcmaster_id,))
        db_adapter.write_data("""
            INSERT INTO training_sessions (team_id, session_type, session_date, duration)
            VALUES (%s, 'blocking', '2025-03-10', 60);
        """, (mcmaster_id,))
        
        # Verify data was inserted
        result = db_adapter.read_data("SELECT COUNT(*) FROM teams;")
        team_count = result[0][0]
        result = db_adapter.read_data("SELECT COUNT(*) FROM players;")
        player_count = result[0][0]
        result = db_adapter.read_data("SELECT COUNT(*) FROM matches;")
        match_count = result[0][0]
        
        print(f"Data verification: {team_count} teams, {player_count} players, {match_count} matches")
        print("Sample data population complete!")
        
        # Close the connection
        db_adapter.close()
        
    except Exception as e:
        print(f"Error during sample data population: {e}")
        if db_adapter:
            db_adapter.close()

if __name__ == "__main__":
    populate_sample_data()
