# -*- coding: utf-8 -*-

import re
from Queue import LifoQueue

import requests
from retrying import retry
from scrapy.selector import Selector

import settings

# Xpaths
TABLES_XPATH = '//div[@class="sub_ins"]//table'
FANS_URL_XPATH = './tr[1]/td[2]/div[@class="pl2"]/a/@href'
FANS_NAME_XPATH = './tr[1]/td[2]/div[@class="pl2"]/a/text()'
NEXT_PAGE_XPATH = '//span[@class="next"]/a/@href'


class DoubanUserSpider(object):

    urls_queue = LifoQueue()
    
    def __init__(self, url):
        self.url = url
        self._before_request()

    def _before_request(self):
        self.urls_queue.put({'url':self.url+'collections'})
        self.urls_queue.put({'url':self.url+'wishes'})
    
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def _request(self, url):
        print 'Crawling page ' + url
        session = requests.Session()
        r = session.get(url, headers={'user-agent':settings.USER_AGENT}, 
            timeout=settings.TIMEOUT)
        print 'status_code:', r.status_code
        r.raise_for_status()
        return r.text

    def crawl(self):
        while True:
            if not self.urls_queue.empty():
                req = self.urls_queue.get()
                response = self._request(req['url'])
                for item in self._parse(response):
                    yield item
                # time.sleep(4)
            else:
                print 'finish crawling: ', self.url
                break
    
    def _parse(self, response):
        if response is None:
            return

        selector = Selector(text=response)
        tables = selector.xpath(TABLES_XPATH)
        if len(tables) < 1:
            return
        else:
            for table in tables:
                fans_url = table.xpath(FANS_URL_XPATH).extract_first()
                search = re.search(r'people/(.*?)/', fans_url)
                if search:
                    fans_douban_id = search.group(1)
                else:
                    print 'No fans_url found in fans_url: %s' % fans_url
                    continue

                fans_name = table.xpath(FANS_NAME_XPATH).extract_first()
                fans_name = fans_name.strip() if fans_name is not None else ''

                print fans_douban_id, ' ', fans_name.encode('utf-8')

                yield (fans_douban_id, fans_name)

        next_page_url = selector.xpath(NEXT_PAGE_XPATH)\
            .extract_first()
        print 'next_page: ', next_page_url
        if next_page_url is not None:
            self.urls_queue.put({'url':next_page_url})