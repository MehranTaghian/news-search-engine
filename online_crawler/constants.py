import logging

seed = [
    'http://www.rajanews.com/rss/all',
    'http://khorasannews.com/newspaper/feed',
    'https://www.irna.ir/rss',
    'https://www.ilna.news/feeds/',
    'https://www.mehrnews.com/rss',
    'https://www.mashreghnews.ir/rss',
    # 'https://fararu.com/fa/rss/allnews',
    # 'https://www.yjc.ir/fa/rss/allnews',
    'https://www.tarafdari.com/category/all/all/feed.xml'
]

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
