import os
from psycopg2 import pool
from dotenv import load_dotenv


# database init script
def db_init():

    # Load .env file
    load_dotenv()

    # Get the connection string from the environment variable
    connection_string = os.getenv('DATABASE_URL')

    # Create a connection pool
    connection_pool = pool.SimpleConnectionPool(
        1,  # Minimum number of connections in the pool
        10,  # Maximum number of connections in the pool
        connection_string
    )

    # Check if the pool was created successfully
    if connection_pool:
        print("Connection pool created successfully")
    
    return connection_pool


# Run query with options to commit or not. For create/insert use commit as True 
def run_query(query, commit = False):

    connection_pool = db_init()
    conn = connection_pool.getconn()
    cur = conn.cursor()

    # Execute SQL commands to retrieve the current time and version from PostgreSQL
    try:
        cur.execute(query)
        if commit: 
            conn.commit(); 
            return
        op = cur.fetchall()
        return op
    except:
        conn.close()
