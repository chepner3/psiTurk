from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from psiturk_config import PsiturkConfig
import re, os
import logging

config = PsiturkConfig()
config.load_config()

r = re.compile("OPENSHIFT_(.+)_DB_URL") # Might be MYSQL or POSTGRESQL
matches = filter(r.match, os.environ)
if matches:
    DATABASE = "{}{}".format(os.environ[matches[0]], os.environ['OPENSHIFT_APP_NAME'])
else:
    DATABASE = config.get('Database Parameters', 'database_url')

if 'mysql://' in DATABASE.lower():
	try:
		 __import__('imp').find_module('pymysql')
	except ImportError:
		print("To use a MySQL database you need to install "
			  "the `pymysql` python package.  Try `pip install "
			  "pymysql`.")
		exit()
	# internally use `mysql+pymysql://` so sqlalchemy talks to
	# the pymysql package
	DATABASE = DATABASE.replace('mysql://', 'mysql+pymysql://')

# set up logging
if config.has_option('Database Parameters', 'database_logfile') and config.has_option('Database Parameters', 'database_loglevel'):
	database_logfile = config.get('Database Parameters', 'database_logfile')
	database_loglevel = config.getint('Database Parameters', 'database_loglevel')
	database_handler = logging.FileHandler(database_logfile)
	database_handler.setLevel(database_loglevel)
	database_logger = logging.getLogger('sqlalchemy')
	database_logger.addHandler(database_handler)
	database_logger.setLevel(database_loglevel)

engine = create_engine(DATABASE, echo=False, pool_recycle=3600, pool_pre_ping=True) 
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    #print "Initalizing db if necessary."
    Base.metadata.create_all(bind=engine)
