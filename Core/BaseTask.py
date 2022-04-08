import time

from Core.HCY import build_request_from_hcy
from Core.sendNotify import notify, mail, save


class BaseTask:
    def __init__(self, task_name, task_entrance, user_name):
        self.task_name = task_name
        self.task_entrance = task_entrance
        notify(f"任务:{task_name}\n"
               f"用户:{user_name}\n"
               f"入口:{task_entrance}\n"
               f"时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

    @staticmethod
    def query_from_cookie(query, cookie):
        _cookie = {}
        for item in cookie.split(";"):
            k = item.split("=")
            if len(k) == 1:
                k, v = k[0], ""
            else:
                k, v = k[0], k[1]
            _cookie[k] = v
        if query in _cookie:
            return _cookie[query]
        else:
            return None

    @staticmethod
    def build_request_from_hcy(hcy: str):
        return build_request_from_hcy(hcy)

    @staticmethod
    def notify(text, end='<br/>'):
        notify(text, end)

    @staticmethod
    def mail(title):
        mail(title)

    @staticmethod
    def save():
        save()
