# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,          # Number of connections to keep open
    max_overflow=40,       # Extra connections allowed under load
    pool_timeout=30,       # Seconds to wait before giving up on getting a connection
    pool_recycle=1800,     # Recycle connections every 30 mins to avoid stale DB links
    pool_pre_ping=True,    # Verify connection health before use
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()   
