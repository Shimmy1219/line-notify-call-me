from apscheduler.schedulers.blocking import BlockingScheduler
from push_message import push_message
sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def timed_job():
    push_message()

sched.start()