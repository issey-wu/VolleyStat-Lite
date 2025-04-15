"""
VolleyStat Lite - PostgreSQL Adapter
This module implements the adapter for PostgreSQL database interactions.
"""

import psycopg2
from adapters.adapter_base import ThirdPartyAdapter

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