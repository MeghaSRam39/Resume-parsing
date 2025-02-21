import mysql.connector

# Database connection details
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "meghasram52@",
    "database": "stored_resume"
}

try:
    # Establish connection
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        print("Connected to MySQL database")

        # Create a cursor object
        cursor = connection.cursor()

        # Execute a simple query
        '''cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'stored_resume'")
        columns = cursor.fetchall()
        for column in columns:
            print(column[0])'''
        
        cursor.execute("DELETE FROM resumes")
        connection.commit()
        print("All data deleted from resumes")

        # Fetch and print results
        tables = cursor.fetchall()
        for table in tables:
            print(table)

        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("Connection closed")

except mysql.connector.Error as e:
    print(f"Error: {e}")