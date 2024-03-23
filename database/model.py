import logging
from logging.handlers import RotatingFileHandler

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from config.config_reader import config

engine = create_engine(config.url_db.get_secret_value())
Base = declarative_base()

logger = logging.getLogger('sqlalchemy')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('logs/db.log', maxBytes=5000000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, nullable=False)
    dates = relationship('Date_users')
    
class Date_users(Base):
    __tablename__ = "date_users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    day = Column(String)
    month = Column(String)
    comment = Column(String)
    check_rem = Column(Boolean)
    hour_rem = Column(String)
    minute_rem = Column(String)
    
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()