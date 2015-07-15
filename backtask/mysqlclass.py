import MySQLdb
from DBUtils.PooledDB import PooledDB


class Mysql(object):
    _pool = None

    def __init__(self):
        self._conn = self.__getconn()
        self._cur = self._conn.cursor()

    def __getconn(self):
        if Mysql._pool is None:
            _pool = PooledDB(creator=MySQLdb, maxconnections=1000, user='root',
                             passwd='Dahai1985', db='novel', charset="utf8")
        return _pool.connection()

    def query(self, sql, param=None):
        self._cur.execute(sql) if param is None else self._cur.execute(sql, param)
        return self._cur.fetchall()

    def insert(self, sql, param=None):
        self._cur.execute(sql) if param is None else self._cur.execute(sql, param)
        self._conn.commit()
        return

    def update(self, sql, param=None):
        self.insert(sql, param)
