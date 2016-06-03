# -*- coding: utf-8 -*-

from sqlalchemy import and_
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

import conf
from dbsession import Session

# create the base class of the object
base = declarative_base()


class UserOrm(base):
    # table name
    __tablename__ = conf.table_user

    # table fields
    id = Column(Integer, primary_key=True)
    user_douban_id = Column(String(255), nullable=False)
    user_name = Column(String(255), nullable=False)

    @classmethod
    def user_exists(cls, douban_id):
        session = Session()
        q = session.query(UserOrm).filter(UserOrm.user_douban_id==douban_id)
        exists = session.query(q.exists()).scalar()
        session.close()
        return exists

    @classmethod
    def fetch_user_id(cls, douban_id):
        session = Session()
        result = session.query(UserOrm.id).filter(UserOrm.user_douban_id==douban_id).one()
        session.close()
        return result[0]

    @classmethod
    def fetch_user_id_and_douban_id(cls):
        session = Session()
        result = session.query(UserOrm.id, UserOrm.user_douban_id).all()
        session.close()
        return result


class MovieOrm(base):
    # table name
    __tablename__ = conf.table_movie

    # table fields
    id = Column(Integer, primary_key=True)
    movie_douban_id = Column(String(255), nullable=False)
    movie_name = Column(String(255), nullable=False)

    @classmethod
    def movie_exists(cls, douban_id):
        session = Session()
        q = session.query(MovieOrm).filter(MovieOrm.movie_douban_id==douban_id)
        exists = session.query(q.exists()).scalar()
        session.close()
        return exists

    @classmethod
    def fetch_movie_id(cls, douban_id):
        session = Session()
        result = session.query(MovieOrm.id).filter(MovieOrm.movie_douban_id==douban_id).one()
        session.close()
        return result[0]


class RelationOrm(base):
    # table name
    __tablename__ = conf.table_relation

    # table fields
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    interest_value = Column(Integer, nullable=False)
    relate_date = Column(Date, nullable=True)


def fetch_user_and_movie_and_interest(user_douban_id=None):
    session = Session()
    if user_douban_id:
        result = session.query(UserOrm.user_douban_id, MovieOrm.movie_name,
            RelationOrm.interest_value).filter(and_(UserOrm.user_douban_id==user_douban_id,
            UserOrm.id==RelationOrm.user_id, MovieOrm.id==RelationOrm.movie_id)).all()
    else:
        result = session.query(UserOrm.user_douban_id, MovieOrm.movie_name,
            RelationOrm.interest_value).filter(and_(UserOrm.id==RelationOrm.user_id,
            MovieOrm.id==RelationOrm.movie_id)).all()
    session.close()
    return result


if __name__ == '__main__':
    print UserOrm.user_exists('146513813')
    print UserOrm.user_exists('tmp')
    print UserOrm.fetch_user_id('146513813')
    print UserOrm.fetch_user_id('tmp')