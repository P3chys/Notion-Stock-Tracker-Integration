from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
from app.database import get_db
from app.models import Schedule

class SchedulerService:
    def __init__(self, scheduler=None):
        """Initialize the scheduler service."""
        self.scheduler = scheduler if scheduler else BackgroundScheduler()
        if not scheduler:
            self.scheduler.start()
        try:
            self._load_schedules()
        except RuntimeError:
            # Skip loading schedules if outside application context
            pass

    def _load_schedules(self):
        """Load and initialize all active schedules from the database."""
        db = get_db()
        active_schedules = db.query(Schedule).filter_by(active=True).all()
        
        for schedule in active_schedules:
            self._add_job(schedule)

    def _add_job(self, schedule):
        """Add a job to the scheduler based on schedule configuration."""
        job_id = f"portfolio_update_{schedule.id}"
        
        if schedule.schedule_type == 'daily':
            hour, minute = map(int, schedule.time.split(':'))
            self.scheduler.add_job(
                self._run_portfolio_update,
                trigger=CronTrigger(hour=hour, minute=minute),
                id=job_id,
                args=[schedule.id],
                replace_existing=True
            )
        elif schedule.schedule_type == 'weekly':
            hour, minute = map(int, schedule.time.split(':'))
            self.scheduler.add_job(
                self._run_portfolio_update,
                trigger=CronTrigger(
                    day_of_week=schedule.day_of_week,
                    hour=hour,
                    minute=minute
                ),
                id=job_id,
                args=[schedule.id],
                replace_existing=True
            )

    def _run_portfolio_update(self, schedule_id):
        """Execute a portfolio update for a specific schedule."""
        with current_app.app_context():
            db = get_db()
            schedule = db.query(Schedule).get(schedule_id)
            
            if not schedule or not schedule.active:
                return
                
            try:
                settings = current_app.config['SETTINGS']
                from app.portfolio_tracker import PortfolioTracker
                
                tracker = PortfolioTracker(settings)
                tracker.set_active_sources(schedule.selected_sources)
                tracker.run()
                
                schedule.last_run = db.func.now()
                db.commit()
                
            except Exception as e:
                print(f"Error running scheduled update for schedule {schedule_id}: {str(e)}")

    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()