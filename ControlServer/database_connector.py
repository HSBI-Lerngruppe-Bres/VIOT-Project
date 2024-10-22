from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class DatabaseConnector:
    def __init__(self, username, password, host, port, database):
        self.DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Example usage:
# db_connector = DatabaseConnector("username", "password", "localhost", 5432, "mydatabase")
# Base = db_connector.Base
# get_db = db_connector.get_db
