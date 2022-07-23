import datetime
import heapq
from queue import Queue, Empty
from threading import Lock

from online_crawler.constants import seed


class BackQueues:

    def __init__(self):
        self.b = len(seed)
        self.back_queues_list = []
        self.mapping = {}
        self.heap = []
        self.lock = Lock()
        self.timeout = 1

        for i in range(0, self.b):
            site = seed[i]
            self.mapping[site] = Queue()
            self.heap.append((datetime.datetime.now(), site))

        heapq.heapify(self.heap)

    def get_url(self):
        self.lock.acquire()
        submit_request_time, site = heapq.heappop(self.heap)
        self.lock.release()
        if submit_request_time > datetime.datetime.now():
            self.lock.acquire()
            heapq.heappush(self.heap, (submit_request_time, site))
            self.lock.release()
            return None, None
        else:
            back_queue = self.mapping[site]
            try:
                url, title = back_queue.get(timeout=self.timeout)
                self.lock.acquire()
                heapq.heappush(self.heap,
                               (datetime.datetime.now() + datetime.timedelta(seconds=4), site))  # todo remove 2
                self.lock.release()
                return url, title
            except Empty:
                self.lock.acquire()
                heapq.heappush(self.heap,
                               (datetime.datetime.now() + datetime.timedelta(seconds=4), site))  # todo remove 2
                self.lock.release()
                return None, None

    def add_link(self, host, link, title):
        self.mapping[host].put((link.text, title.text))
