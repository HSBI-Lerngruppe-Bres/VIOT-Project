from sqlalchemy import create_engine
from models import Base, setup_hypertables
from sqlalchemy.orm import sessionmaker

class DatabaseConnector:
    def __init__(self, username, password, host, port, database):
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
        self.Base = Base
        setup_hypertables(self.get_db())
        

    def get_db(self):
        """
        Provides a database session for use within a context.

        This generator function yields a database session object, which can be used
        to interact with the database. The session is automatically closed once the
        context is exited.

        Yields:
            db (Session): A SQLAlchemy session object for database operations.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Example usage:
# db_connector = DatabaseConnector("username", "password", "localhost", 5432, "mydatabase")
# Base = db_connector.Base
# get_db = db_connector.get_db
