import psycopg2

def test_db_connection():
    """Test direct database connection and insertion."""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host="localhost",
            dbname="postgres",
            user="***REMOVED***",
            password="9055678820Iw",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Check if we can connect
        print("Database connection successful")
        
        # Clean existing teams data
        cursor.execute("DELETE FROM teams;")
        conn.commit()
        print("Deleted existing teams data")
        
        # Insert test teams
        cursor.execute("INSERT INTO teams (name) VALUES ('McMaster Marauders') RETURNING id;")
        mcmaster_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO teams (name) VALUES ('Western Mustangs') RETURNING id;")
        western_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Inserted teams with IDs: McMaster={mcmaster_id}, Western={western_id}")
        
        # Verify teams were inserted
        cursor.execute("SELECT * FROM teams;")
        teams = cursor.fetchall()
        print("Teams in database:")
        for team in teams:
            print(f"ID: {team[0]}, Name: {team[1]}")
        
        # Clean up
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database test failed: {e}")

if __name__ == "__main__":
    test_db_connection()