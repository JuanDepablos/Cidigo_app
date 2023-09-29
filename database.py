import mysql.connector

def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',     
            database='proyecto',       
            user='root',          
            password=None,          
            port=3307  
        )
        return conn
    except Exception as e:
        print(e)
        return None
