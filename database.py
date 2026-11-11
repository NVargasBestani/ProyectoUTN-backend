import mysql.connector
from mysql.connector import Error 

def get_db_connection():
    try:
        #aca se configura los datos exactos con el mysql local 
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="naza1045",
            database="ecommerce_db"
        )

        if conexion.is_connected():
            return conexion


    except Error as e:
        print(f"Error al conectar con base de datos: {e}")
        return None 