from flask import Blueprint, jsonify, request, current_app
from app.database import get_db
from app.models import Schedule
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/schedules', methods=['GET'])
def get_schedules():
    """Retrieve all portfolio update schedules."""
    try:
        db = get_db()
        schedules = db.query(Schedule).all()
        return jsonify({
            'status': 'success',
            'schedules': [schedule.to_dict() for schedule in schedules]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/schedules', methods=['POST'])
def create_schedule():
    """Create a new portfolio update schedule."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        required_fields = ['name', 'schedule_type', 'time', 'selected_sources']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        db = get_db()
        schedule = Schedule(
            name=data['name'],
            schedule_type=data['schedule_type'],
            time=data['time'],
            selected_sources=data['selected_sources'],
            day_of_week=data.get('day_of_week'),
            active=True
        )
        
        db.add(schedule)
        db.commit()

        return jsonify({
            'status': 'success',
            'schedule': schedule.to_dict()
        }), 201

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update an existing portfolio update schedule."""
    try:
        db = get_db()
        schedule = db.query(Schedule).get(schedule_id)
        
        if not schedule:
            return jsonify({
                'status': 'error',
                'message': 'Schedule not found'
            }), 404

        data = request.get_json()
        if 'active' in data:
            schedule.active = data['active']
        if 'name' in data:
            schedule.name = data['name']
        if 'schedule_type' in data:
            schedule.schedule_type = data['schedule_type']
        if 'time' in data:
            schedule.time = data['time']
        if 'day_of_week' in data:
            schedule.day_of_week = data['day_of_week']
        if 'selected_sources' in data:
            schedule.selected_sources = data['selected_sources']

        schedule.updated_at = datetime.utcnow()
        db.commit()

        return jsonify({
            'status': 'success',
            'schedule': schedule.to_dict()
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a portfolio update schedule."""
    try:
        db = get_db()
        schedule = db.query(Schedule).get(schedule_id)
        
        if not schedule:
            return jsonify({
                'status': 'error',
                'message': 'Schedule not found'
            }), 404

        db.delete(schedule)
        db.commit()

        return jsonify({
            'status': 'success',
            'message': 'Schedule deleted successfully'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/run', methods=['POST'])
def run_portfolio_update():
    """Execute an immediate portfolio update with specified sources."""
    try:
        data = request.get_json()
        selected_sources = data.get('sources', [])
        
        if not selected_sources:
            return jsonify({
                'status': 'error',
                'message': 'No sources selected for update'
            }), 400

        settings = current_app.config['SETTINGS']
        from app.portfolio_tracker import PortfolioTracker
        
        tracker = PortfolioTracker(settings)
        tracker.set_active_sources(selected_sources)
        result = tracker.run()

        return jsonify({
            'status': 'success',
            'message': 'Portfolio update completed successfully',
            'details': result
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500