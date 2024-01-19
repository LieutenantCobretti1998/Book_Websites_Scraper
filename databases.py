from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    old_price = Column(Float)
    discount = Column(Float)
    new_price = Column(Float)
    currency = Column(String)
    language = Column(String)
    store = Column(String)
    available = Column(Boolean)


class TestDb(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    old_price = Column(Float)
    discount = Column(Float)
    new_price = Column(Float)
    currency = Column(String)
    language = Column(String)
    store = Column(String)
    available = Column(Boolean)


# Setup database engine
engine = create_engine('sqlite:///books.db')
Base.metadata.create_all(engine)

# Create a sessionMaker
Session = sessionmaker(bind=engine)



