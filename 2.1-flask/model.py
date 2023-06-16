import os
from atexit import register

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DB", "site_ads")
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", "5433")

PG_DSN = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(PG_DSN)

Session = sessionmaker(bind=engine)
Base = declarative_base()


class Ads(Base):
    __tablename__ = "site_ads"

    id = Column(Integer, primary_key=True)
    heading = Column(String, nullable=False)
    description = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    owner = Column(String, nullable=False)


# Создает все таблицы(выполняются миграции)
Base.metadata.create_all(bind=engine)

register(engine.dispose)
