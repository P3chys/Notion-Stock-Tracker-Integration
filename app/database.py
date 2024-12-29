from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import current_app, g

Base = declarative_base()

def get_engine():
    """Create and return a SQLAlchemy engine instance."""
    return create_engine(
        current_app.config['SQLALCHEMY_DATABASE_URI'],
        convert_unicode=True
    )

def init_db(app):
    """Initialize the database and create all tables."""
    with app.app_context():
        engine = get_engine()
        Base.metadata.create_all(bind=engine)

def get_db():
    """Get or create a database session for the current request context."""
    if 'db' not in g:
        engine = get_engine()
        db_session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        )
        Base.query = db_session.query_property()
        g.db = db_session

    return g.db

def close_db(e=None):
    """Close the database session."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Register database functions with the Flask application."""
    app.teardown_appcontext(close_db)