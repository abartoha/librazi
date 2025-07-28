import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class SessionPool:
    def __init__(self):
        dotenv.load_dotenv()
        self.url = os.getenv("DATABASE_URL")
        if not self.url:
            raise ValueError("DATABASE_URL not found in environment variables")
        self.engine = create_engine(self.url, pool_size=5, max_overflow=10)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def close_session(self, session):
        session.close()