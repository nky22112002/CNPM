import mysql.connector

def get_db_connection():
    db_config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'student_management'
        
    }
    conn = mysql.connector.connect(**db_config)
    return conn
