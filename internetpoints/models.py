from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer


Base = declarative_base()


class Poster(Base):
    __tablename__ = 'posters'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    emails = relationship('PosterEmail', back_populates='poster')


class PosterEmail(Base):
    __tablename__ = 'poster_emails'

    address = Column(String, primary_key=True)

    poster = relationship('Poster', uselist=False, back_populates='emails')


class Thread(Base):
    __tablename__ = 'threads'

    id = Column(Integer, primary_key=True)

    messages = relationship('Message', back_populates='thread')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(String, primary_key=True)

    thread = relationship('Thread', back_populates='messages')
