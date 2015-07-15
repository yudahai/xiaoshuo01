#coding:utf-8
import threading
import logging

#logging设置
console = logging.StreamHandler()
console.setLevel(logging.WARN)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

#headers信息，防止网站要求agent
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"}

#生产者，消费者模型
def produce_consume(threads, MAX_THREADS=50):
    running_threads = []
    condition = threading.Condition()

    def produce():
        while threads:
            condition.acquire()
            if len(running_threads) > MAX_THREADS:
                condition.wait()
            t = threads.pop()
            t.start()
            running_threads.append(t)
            condition.release()

    def consume():
        while True:
            condition.acquire()
            [running_threads.remove(t) for t in running_threads if not t.isAlive()]
            if len(running_threads) < MAX_THREADS:
                condition.notify()
            condition.release()
            if len(running_threads) == 0:
                break

    t_produce = threading.Thread(target=produce)
    t_consume = threading.Thread(target=consume)

    t_produce.start()
    t_consume.start()

    t_produce.join()
    t_consume.join()
