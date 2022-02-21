from apscheduler.schedulers.blocking import BlockingScheduler
from notify import run_thread
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    run_thread()

sched.start()