"""
VolleyStat Lite - Volleyball Performance Tracking System
Author: Issey Wu (400387909)
Date: April 8, 2025

Main entry point for the application.
"""

import os
from adapters.postgres_adapter import PostgresAdapter
from adapters.sheets_adapter import GoogleSheetsAdapter
from core.system import VolleyStatSystem
from models.observer import Coach, Player, TeamAnalyst
from models.training_session import TrainingSessionFactory

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
            print("5. Export Comprehensive Report")
            print("6. Back to Main Menu")
            
            report_choice = input("\nEnter your choice (1-6): ")
            
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

            elif report_choice == "5":
                if not sheets_adapter:
                    print("Google Sheets adapter not available.")
                    continue
                
                print("\nEXPORT COMPREHENSIVE REPORT")
                # Implement comprehensive report export logic here
                # For now, just a placeholder message
                print("This will export all data to Google Sheets with multiple sheets/tabs")
                confirm = input("Do you want to proceed? (y/n): ")
    
                if confirm.lower() == 'y':
                    result = system.export_comprehensive_report(SAMPLE_SPREADSHEET_ID)
        
                    if result:
                        print("Comprehensive report exported successfully!")

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