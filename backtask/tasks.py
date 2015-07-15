#coding:utf-8
from celery import Celery

app = Celery('tasks', backend='amqp', broker='sqla+mysql://root:Dahai1985@localhost:3306/novel?charset=utf8')

app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)


@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y

@app.task
def xsum(numbers):
    return sum(numbers)


if __name__ == '__main__':
    app.start()