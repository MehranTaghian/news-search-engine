import threading
from math import ceil
from queue import Queue, Empty

from online_crawler.constants import seed, setup_logger


class RoundRobinPolicy:
    pass


class HarmonicPolicy:
    pass


class AtomicCounter:
    def __init__(self, initial=0):
        self.value = initial
        self._lock = threading.Lock()

    def increment(self, num=1):
        with self._lock:
            self.value += num
            return self.value

    def mod(self, num):
        with self._lock:
            self.value %= num
            return self.value

    def reset(self):
        with self._lock:
            self.value = 0
            return self.value


class FrontQueues:

    def __init__(self):
        self.k = 5
        self.front_queues_list = []
        self.host_to_front_queue_mapping = {}
        self.logger = setup_logger('front_queue', 'front_queue.log')

        for i in range(0, self.k):
            self.front_queues_list.append(Queue())

        for i in range(0, len(seed)):
            queue_number = int(i / ceil(len(seed) / self.k))
            self.front_queues_list[queue_number].put(seed[i])
            self.host_to_front_queue_mapping[seed[i]] = self.front_queues_list[queue_number]

        self.current_queue_pointer = AtomicCounter()
        self.current_passed_rounds = AtomicCounter()

    def biased_select(self, policy=HarmonicPolicy, timeout=None):  # policy : 1 , 2 , 3 , 4 , ... , k
        queue = self.front_queues_list[self.current_queue_pointer.value]
        try:
            host = queue.get(timeout=timeout)
            queue.put(host)
        except Empty as e:
            self.current_queue_pointer.increment()
            self.current_queue_pointer.mod(self.k)
            self.current_passed_rounds.reset()
            raise e
        if policy == RoundRobinPolicy:
            self.current_queue_pointer.increment()
            self.current_queue_pointer.mod(self.k)
            return host
        elif policy == HarmonicPolicy:
            self.current_passed_rounds.increment()
            if self.current_passed_rounds.value == self.current_queue_pointer.value + 1:
                self.current_queue_pointer.increment()
                self.current_queue_pointer.mod(self.k)
                self.current_passed_rounds.reset()
            return host
        else:
            self.logger.error('undefined policy')
            raise Exception('undefined policy')

    def optimize(self, host_to_rate):
        i = 0
        changes = {}
        for host, rate in sorted(host_to_rate.items(), key=lambda item: item[1]):
            while True:
                a = self.host_to_front_queue_mapping[host].get()
                if a == host:
                    break
                self.host_to_front_queue_mapping[host].put(host)
            queue_number = int(i / ceil(len(seed) / self.k))
            self.front_queues_list[queue_number].put(host)
            self.host_to_front_queue_mapping[host] = self.front_queues_list[queue_number]
            changes.update({host: (queue_number, rate)})
            i += 1
        # self.logger.info('front queues optimized. ' + str(changes), extra=changes)
