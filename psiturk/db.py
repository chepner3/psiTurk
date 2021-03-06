from __future__ import print_function
from __future__ import absolute_import
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from .psiturk_config import PsiturkConfig
import re
import os
import sys

config = PsiturkConfig()
config.load_config()

DATABASE = config.get('Database Parameters', 'database_url')

if 'mysql://' in DATABASE.lower():
	try:
		 __import__('imp').find_module('pymysql')
	except ImportError:
		print("To use a MySQL database you need to install "
			  "the `pymysql` python package.  Try `pip install "
			  "pymysql`.")
		sys.exit()
	# internally use `mysql+pymysql://` so sqlalchemy talks to
	# the pymysql package
	DATABASE = DATABASE.replace('mysql://', 'mysql+pymysql://')

engine = create_engine(DATABASE, echo=False, pool_recycle=3600) 
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def object_as_dict(self, filter_these=[]):
    return {c.key: getattr(self, c.key)
        for c in inspect(self).mapper.column_attrs if c.key not in filter_these}

Base.object_as_dict = object_as_dict

def init_db():
    #print "Initalizing db if necessary."
    Base.metadata.create_all(bind=engine)


def truncate_tables():
    for table in Base.metadata.sorted_tables:
        db_session.execute(table.delete(bind=engine))
    db_session.commit()
