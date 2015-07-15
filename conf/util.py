import ConfigParser
import os
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"}


conf = ConfigParser.ConfigParser()
path = os.path.join(os.path.dirname(__file__), "local_test.conf")
conf.read(path)

sql_user = conf.get('sql', 'user')
sql_password = conf.get('sql', 'password')


class MeinvException(Exception):
    def __init__(self, msg, url):
        self.msg = msg
        self.url = url


if __name__ == '__main__':
    print sql_password
