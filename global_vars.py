from database_connection import get_mongodb_connection, get_postgres_connection, disconnect_mongodb, disconnect_postgres

# connecting the databases
mongo_client = get_mongodb_connection()
post_client = get_postgres_connection()