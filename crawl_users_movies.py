# -*- coding: utf-8 -*-

from spiders.movie import FansDoubanMovieSpider
from db.orm import UserOrm, MovieOrm, RelationOrm
from db.dbsession import session_scope


def crawl(ids):
    movie_id_cache = dict()
    for id in ids:
        user_id = id[0]
        spider = FansDoubanMovieSpider(id[1])
        for item in spider.crawl():
            if not MovieOrm.movie_exists(item[0]):
                with session_scope() as session:
                    session.add(
                        MovieOrm(movie_douban_id=item[0], movie_name=item[1])
                    )
            if item[0] not in movie_id_cache:
                movie_id_cache[item[0]] = MovieOrm.fetch_movie_id(item[0])
            movie_id = movie_id_cache[item[0]]
            with session_scope() as session:
                session.add(
                    RelationOrm(movie_id=movie_id, user_id=user_id,
                        interest_value=item[3], relate_date=item[2])
                )


if __name__ == '__main__':
    ids = UserOrm.fetch_user_id_and_douban_id()
    crawl(ids)

