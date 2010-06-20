# coding: utf-8

'''
    pyseeek.model
    ~~~~~~~~~~~~~

    Database model for PySeeek.
    
    :copyright: (c) 2010 by Marc Schlaich
    :license: MIT, see LICENSE for more details.
'''

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///temp.db', convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))

Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)


class Page(Base):
    __tablename__ = 'pages'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=False)
    
class WordIndex(Base):
    __tablename__ = 'word_index'
    
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False)
    

if __name__ == '__main__':
    init_db()
