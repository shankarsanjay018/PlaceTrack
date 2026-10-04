import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Sanjay@2005",
        database="placetrack"
    )

    return connection
if __name__ == "__main__":
    connection = get_db_connection()

    if connection.is_connected():
        print("MySQL connection successful!")

    connection.close()