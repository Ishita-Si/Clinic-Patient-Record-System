import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("127.0.0.1"),
        user=os.getenv("Database"),
        password=os.getenv("Blackpink09"),
        database=os.getenv("clinic_db")
    )

