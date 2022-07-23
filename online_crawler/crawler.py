import queue

import requests
from collections import defaultdict
import xml.etree.ElementTree as et
from threading import Lock, get_ident, Timer

from online_crawler.back_queue_utils import BackQueues
from online_crawler.constants import seed, setup_logger
from online_crawler.front_queue_utils import FrontQueues

database_name = 'crawled_data.db'
db_table = 'data'

hosts_refresh_rates = {}
timeout = 0.1
lock = Lock()
visited_urls = defaultdict(set)
commit_counter = 5
front_queues = FrontQueues()
back_queues = BackQueues()
front_back_logger = setup_logger('front_queues_link_extraction_back_queues_link_insertion', 'front_back.log')
fetcher_parser_logger = setup_logger('fetch_and_parse', 'fetch_parse.log')


def extract_link_from_front_queue_and_put_in_back_queue():
    while True:
        try:
            host = front_queues.biased_select(timeout=timeout)
            rss = requests.get(url=host)
            root = et.fromstring(rss.content)
            num_of_new_links = 0
            for link, title in zip(root.iter('link'), root.iter('title')):
                if link.text.lower() in seed:
                    continue
                lock.acquire()
                if link.text not in visited_urls[host]:
                    num_of_new_links += 1
                    visited_urls[host].add(link.text)
                    back_queues.add_link(host, link, title)
                lock.release()
            hosts_refresh_rates[get_ident()][host] += num_of_new_links
            # front_back_logger.info('url extracted and put to back queues. ' + host + '  |  ' + str(num_of_new_links),
            #                        extra={'host': host, 'new_links': num_of_new_links})
        except queue.Empty:
            pass


def reorder_front_queues():
    host_to_rate = defaultdict(int)
    for rates in hosts_refresh_rates.values():
        for host, rate in rates.items():
            host_to_rate[host] += rate
            rates[host] = 0

    front_queues.optimize(host_to_rate)
    Timer(5, reorder_front_queues).start()

# def main():
#     conn = sqlite3.connect(database_name)
#     cursor = conn.cursor()
#     cursor.execute('CREATE TABLE IF NOT EXISTS %s (link TEXT PRIMARY KEY, title TEXT, content TEXT)' % db_table)
#     cursor.execute('pragma encoding=UTF8')
#     conn.commit()
#     num_of_extractors = 2
#     num_of_parsers = 1
#
#     for i in range(0, num_of_extractors):
#         thread = Thread(target=extract_link_from_front_queue_and_put_in_back_queue)
#         # thread.daemon = True
#         thread.start()
#         hosts_refresh_rates[thread.ident] = defaultdict(int)
#
#     for i in range(0, num_of_parsers):
#         thread = Thread(target=fetch_and_parse)
#         # thread.daemon = True
#         thread.start()
#
#     Timer(5, reorder_front_queues).start()
#
#
# if __name__ == '__main__':
#     main()
