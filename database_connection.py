import streamlit as st
import pymongo
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_mongodb_connection():

    try:
        uri = os.getenv("MONGODB_URI")
        client = pymongo.MongoClient(uri)
        client.admin.command('hello')  # Ping the server to verify connection
        return client
    
    except pymongo.errors.ConnectionFailure as e:
        raise pymongo.errors.ConnectionFailure(f"Error connecting to MongoDB: {e}")

def get_postgres_connection():

    try:
        connection = psycopg2.connect(
        database=os.getenv("DATABASE"),
        user=os.getenv("DB_USER_NAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),  # Localhost if running on the same machine
        port=os.getenv("DB_PORT")  # Default port for PostgreSQL
    )
        return connection

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return None  # Indicate connection failure
    
def disconnect_mongodb(connection):
    
    if connection:
        try:
            connection.close()
        except Exception as e:
            st.write("Error disconnecting from MongoDB:", e)

def disconnect_postgres(connection):
    if connection:
        try:
            connection.close()
        except Exception as e:
            st.write("Error disconnecting from PostgreSQL:", e)