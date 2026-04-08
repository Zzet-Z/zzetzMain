from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker


class Base(DeclarativeBase):
    pass


SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False),
)


def init_db(database_url: str):
    engine = create_engine(database_url, future=True)
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(engine)
    return engine
