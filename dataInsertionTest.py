import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="***REMOVED***",
        password="9055678820Iw",
        port="5432"
    )
    cursor = conn.cursor()
    
    # Create a test table
    cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR(100));")
    
    # Insert a test row
    cursor.execute("INSERT INTO test_table (name) VALUES ('Test Entry');")
    conn.commit()
    
    # Verify the data was inserted
    cursor.execute("SELECT COUNT(*) FROM test_table;")
    count = cursor.fetchone()[0]
    print(f"Records in test_table: {count}")
    
    cursor.close()
    conn.close()
    print("Test completed successfully")
except Exception as e:
    print(f"Database connection test failed: {e}")