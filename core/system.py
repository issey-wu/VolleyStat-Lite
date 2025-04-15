"""
VolleyStat Lite - Core System
This module contains the main functionality of the VolleyStat system.
"""

import statistics
import datetime
from models.observer import Subject
from utils.db_initializer import initialize_database

class VolleyStatSystem(Subject):
    """Main class for the VolleyStat Lite system."""
    def __init__(self, db_adapter, sheets_adapter=None):
        super().__init__()
        self.db_adapter = db_adapter
        self.sheets_adapter = sheets_adapter
        initialize_database(db_adapter)
    
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
        # First verify the team exists
        team_check_query = "SELECT * FROM teams WHERE id = %s;"
        team_exists = self.db_adapter.read_data(team_check_query, (team_id,))
    
        if not team_exists:
            print(f"Error: Team with ID {team_id} does not exist. Match not recorded.")
            return None
    
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
        
            # Verify the match was saved
            verify_query = "SELECT * FROM matches WHERE id = %s;"
            verify_result = self.db_adapter.read_data(verify_query, (match_id,))
            if verify_result:
                print(f"Match verification successful. ID: {match_id}, Team ID: {verify_result[0][1]}")
            else:
                print("Warning: Match was created but couldn't be verified!")
            
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
    
    def export_comprehensive_report(self, spreadsheet_id):
        """Export a comprehensive report of all data to Google Sheets."""
        if not self.sheets_adapter:
            print("Google Sheets adapter not available.")
            return False
        
        try:
            # First, make sure the sheets exist
            # We need to use the spreadsheets.batchUpdate API for this
            if not self.sheets_adapter.service:
                if not self.sheets_adapter.connect():
                    return False
            
            # Define the sheets we need
            sheet_names = ["Summary", "Teams", "Players", "Matches", "Player Stats", "Training Sessions"]
            
            # Check what sheets already exist
            spreadsheet_info = self.sheets_adapter.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet_info.get('sheets', [])]
            
            # Prepare requests to add missing sheets
            requests = []
            for sheet_name in sheet_names:
                if sheet_name not in existing_sheets:
                    requests.append({
                        'addSheet': {
                            'properties': {
                                'title': sheet_name
                            }
                        }
                    })
            
            # Execute the batch update if there are any requests
            if requests:
                self.sheets_adapter.service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': requests}
                ).execute()
                print(f"Created {len(requests)} new sheets in the spreadsheet")
            
            # Now we can proceed with populating the data
            
            # 1. Export Teams Data
            teams = self.db_adapter.read_data("SELECT * FROM teams ORDER BY id;")
            if teams:
                teams_data = [["Team ID", "Team Name"]]
                for team in teams:
                    teams_data.append([team[0], team[1]])
                
                self.sheets_adapter.write_data(spreadsheet_id, "Teams!A1", teams_data)
                print("Teams data exported successfully")
            
            # 2. Export Players Data
            players = self.db_adapter.read_data("""
                SELECT p.id, p.name, p.position, t.name as team_name
                FROM players p
                JOIN teams t ON p.team_id = t.id
                ORDER BY p.id;
            """)
            if players:
                players_data = [["Player ID", "Name", "Position", "Team"]]
                for player in players:
                    players_data.append([player[0], player[1], player[2], player[3]])
                
                self.sheets_adapter.write_data(spreadsheet_id, "Players!A1", players_data)
                print("Players data exported successfully")
            
            # 3. Export Matches Data
            matches = self.db_adapter.read_data("""
                SELECT m.id, t.name, m.opponent, m.match_date, m.sets_won, m.sets_lost
                FROM matches m
                JOIN teams t ON m.team_id = t.id
                ORDER BY m.match_date DESC;
            """)
            if matches:
                matches_data = [["Match ID", "Team", "Opponent", "Date", "Sets Won", "Sets Lost", "Result"]]
                for match in matches:
                    result = "Won" if match[4] > match[5] else "Lost"
                    matches_data.append([match[0], match[1], match[2], match[3], match[4], match[5], result])
                
                self.sheets_adapter.write_data(spreadsheet_id, "Matches!A1", matches_data)
                print("Matches data exported successfully")
            
            # 4. Export Player Stats Data
            stats = self.db_adapter.read_data("""
                SELECT ps.id, p.name as player_name, t.name as team_name, 
                       m.opponent, m.match_date, ps.attacks, ps.kills, ps.errors, 
                       ps.blocks, ps.digs, ps.aces
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.id
                JOIN matches m ON ps.match_id = m.id
                JOIN teams t ON p.team_id = t.id
                ORDER BY m.match_date DESC;
            """)
            if stats:
                stats_data = [["Stat ID", "Player", "Team", "Opponent", "Match Date", 
                               "Attacks", "Kills", "Errors", "Blocks", "Digs", "Aces"]]
                for stat in stats:
                    stats_data.append([
                        stat[0], stat[1], stat[2], stat[3], stat[4], 
                        stat[5], stat[6], stat[7], stat[8], stat[9], stat[10]
                    ])
                
                self.sheets_adapter.write_data(spreadsheet_id, "Player Stats!A1", stats_data)
                print("Player stats data exported successfully")
            
            # 5. Export Training Sessions Data
            sessions = self.db_adapter.read_data("""
                SELECT ts.id, t.name, ts.session_type, ts.session_date, ts.duration
                FROM training_sessions ts
                JOIN teams t ON ts.team_id = t.id
                ORDER BY ts.session_date DESC;
            """)
            if sessions:
                sessions_data = [["Session ID", "Team", "Type", "Date", "Duration (min)"]]
                for session in sessions:
                    sessions_data.append([
                        session[0], session[1], session[2], session[3], session[4]
                    ])
                
                self.sheets_adapter.write_data(spreadsheet_id, "Training Sessions!A1", sessions_data)
                print("Training sessions data exported successfully")
            
            # 6. Create Summary Dashboard
            summary_data = [
                ["VOLLEYSTAT LITE - COMPREHENSIVE REPORT"],
                [f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
                [],
                ["Category", "Count"],
                ["Teams", len(teams) if teams else 0],
                ["Players", len(players) if players else 0],
                ["Matches", len(matches) if matches else 0],
                ["Stats Records", len(stats) if stats else 0],
                ["Training Sessions", len(sessions) if sessions else 0],
            ]
            
            self.sheets_adapter.write_data(spreadsheet_id, "Summary!A1", summary_data)
            print("Summary dashboard created successfully")
            
            print("\nComprehensive report exported successfully to Google Sheets!")
            print(f"Spreadsheet ID: {spreadsheet_id}")
            return True
            
        except Exception as e:
            print(f"Error exporting comprehensive report: {e}")
            return False