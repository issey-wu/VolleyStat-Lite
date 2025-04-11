"""
Sample Data Population Script for VolleyStat Lite
Author: Issey Wu (400387909)
Date: April 8, 2025

This script populates the database with sample data for demonstration purposes.
"""

import sys
import datetime
from Implementation import PostgresAdapter, VolleyStatSystem

def populate_sample_data():
    """Populate the database with sample data."""
    print("Populating database with sample data...")
    
    # Database connection details
    DB_HOST = "localhost"
    DB_NAME = "volleystat_lite"
    DB_USER = "postgres"
    DB_PASSWORD = "9055678820Iw"
    DB_PORT = "5432"
    
    # Initialize database adapter
    db_adapter = PostgresAdapter(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    
    # Initialize VolleyStat system
    system = VolleyStatSystem(db_adapter)
    
    # Clean existing data
    print("Cleaning existing data...")
    db_adapter.write_data("DELETE FROM player_stats;")
    db_adapter.write_data("DELETE FROM matches;")
    db_adapter.write_data("DELETE FROM training_sessions;")
    db_adapter.write_data("DELETE FROM players;")
    db_adapter.write_data("DELETE FROM teams;")
    
    # Add teams
    print("Adding teams...")
    mcmaster_id = system.add_team("McMaster Marauders")
    western_id = system.add_team("Western Mustangs")
    
    # Add players to McMaster
    print("Adding players to McMaster...")
    michael_id = system.add_player("Michael Johnson", "Outside Hitter", mcmaster_id)
    emma_id = system.add_player("Emma Davis", "Setter", mcmaster_id)
    brandon_id = system.add_player("Brandon Chen", "Middle Blocker", mcmaster_id)
    sophia_id = system.add_player("Sophia Martinez", "Libero", mcmaster_id)
    jacob_id = system.add_player("Jacob Wilson", "Opposite", mcmaster_id)
    olivia_id = system.add_player("Olivia Brown", "Middle Blocker", mcmaster_id)
    
    # Add players to Western
    print("Adding players to Western...")
    system.add_player("Ethan Taylor", "Outside Hitter", western_id)
    system.add_player("Ava Roberts", "Setter", western_id)
    system.add_player("Liam Garcia", "Middle Blocker", western_id)
    system.add_player("Isabella Kim", "Libero", western_id)
    system.add_player("Noah Lewis", "Opposite", western_id)
    
    # Add matches for McMaster
    print("Adding matches for McMaster...")
    match1_id = system.record_match(mcmaster_id, "Western Mustangs", "2025-03-01", 3, 1)
    match2_id = system.record_match(mcmaster_id, "Queen's Gaels", "2025-03-08", 3, 2)
    match3_id = system.record_match(mcmaster_id, "Toronto Varsity Blues", "2025-03-15", 1, 3)
    match4_id = system.record_match(mcmaster_id, "Waterloo Warriors", "2025-03-22", 3, 0)
    match5_id = system.record_match(mcmaster_id, "Guelph Gryphons", "2025-03-29", 2, 3)
    
    # Add player stats for match 1
    print("Adding player stats for matches...")
    system.record_player_stats(michael_id, match1_id, 35, 15, 5, 2, 8, 3)
    system.record_player_stats(emma_id, match1_id, 5, 2, 1, 0, 10, 2)
    system.record_player_stats(brandon_id, match1_id, 20, 8, 2, 5, 3, 0)
    system.record_player_stats(sophia_id, match1_id, 0, 0, 0, 0, 18, 0)
    system.record_player_stats(jacob_id, match1_id, 28, 12, 4, 1, 5, 2)
    system.record_player_stats(olivia_id, match1_id, 18, 7, 3, 4, 2, 1)
    
    # Add player stats for match 2
    system.record_player_stats(michael_id, match2_id, 40, 18, 7, 1, 10, 2)
    system.record_player_stats(emma_id, match2_id, 6, 3, 2, 0, 12, 3)
    system.record_player_stats(brandon_id, match2_id, 22, 9, 3, 4, 2, 0)
    system.record_player_stats(sophia_id, match2_id, 0, 0, 0, 0, 22, 0)
    system.record_player_stats(jacob_id, match2_id, 32, 14, 6, 2, 7, 1)
    system.record_player_stats(olivia_id, match2_id, 20, 8, 4, 3, 3, 0)
    
    # Add player stats for match 3
    system.record_player_stats(michael_id, match3_id, 30, 10, 8, 1, 7, 1)
    system.record_player_stats(emma_id, match3_id, 4, 1, 2, 0, 8, 1)
    system.record_player_stats(brandon_id, match3_id, 15, 5, 4, 3, 1, 0)
    system.record_player_stats(sophia_id, match3_id, 0, 0, 0, 0, 15, 0)
    system.record_player_stats(jacob_id, match3_id, 25, 8, 7, 0, 4, 1)
    system.record_player_stats(olivia_id, match3_id, 12, 4, 5, 2, 1, 0)
    
    # Add player stats for match 4
    system.record_player_stats(michael_id, match4_id, 25, 14, 3, 3, 6, 4)
    system.record_player_stats(emma_id, match4_id, 3, 2, 0, 0, 9, 4)
    system.record_player_stats(brandon_id, match4_id, 18, 10, 1, 6, 2, 0)
    system.record_player_stats(sophia_id, match4_id, 0, 0, 0, 0, 20, 0)
    system.record_player_stats(jacob_id, match4_id, 22, 13, 2, 2, 5, 3)
    system.record_player_stats(olivia_id, match4_id, 16, 9, 2, 5, 2, 1)
    
    # Add player stats for match 5
    system.record_player_stats(michael_id, match5_id, 38, 16, 6, 2, 9, 2)
    system.record_player_stats(emma_id, match5_id, 5, 1, 2, 0, 11, 2)
    system.record_player_stats(brandon_id, match5_id, 24, 10, 4, 4, 3, 0)
    system.record_player_stats(sophia_id, match5_id, 0, 0, 0, 0, 24, 0)
    system.record_player_stats(jacob_id, match5_id, 30, 12, 5, 1, 6, 2)
    system.record_player_stats(olivia_id, match5_id, 22, 9, 5, 3, 2, 0)
    
    # Add training sessions
    print("Adding training sessions...")
    system.record_training_session(mcmaster_id, "serving", "2025-03-03", 90)
    system.record_training_session(mcmaster_id, "attacking", "2025-03-05", 120)
    system.record_training_session(mcmaster_id, "blocking", "2025-03-10", 60)
    system.record_training_session(mcmaster_id, "serving", "2025-03-17", 90)
    system.record_training_session(mcmaster_id, "attacking", "2025-03-19", 120)
    system.record_training_session(mcmaster_id, "blocking", "2025-03-24", 60)
    
    print("Sample data population complete!")
    db_adapter.close()

if __name__ == "__main__":
    populate_sample_data()