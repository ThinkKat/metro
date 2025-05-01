import os

from dotenv import load_env

from repositories.metro_repository.postgresql_metro_repository import PostgresqlMetroRepository
from repositories.timetable_repository.postgresql_timetable_repository import PostgresqlTimetableRepository

load_env()

async def get_metro_repository():
    repo = PostgresqlMetroRepository()
    repo.create_engine(os.getenv("POSTGRESQL_METRO_DB_URL"))
    return repo

async def get_timetable_repository():
    repo = PostgresqlTimetableRepository()
    repo.create_engine(os.getenv("POSTGRESQL_METRO_DB_URL"))
    return repo
