from concurrent.futures import ThreadPoolExecutor
import time
import hashlib
import threading
import random
import uuid

STATE_STOP = 1 << 10
STATE_RUNNING = 1 << 11
STATE_SUSPENDING = 1 << 12
STATE_READY = 1 << 13
STATE_DONE = 1 << 14

class Event:

    def __init__(self, job, timeout = None, interval = None,state = STATE_READY,tags=None,args=None):
        self.event_id = str(uuid.uuid4())
        self.e_job = job
        self.args = args
        self.timeout = timeout
        self.e_interval = interval #interval=-1表示只做一次
        self.e_future = None
        self.run_time = time.time() + self.e_interval
        self.state = state
        self.tags = tags
    
    def set_run_time(self,runtime):
        self.run_time = runtime
        return self.run_time
    
    def stop(self):
        self.state = STATE_STOP

    def ready(self):
        self.state = STATE_READY

class EventStore:

    def __init__(self, event_list = list(), max_size = 100):
        self.event_list = event_list
    
    def add_event(self, event):
        self.event_list.append(event)

    def remove_event(self, event):
        event_id = event.event_id
        index = 0
        for i, event in enumerate(self.event_list):
            if event.event_id == event_id:
                index = i
        self.event_list.pop(index)

    def clear_all(self):
        self.event_list = dict()

    def get_event_list(self):
        events = []
        for i,event in enumerate(self.event_list):
            if event != None and event.state == STATE_READY:
                events.append(event)
        return events
    
    def get_all_event(self):
        events = []
        for i,event in enumerate(self.event_list):
            if event != None:
                events.append(event)
        return events

class Scheduler:

    def __init__(self, executor_workers = 10, executor_timeout = 60 * 5):
        self.executor = Executor(max_workers=executor_workers)
        self.eventStore = EventStore()
        self.executor_timeout = executor_timeout
        self.__re_entry_lock = 0
        self.__own_thread_id = None
        self.__main_loop_condition = threading.Condition()

    def re_entry(self):
        if self.__own_thread_id == None:
            self.__re_entry_lock = self.__re_entry_lock + 1
            self.__own_thread_id= threading.currentThread().ident
        elif self.__own_thread_id == threading.currentThread().ident:
            self.__re_entry_lock = self.__re_entry_lock + 1
        else:
            print('current thread with ower thread is not same')
            return 1

    def out_re_entry(self):
        if self.__own_thread_id == threading.currentThread().ident and self.__re_entry_lock > 0:
            self.__re_entry_lock = self.__re_entry_lock - 1
        else:
            print('current thread with ower thread is not same')
            return 1
    # To find now all due event in event_list
    # and job in due event would called by Executor do_job function 
    def get_due_time_event(self, now_time, event_list):
        due_event_list = []
        for event in event_list:
            if event.run_time < now_time and (event.state == STATE_READY):
                due_event_list.append(event)
        return due_event_list
    
    def get_min_time(self, event_list):
        min_time = 1 << 32
        for event in event_list:
            if event.run_time < min_time and event.state == STATE_READY:
                min_time = event.run_time
        if min_time == 1 << 32:
            # if not have event that state was state_ready in event_list
            # set min_time = 0 to sure main_loop don't sleep too long.
            min_time = time.time()
        return min_time

    def __set_next_run_time(self, now_time, events):
        for event in events:
            if event.state == STATE_READY:
                if event.e_interval > 0:
                    event.run_time = now_time + event.e_interval
                else:
                    # if event interval less than 0 ,it mean the event just do once and go to done
                    # set run_time = now time let doing now.
                    event.run_time = time.time() + 1 

    def handle_done_event(self):
        while True:
            # interval of five second to check every event's state in eventstore
            # and remove done event from eventstore  
            time.sleep(5) 
            events = self.eventStore.get_all_event()
            for event in events:
                if event.e_future != None and event.e_future.done():
                    print(event.e_future.exception())
                    if event.e_interval < 0:
                        event.state = STATE_DONE
                        self.eventStore.remove_event(event)
                    else:
                        event.state = STATE_READY


    def add_job(self, interval, job, tags=None, *args):
        event = Event(job = job, timeout = self.executor_timeout, interval = interval,tags=tags, args=args)
        self.eventStore.add_event(event)
        self.__main_loop_condition.acquire()
        self.__main_loop_condition.notify()
        self.__main_loop_condition.release()
        return event

    def __do_sleep(self, sleep_time):
        time.sleep(sleep_time)

    def __do_real_start(self):
        now_time = time.time()
        due_event_list = self.get_due_time_event(now_time, self.eventStore.get_event_list())
        for event in due_event_list:
            self.executor.do_job(event, self.executor_timeout)
            event.state = STATE_RUNNING
        self.__set_next_run_time(now_time, due_event_list)

    def __main_loop(self):
        now_time = time.time()
        self.re_entry()
        interrupted = False
        try:
            while not interrupted:
                event_list = self.eventStore.get_event_list()
                if len(event_list) == 0:
                    print('not find ready event,take a nip wait for notify from add_job ')
                    self.__main_loop_condition.acquire()
                    self.__main_loop_condition.wait()
                    self.__main_loop_condition.release()
                    continue
                sleep_time = self.get_min_time(event_list) - time.time()
                if sleep_time > 0:
                    self.__do_sleep(sleep_time)
                self.__do_real_start()
        except KeyboardInterrupt():
            interrupted = True
            print('interrupt...')
        self.out_re_entry()

    def start(self):
        start_future = self.executor.start_main_loop(self.__main_loop)
        handle_done_future = self.executor.start_handle_done_event(self.handle_done_event)
        return 0

class Executor:

    def __init__(self, max_workers = None):
        self.executor = ThreadPoolExecutor(max_workers = max_workers)
            
    def start_main_loop(self, fn_main_loop, *args):
        future = self.executor.submit(fn_main_loop, *args)
        return future

    def start_handle_done_event(self, fn_handle_done_event):
        future = self.executor.submit(fn_handle_done_event)
        return future
        
    def do_job(self, event, timeout = None):
        e_job = event.e_job
        args = event.args
        # according given number of arguments to choose whether addition args on submit funcion  
        if args:
            future = self.executor.submit(e_job, *args)
        else:
            future = self.executor.submit(e_job)
        event.e_future = future
        #feature.result(timeout) # set executor asyc timeout 
        #feature.add_done_callback() # bind event callback function

def test1(key):
    print('start 1')
    time.sleep(5)
    print('Test function with asyc background and identify:1')
def test2(key,k2):
    print('start 2')
    print(key)
    print(k2)
    time.sleep(5)
    print('Test function with asyc background and identify:2')

if __name__ == '__main__':
    sc = Scheduler()
    #sc.add_job(3, test1, 'i am a key!')
    f = sc.start()
    sc.add_job(-1, test2,'t','hello','done')
    while True:
        print('i am the deamon:\n')
        time.sleep(1)
        if f.done():
            print(f.exception())