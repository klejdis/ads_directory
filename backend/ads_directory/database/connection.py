from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ads_directory.config import settings

engine = create_async_engine(settings.database.URI, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)
