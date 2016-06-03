# -*- coding: utf-8 -*-

import re
import time
from Queue import LifoQueue

import requests
from retrying import retry
from scrapy.selector import Selector

from spiders import settings

# base urls
WISH_BASE_URL = 'http://movie.douban.com/people/%s/wish'
DO_BASE_URL = 'http://movie.douban.com/people/%s/do'
COLLECT_BASE_URL = 'http://movie.douban.com/people/%s/collect'

# xpath
MOVIE_ITEMS_XPATH = '//div[@class="item"]'
MOVIE_URL_XPATH = './div[@class="pic"]/a/@href'
MOVIE_NAME_XPATH = './div[@class="info"]/ul/li[@class="title"]/a/em/text()'
COMMENT_DATE_XPATH = './div[@class="info"]//span[@class="date"]/text()'
NEXT_PAGE_XPATH = '//span[@class="next"]/a/@href'

class FansDoubanMovieSpider(object):

    urls_queue = LifoQueue()

    def __init__(self, user_id):
        self.user_id = user_id
        self._before_request()

    def _before_request(self):
        self.urls_queue.put({
            'url': WISH_BASE_URL % self.user_id,
            'interest_value': settings.WISHES}
            )
        self.urls_queue.put({
            'url': COLLECT_BASE_URL % self.user_id,
            'interest_value': settings.COLLECTIONS}
            )

    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def _request(self, url):
        print 'Crawling page ' + url
        r = requests.get(url, headers={'user-agent':settings.USER_AGENT},
            cookies=settings.COOKIES, timeout=settings.TIMEOUT)
        print 'status_code: ', r.status_code
        if r.status_code == 403:
            print 'Spider is sleeping....'
            # time.sleep(1800)
        r.raise_for_status()
        return r.text

    def crawl(self):
        while True:
            if not self.urls_queue.empty():
                req = self.urls_queue.get()
                response = self._request(req['url'])
                for item in self._parse(response, req['interest_value']):
                    yield item
                time.sleep(4)
            else:
                print 'finish crawling: ', self.user_id
                break

    def _parse(self, response, interest_value):
        if response is None:
            return
        selector = Selector(text=response)

        movie_items = selector.xpath(MOVIE_ITEMS_XPATH)

        for item in movie_items:
            movie_url = item.xpath(MOVIE_URL_XPATH)\
                .extract_first()
            search = re.search(r'subject/(.*?)/', movie_url)
            if search:
                movie_id = search.group(1)
            else:
                print 'No movie_id found in %s' % movie_url
                continue

            movie_name = item.xpath(MOVIE_NAME_XPATH)\
                .extract_first()
            movie_name = movie_name.split('/')[0].strip() \
                if movie_name is not None else None
            if movie_name is None:
                print 'No movie_name found in %s' % movie_name.encode('utf-8')
                continue

            comment_date = item.xpath(COMMENT_DATE_XPATH)\
                .extract_first()

            print '%s_%s_%s' % (movie_id, movie_name, comment_date)

            yield (movie_id, movie_name, comment_date, interest_value)

        next_page_url = selector.xpath(NEXT_PAGE_XPATH).extract_first()
        print 'next_page:', next_page_url
        if next_page_url is not None:
            self.urls_queue.put({'url':next_page_url, 'interest_value':interest_value})

if __name__ == '__main__':
    spider = FansDoubanMovieSpider('http://movie.douban.com/people/sayshevaforever/')
    movies = list(spider.crawl())