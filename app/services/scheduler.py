from apscheduler.schedulers.background import BackgroundScheduler
from app.services.fetch_image import fetch_latest_image

def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_latest_image, 'interval', hours=0.5)
    scheduler.start()
