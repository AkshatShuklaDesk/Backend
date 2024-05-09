from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import constants
from sshtunnel import SSHTunnelForwarder
load_dotenv()

if 1:
    server = SSHTunnelForwarder(
        ('43.252.197.60', 22),
        ssh_password="rcc@5661",
        ssh_username="jeet",
        remote_bind_address=('127.0.0.1', 5432))

    server.start()

    # engine = create_engine('mysql+mysqldb://user:pass@127.0.0.1:%s/db' % server.local_bind_port)

    # SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    # SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://utzuah2jbuhnlxmm:jzGBXrUt00lDeA1g5qcS@bf8t56knvv0cagblos75-mysql.services.clever-cloud.com:3306/bf8t56knvv0cagblos75"
    SQLALCHEMY_DATABASE_URL = f"postgresql://{constants.id}:{constants.password}@127.0.0.1:{server.local_bind_port}/{constants.db_name}"
    # SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{'dbroot'}:{'dbroot'}@localhost:{constants.port}/{constants.db_name}"
else:
    SQLALCHEMY_DATABASE_URL = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
