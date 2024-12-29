from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from datetime import datetime
from app.database import Base

class Schedule(Base):
    """Database model for storing portfolio update schedules."""
    
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    schedule_type = Column(String(20), nullable=False)  # 'daily' or 'weekly'
    time = Column(String(5), nullable=False)  # Format: "HH:MM"
    day_of_week = Column(Integer, nullable=True)  # 0-6 for weekly schedules
    selected_sources = Column(JSON, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert schedule to dictionary format."""
        return {
            'id': self.id,
            'name': self.name,
            'schedule_type': self.schedule_type,
            'time': self.time,
            'day_of_week': self.day_of_week,
            'selected_sources': self.selected_sources,
            'active': self.active,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def create(cls, db_session, name, schedule_type, time, selected_sources, day_of_week=None):
        """Create a new schedule in the database.
        
        Args:
            db_session: SQLAlchemy session
            name (str): Name of the schedule
            schedule_type (str): Type of schedule ('daily' or 'weekly')
            time (str): Time in "HH:MM" format
            selected_sources (list): List of selected source names
            day_of_week (int, optional): Day of week for weekly schedules (0-6)
            
        Returns:
            Schedule: Created schedule instance
        """
        schedule = cls(
            name=name,
            schedule_type=schedule_type,
            time=time,
            selected_sources=selected_sources,
            day_of_week=day_of_week
        )
        db_session.add(schedule)
        db_session.commit()
        return schedule

    def update_last_run(self, db_session):
        """Update the last run timestamp of the schedule.
        
        Args:
            db_session: SQLAlchemy session
        """
        self.last_run = datetime.utcnow()
        db_session.commit()