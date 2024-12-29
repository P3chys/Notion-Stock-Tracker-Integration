from flask import Blueprint, render_template, current_app
from app.portfolio_tracker import PortfolioTracker
from app.database import get_db
from app.models import Schedule

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Serve the main application page with available sources and schedules."""
    # Get portfolio tracker sources
    settings = current_app.config['SETTINGS']
    tracker = PortfolioTracker(settings)
    sources = tracker.get_available_sources()
    
    return render_template('index.html', sources=sources)

def init_app(app):
    """Register blueprints with the Flask application."""
    from app.routes.api import bp as api_bp
    
    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(api_bp)