#coding:utf-8
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Text, DateTime, Boolean, and_, or_,SmallInteger, func
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql://root:Dahai1985@localhost:3306/novel?charset=utf8')
Base = declarative_base()


class Novel(Base):
    __tablename__ = 'novel'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), index=True)
    author = Column(String(20), index=True)
    type = Column(String(20), index=True)
    image = Column(String(80))
    description = Column(Text)
    recommend = Column(Integer, index=True)
    last_update = Column(DateTime, index=True)
    words_count = Column(Integer, index=True)
    source_url = Column(String(120), index=True)
    chapter_source_bequge_url = Column(String(120), index=True)
    chapter_source_ybd_url = Column(String(120), index=True)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(50), index=True)
    password = Column(String(30))
    nickname = Column(String(50), index=True)
    headpic = Column(String(80))
    is_admin = Column(Boolean, default=False)


class Chapter(Base):
    __tablename__ = 'chapter'

    id = Column(Integer, primary_key=True)
    novel_id = Column(Integer, ForeignKey('novel.id'))
    name = Column(String(120))
    url = Column(String(80))
    content = Column(Text)
    last_chapter = Column(Integer)
    next_chapter = Column(Integer)
    '''
    1从一本读上传
    2从笔趣阁上传
    '''
    content_source = Column(SmallInteger, default=1)

    novel = relationship("Novel", backref=backref("chapter"))


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('user.id'))
    to_user_id = Column(Integer, ForeignKey('user.id'))
    from_novel_id = Column(Integer, ForeignKey('novel.id'))
    is_host = Column(Boolean, index=True)
    group_id = Column(Integer)
    content = Column(Text)

    from_user = relationship("User", foreign_keys=[from_user_id], backref=backref("from_user"))
    to_user = relationship("User", foreign_keys=[to_user_id], backref=backref("to_user"))
    from_novel = relationship("Novel", backref=backref("comment"))


db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base.query = db_session.query_property()


if __name__ == '__main__':
    Base.metadata.create_all(engine)