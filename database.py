import mysql.connector
from mysql.connector import Error

def init_db():
   """Initialize the MySQL database"""
   try:
       conn = mysql.connector.connect(
           host='localhost',     
           user='root',          
           password='meghasram52@',          
           database='stored_resume'  
       )
       
       cursor = conn.cursor()
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS resumes (
               id INT AUTO_INCREMENT PRIMARY KEY,
               filename VARCHAR(255),
               experience TEXT,
               skills TEXT,
               contact_details TEXT,
               upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )
       ''')
       conn.commit()
       cursor.close()
       conn.close()
   
   except Error as e:
        print(f"Error while connecting to MySQL: {e}")
