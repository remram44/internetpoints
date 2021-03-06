from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, String, Text, DateTime


Base = declarative_base()


class Poster(Base):
    __tablename__ = 'posters'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    score = Column(Integer, nullable=False, default=0)

    emails = relationship('PosterEmail')


class PosterEmail(Base):
    __tablename__ = 'poster_emails'

    address = Column(String, primary_key=True)

    poster_id = Column(Integer, ForeignKey('posters.id'), nullable=False)
    poster = relationship('Poster', back_populates='emails')


class Thread(Base):
    __tablename__ = 'threads'

    id = Column(Integer, primary_key=True)
    # Date is UTC!
    last_msg = Column(DateTime, nullable=False)

    messages = relationship('Message', back_populates='thread')
    task_assignations = relationship('TaskAssignation',
                                     back_populates='thread')

    @property
    def assigned(self):
        return bool(self.task_assignations)


class Message(Base):
    __tablename__ = 'messages'

    id = Column(String, primary_key=True)
    from_ = Column(String, nullable=False)
    subject = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    # Date is UTC!
    date = Column(DateTime, nullable=False)

    thread_id = Column(Integer, ForeignKey('threads.id'), nullable=False)
    thread = relationship('Thread',  back_populates='messages')
    poster_email = relationship('PosterEmail',
                                primaryjoin=from_ == PosterEmail.address,
                                foreign_keys=from_,
                                remote_side=PosterEmail.address)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    reward = Column(Integer, nullable=False, default=0)

    assignations = relationship('TaskAssignation', back_populates='task')


class TaskAssignation(Base):
    __tablename__ = 'thread_tasks'

    # Date is UTC!
    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    thread_id = Column(Integer, ForeignKey('threads.id'), primary_key=True)
    thread = relationship('Thread', back_populates='task_assignations')
    task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True)
    task = relationship('Task', back_populates='assignations')
    poster_id = Column(Integer, ForeignKey('posters.id'), nullable=False)
    poster = relationship('Poster')
