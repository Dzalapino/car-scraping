from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from repository.models import Base

# Db setup
engine = create_engine('sqlite:///car-scraping.db')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
