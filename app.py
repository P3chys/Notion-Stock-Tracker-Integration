import click
from flask import Flask
from flask.cli import AppGroup
from config.settings import Settings
from app.database import init_db
import logging
import os

def create_app(test_config=None):
    """Create and configure the Flask application instance."""
    
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE_URL=os.environ.get('DATABASE_URL', 'sqlite:///portfolio.db'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize settings
    settings = Settings.load_from_env()
    app.config['SETTINGS'] = settings

    # Initialize database
    from app.database import init_app
    init_app(app)

    # Register blueprints
    from app.routes import init_app as init_routes
    init_routes(app)

    # Create CLI commands group
    cli_group = AppGroup('portfolio')

    @cli_group.command('init-db')
    def init_db_command():
        """Clear existing data and create new tables."""
        # from app.database import init_db
        init_db(app)
        click.echo('Initialized the database.')

    app.cli.add_command(cli_group)

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    return app

def main():
    """Main entry point for running the application."""
    app = create_app()
    
    # Set up logging for production
    if not app.debug:
        file_handler = logging.FileHandler('portfolio_tracker.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Portfolio Tracker startup')

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()