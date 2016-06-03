# -*- coding: utf-8 -*-

from db.orm import UserOrm
from db.dbsession import session_scope
from spiders.user import DoubanUserSpider


def crawl(url):
    spider = DoubanUserSpider(url)
    with session_scope() as session:
        for item in spider.crawl():
            session.add(
                UserOrm(user_douban_id=item[0], user_name=item[1])
            )


if __name__ == '__main__':
    url = 'https://movie.douban.com/subject/25662329/'
    crawl(url)