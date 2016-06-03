# -*- coding: utf-8 -*-

import conf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import contextlib

# 初始化数据库连接:
connection_str = 'mysql+mysqldb://{0}:{1}@{2}:{3}/{4}?charset={5}'\
                .format(conf.user, conf.passwd, conf.host, conf.port, 
                        conf.scheme, conf.charset)
engine = create_engine(connection_str)
# 创建DBSession类型:
Session = sessionmaker(bind=engine)

@contextlib.contextmanager
def session_scope():
	''' define a context manager for the session '''
	session = Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()