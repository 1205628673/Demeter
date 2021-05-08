from concurrent.futures import ThreadPoolExecutor
import time

STATE_STOP = 1 << 10
STATE_RUNNING = 1 << 11
STATE_SUSPENDING = 1 << 12
STATE_READY = 1 << 13

class Event:

    def __init__(self, job, timeout = None, interval = None,state = STATE_READY, *args):
        self.event_id = str(job)
        self.run_time = 0
        self.e_job = job
        self.args = args
        self.timeout = timeout
        self.e_interval = interval
        self.state = state

    def set_run_time(self,runtime):
        self.run_time = runtime
        return self.run_time
    
    def stop(self):
        self.state = STATE_STOP

    def ready(self):
        self.state = STATE_READY

class EventStore:

    def __init__(self, event_list = [], max_size = 100):
        self.event_list = event_list
    
    def add_event(self, event):
        self.event_list.append(event)
    
    def clear(self):
        self.event_list = []

    def get_event_list(self):
        return self.event_list
    
class Scheduler:

    def __init__(self, executor_workers = 10, executor_timeout = 60 * 5):
        self.executor = Executor(max_workers=executor_workers)
        self.eventStore = EventStore()
        self.executor_timeout = executor_timeout

    def get_due_time_event(self, now_time, event_list):
        due_event_list = []
        for event in event_list:
            if event.run_time < now_time and (event.state == STATE_READY or event.state == STATE_RUNNING):
                due_event_list.append(event)
        return due_event_list
    
    def get_min_time(self, event_list):
        min_time = 1 << 32
        for event in event_list:
            if event.run_time < min_time:
                min_time = event.run_time
        return min_time

    def __set_next_run_time(self, now_time, events):
        for event in events:
            event.run_time = now_time + event.e_interval

    def add_job(self, interval , job, *args):
        event = Event(job = job, timeout = self.executor_timeout, interval = interval)
        self.eventStore.add_event(event)
        return event

    def __do_sleep(self, sleep_time):
        time.sleep(sleep_time)

    def __do_real_start(self):
        now_time = time.time()
        due_event_list = self.get_due_time_event(now_time, self.eventStore.get_event_list())
        for event in due_event_list:
            self.executor.do_job(event.e_job, self.executor_timeout, event.args)
            event.state = STATE_RUNNING
        self.__set_next_run_time(now_time, due_event_list)

    def do_start(self):
        now_time = time.time()
        event_list = self.eventStore.get_event_list()
        self.__set_next_run_time(now_time, event_list)
        while True:
            sleep_time = self.get_min_time(event_list) - time.time()
            if sleep_time >= 0:
                self.__do_sleep(sleep_time)
            self.__do_real_start()

    def start(self):
        self.executor.do_job(self.do_start)
        return 0

class Executor:

    def __init__(self, max_workers = None):
        self.executor = ThreadPoolExecutor(max_workers = max_workers)
    
    def do_job(self, e_job, timeout = None, *args):
        feature = self.executor.submit(e_job, *args)
        #feature.result(timeout) #设置executor异步的超时时间

def test(key):
    print('Test function with asyc background and key:')
if __name__ == '__main__':
    sc = Scheduler()
    sc.add_job(3, test, 'i am a key!')
    sc.start()
    while True:
        print('i am the deamon:\n')
        time.sleep(4)