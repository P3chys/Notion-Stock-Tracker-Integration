import click
from flask import Flask
from app.database import init_db, init_app as init_db_app
from app.services.scheduler import SchedulerService
from config.settings import Settings
from apscheduler.schedulers.background import BackgroundScheduler

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask("__name__")
    
    if test_config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio_tracker.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'dev'
    else:
        app.config.update(test_config)

    # Initialize database
    init_db_app(app)

    # Initialize settings
    settings = Settings.load_from_env()
    app.config['SETTINGS'] = settings

    # Initialize scheduler after database setup
    with app.app_context():
        scheduler = BackgroundScheduler()
        scheduler.start()
        scheduler_service = SchedulerService(scheduler)
        app.config['SCHEDULER_SERVICE'] = scheduler_service

    # Register blueprints
    from app.routes.api import bp as api_bp
    from app.routes import main
    app.register_blueprint(main)
    app.register_blueprint(api_bp)

    @click.command('init-db')
    def init_db_command():
        """Clear existing data and create new tables."""
        init_db(app)
        print('Initialized the database.')