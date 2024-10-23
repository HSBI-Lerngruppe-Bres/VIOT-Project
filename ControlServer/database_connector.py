from sqlalchemy import create_engine
from models import Base, setup_hypertables
from sqlalchemy.orm import sessionmaker

class DatabaseConnector:
    def __init__(self, username, password, host, port, database, logger=None):
        """
        Initializes the database connector with the given parameters and sets up the database engine and session.

        Args:
            username (str): The username for the database.
            password (str): The password for the database.
            host (str): The host address of the database.
            port (int): The port number to connect to the database.
            database (str): The name of the database.
        """
        self.DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logger
        self.Base = Base
        self.Base.metadata.create_all(bind=self.engine)
        setup_hypertables(self.engine)
        self.logger.info("Database tables created successfully.")
        

# Example usage:
# db_connector = DatabaseConnector("username", "password", "localhost", 5432, "mydatabase")