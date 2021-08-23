# -*- coding: utf-8 -*-
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


"""This function is a decorator that can be used to define a factory function for with statement context managers, 
   without needing to create a class or separate __enter__() and __exit__() methods."""


@contextmanager
def db_session(db_url):
    """ Creates a context with an open SQLAlchemy session.
    """
    engine = create_engine(db_url, convert_unicode=True, echo=False, connect_args={'check_same_thread': False})

    '''if echo = True, the Engine will log all
    statements as well as a repr() of their parameter lists to the engines logger'''

    '''if set convert_unicode to True, sets the default behavior of convert_unicode on the String type to True'''

    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))

    # todo: 注意ProgrammingError: Thread error in SQLAlchemy
    # app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    # db = SQLAlchemy(app)
    # db_session = db.session

    yield db_session  # like __exit__() methods.
    db_session.close()
    connection.close()

