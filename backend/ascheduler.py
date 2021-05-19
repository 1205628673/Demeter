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
        self.callback = None
        self.callback_args = None
        
    def set_run_time(self,runtime):
        self.run_time = runtime
        return self.run_time
    

    def set_callback(self, fn_callback, *args):
        self.callback = fn_callback
        self.callback_args = args

    def stop(self):
        self.state = STATE_STOP

    def ready(self):
        self.state = STATE_READY

class TimeWheelsEventNode:

    def __init__(self, event, due_round):
        self.due_round = due_round
        self.event = event

class LinkedList:

    class LinkedListNode:
        def __init__(self, node = None):
            self.next = None
            self.node = node
    
    class Iterator:
        def __init__(self):
            self.node = None

        def has_next(self):
            return True if self.node.next else False

        def next(self):
            self.node = self.node.next
            return self.node            
        
    def __init__(self):
        self.head = LinkedList.LinkedListNode()
        self.__num = 0

    def add(self, node):
        linkedNode = self.head
        if linkedNode.next == None:
                linkedNode.next = LinkedList.LinkedListNode(node)
        else:
            while linkedNode.next:
                linkedNode = linkedNode.next
            linkedNode.next = LinkedList.LinkedListNode(node)
        self.__num += 1

    def remove(self, index):
        if index < 0 or index > self.__num - 1: 
            raise Exception('out of range in linked list')
        linkedNode = self.head
        i = 0
        while i < index:
            linkedNode = linkedNode.next
        if index == self.__num - 1:
            linkedNode.next = None
        else:
            removedNode = linkedNode.next
            nextNode = removedNode.next
            linkedNode.next = nextNode
        self.__num -= 1
    
    def iterator(self):
        iter = LinkedList.Iterator()
        iter.node = self.head
        return iter

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

class TimeWheels:

    def __init__(self, max_size = 16):
        self.max_size = max_size # time wheels list max size 
        self.circle_list = [LinkedList() for i in range(self.max_size)]
        self.round = 0 # how round of current ,every gone max size of circle list, it will add 1  
        self.current_index = 0 # circle list index of this round

    def set_time_chip_to_event(self, event):
        # less or equals than 0 that mean do event now 
        # greate than 0 ,it mean interval event,we need to compute how round and position time wheels index
        if event.e_interval <= 0:
            target_index = self.current_index + 1
            self.circle_list[target_index].add(TimeWheelsEventNode(event, self.round))
        else:
            event_interval = event.e_interval
            target_index = (self.current_index + event_interval) % self.max_size
            target_round = self.round + (self.current_index + event_interval) // self.max_size
            self.circle_list[target_index].add(TimeWheelsEventNode(event, target_round))

    def increment_current_index(self):
        self.round = self.round + (self.current_index + 1) // (self.max_size)
        self.current_index = (self.current_index + 1) % (self.max_size)

class Scheduler:

    def __init__(self, executor_workers = 10, executor_timeout = 60 * 5):
        self.executor = Executor(max_workers=executor_workers)
        self.event_store = EventStore()
        self.time_wheels = TimeWheels(16)
        self.executor_timeout = executor_timeout
        self.__re_entry_lock = 0
        self.__own_thread_id = None
        self.__interrupted = False

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

    def handle_done_event(self):
        while True:
            # interval of five second to check every event's state in eventstore
            # and remove done event from eventstore  
            time.sleep(5)
            events = self.event_store.get_all_event()
            for event in events:
                if event.e_future != None and event.e_future.done():
                    print(event.e_future.exception())
                    self.event_store.remove_event(event)


    def add_job(self, interval, job, tags=None, *args):
        event = Event(job = job, timeout = self.executor_timeout, interval = interval,tags=tags, args=args)
        self.time_wheels.set_time_chip_to_event(event)
        return event

    def __do_sleep(self, sleep_time):
        time.sleep(sleep_time)

    # handle due event on time wheels chip ,this chip is a linked list,
    # in there we async do due event and remove which due event from chip.
    def handle_chip_due_event(self, chip):
        iter = chip.iterator()
        i = 0
        while iter.has_next():
            time_wheels_event = iter.next()
            if time_wheels_event.node.due_round == self.time_wheels.round:
                event = time_wheels_event.node.event
                self.event_store.add_event(event)
                self.executor.do_job(event)
                if event.e_interval > 0:
                    # if this event is a delay interval event,put in time wheels again
                    self.time_wheels.set_time_chip_to_event(event)
                chip.remove(i)
            i = i + 1

    def __main_loop(self):
        self.re_entry()
        try:
            while not self.__interrupted:
                time_chip = self.time_wheels.circle_list[self.time_wheels.current_index]
                self.handle_chip_due_event(time_chip)
                self.__do_sleep(1)
                self.time_wheels.increment_current_index()
        except Exception():
            print('interrupt...')
        self.out_re_entry()

    def start(self):
        self.__interrupted = False
        start_future = self.executor.start_main_loop(self.__main_loop)
        handle_done_future = self.executor.start_handle_done_event(self.handle_done_event)
        return start_future

    def shutdown(self):
        self.__interrupted = True

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