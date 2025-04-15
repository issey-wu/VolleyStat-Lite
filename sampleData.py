"""
Sample Data Population Script for VolleyStat Lite
Author: Issey Wu (400387909)
Date: April 8, 2025

This script populates the database with sample data for demonstration purposes.
"""

import psycopg2
import datetime

def populate_sample_data():
    """Populate the database with sample data."""
    print("Populating database with sample data...")
    
    # Database connection details
    DB_HOST = "localhost"
    DB_NAME = "postgres"
    DB_USER = "***REMOVED***"
    DB_PASSWORD = "9055678820Iw"
    DB_PORT = "5432"
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Clean existing data
        print("Cleaning existing data...")
        cursor.execute("DELETE FROM player_stats;")
        cursor.execute("DELETE FROM matches;")
        cursor.execute("DELETE FROM training_sessions;")
        cursor.execute("DELETE FROM players;")
        cursor.execute("DELETE FROM teams;")
        conn.commit()
        print("Existing data cleaned")
        
        # Add teams
        print("Adding teams...")
        cursor.execute("INSERT INTO teams (name) VALUES ('McMaster Marauders') RETURNING id;")
        mcmaster_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO teams (name) VALUES ('Western Mustangs') RETURNING id;")
        western_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Teams added: McMaster (ID: {mcmaster_id}), Western (ID: {western_id})")
        
        # Add players to McMaster
        print("Adding players to McMaster...")
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Michael Johnson', 'Outside Hitter', %s) RETURNING id;", (mcmaster_id,))
        michael_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Emma Davis', 'Setter', %s) RETURNING id;", (mcmaster_id,))
        emma_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Brandon Chen', 'Middle Blocker', %s) RETURNING id;", (mcmaster_id,))
        brandon_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Sophia Martinez', 'Libero', %s) RETURNING id;", (mcmaster_id,))
        sophia_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Jacob Wilson', 'Opposite', %s) RETURNING id;", (mcmaster_id,))
        jacob_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Olivia Brown', 'Middle Blocker', %s) RETURNING id;", (mcmaster_id,))
        olivia_id = cursor.fetchone()[0]
        conn.commit()
        
        # Add players to Western
        print("Adding players to Western...")
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Ethan Taylor', 'Outside Hitter', %s) RETURNING id;", (western_id,))
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Ava Roberts', 'Setter', %s) RETURNING id;", (western_id,))
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Liam Garcia', 'Middle Blocker', %s) RETURNING id;", (western_id,))
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Isabella Kim', 'Libero', %s) RETURNING id;", (western_id,))
        cursor.execute("INSERT INTO players (name, position, team_id) VALUES ('Noah Lewis', 'Opposite', %s) RETURNING id;", (western_id,))
        conn.commit()
        
        # Add matches for McMaster
        print("Adding matches for McMaster...")
        cursor.execute("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Western Mustangs', '2025-03-01', 3, 1) RETURNING id;
        """, (mcmaster_id,))
        match1_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Queen''s Gaels', '2025-03-08', 3, 2) RETURNING id;
        """, (mcmaster_id,))
        match2_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Toronto Varsity Blues', '2025-03-15', 1, 3) RETURNING id;
        """, (mcmaster_id,))
        match3_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Waterloo Warriors', '2025-03-22', 3, 0) RETURNING id;
        """, (mcmaster_id,))
        match4_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO matches (team_id, opponent, match_date, sets_won, sets_lost)
            VALUES (%s, 'Guelph Gryphons', '2025-03-29', 2, 3) RETURNING id;
        """, (mcmaster_id,))
        match5_id = cursor.fetchone()[0]
        conn.commit()
        
        # Add player stats for the matches
        print("Adding player stats...")
        # Match 1 stats
        cursor.execute("""
            INSERT INTO player_stats (player_id, match_id, attacks, kills, errors, blocks, digs, aces)
            VALUES (%s, %s, 35, 15, 5, 2, 8, 3);
        """, (michael_id, match1_id))
        cursor.execute("""
            INSERT INTO player_stats (player_id, match_id, attacks, kills, errors, blocks, digs, aces)
            VALUES (%s, %s, 5, 2, 1, 0, 10, 2);
        """, (emma_id, match1_id))
        # Add more stats for other players and matches...
        conn.commit()
        
        # Add training sessions
        print("Adding training sessions...")
        cursor.execute("""
            INSERT INTO training_sessions (team_id, session_type, session_date, duration)
            VALUES (%s, 'serving', '2025-03-03', 90);
        """, (mcmaster_id,))
        cursor.execute("""
            INSERT INTO training_sessions (team_id, session_type, session_date, duration)
            VALUES (%s, 'attacking', '2025-03-05', 120);
        """, (mcmaster_id,))
        cursor.execute("""
            INSERT INTO training_sessions (team_id, session_type, session_date, duration)
            VALUES (%s, 'blocking', '2025-03-10', 60);
        """, (mcmaster_id,))
        conn.commit()
        
        # Verify data was inserted
        cursor.execute("SELECT COUNT(*) FROM teams;")
        team_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM players;")
        player_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM matches;")
        match_count = cursor.fetchone()[0]
        
        print(f"Data verification: {team_count} teams, {player_count} players, {match_count} matches")
        print("Sample data population complete!")
        
        # Close the connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error during sample data population: {e}")

if __name__ == "__main__":
    populate_sample_data()