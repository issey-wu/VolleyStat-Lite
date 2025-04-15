def populate_sample_data():
    """Populate the database with sample data."""
    print("Populating database with sample data...")
    
    # Database connection details
    DB_HOST = "localhost"
    DB_NAME = "postgres"
    DB_USER = "***REMOVED***"
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
    
    # Test database connection
    test_query = "SELECT 1;"
    result = db_adapter.read_data(test_query)
    print(f"Database connection test: {'Successful' if result else 'Failed'}")
    
    # Initialize VolleyStat system
    system = VolleyStatSystem(db_adapter)
    
    # Clean existing data
    print("Cleaning existing data...")
    try:
        db_adapter.write_data("DELETE FROM player_stats;")
        db_adapter.write_data("DELETE FROM matches;")
        db_adapter.write_data("DELETE FROM training_sessions;")
        db_adapter.write_data("DELETE FROM players;")
        db_adapter.write_data("DELETE FROM teams;")
        print("Data cleaning completed successfully")
    except Exception as e:
        print(f"Error cleaning data: {e}")
    
    # Add teams directly to test database insertion
    print("Testing direct database insertion...")
    try:
        db_adapter.write_data("INSERT INTO teams (name) VALUES ('Test Team') RETURNING id;")
        test_count = db_adapter.read_data("SELECT COUNT(*) FROM teams;")
        print(f"Teams after direct insertion: {test_count[0][0] if test_count else 'None'}")
    except Exception as e:
        print(f"Direct insertion error: {e}")
    
    # Add teams through system
    print("Adding teams via system...")
    try:
        mcmaster_id = system.add_team("McMaster Marauders")
        print(f"McMaster team ID: {mcmaster_id}")
        western_id = system.add_team("Western Mustangs")
        print(f"Western team ID: {western_id}")
        
        # Check team count
        team_count = db_adapter.read_data("SELECT COUNT(*) FROM teams;")
        print(f"Total teams in database: {team_count[0][0] if team_count else 'None'}")
        
        # Display team data
        teams = db_adapter.read_data("SELECT * FROM teams;")
        print("Teams in database:")
        for team in teams:
            print(f"ID: {team[0]}, Name: {team[1]}")
    except Exception as e:
        print(f"Error adding teams: {e}")
    
    print("Sample data population complete!")
    db_adapter.close()