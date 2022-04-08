import json
import logging
import os
import threading

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logFormat = logging.Formatter("%(message)s")
stream = logging.StreamHandler()
stream.setFormatter(logFormat)
logger.addHandler(stream)

# 配信内容格式
allMess = ''
mutex = threading.Lock()


def notify(content=None, end='\n'):
    with mutex:
        global allMess
        if isinstance(content, dict):
            content = json.dumps(content, ensure_ascii=False)
        allMess = allMess + content + end
        logger.info(content)


def console() -> None:
    """
    使用 控制台 推送消息。
    """
    if not os.path.exists('log.log'):
        with open('log.log', 'a', encoding='utf-8') as f:
            f.write("")
    with open('log.log', 'r+', encoding='utf-8') as f:
        content_old = f.read()
        f.seek(0, 0)
        f.write(allMess + content_old)


def mail(title: str, subject="树莓派脚本", msg_from="290120506@qq.com", password="",
             msg_to="290120506", smtp_ssl="smtp.qq.com") -> None:
    """
    使用 电子邮箱 推送消息。
    """
    content = allMess.replace('\n', '<br/>')  # 邮件正文内容。
    try:
        print(requests.get(url=f'http://127.0.0.1:8080/send?msg={content}&qq={msg_to}'))
    except BaseException as e:
        print("error when send email", e)


def qq(msg_to, msg=allMess[:-1], host="127.0.0.1"):
    try:
        print(requests.get(url=f'http://{host}:8080/send?msg={msg}&qq={msg_to}'))
    except BaseException as e:
        print("error when send email", e)


def send(title: str, content: str) -> None:
    if not content:
        print(f"{title} 推送内容为空！")
        return
    console()


def save() -> None:
    console()


def main():
    send("title", "content")


if __name__ == "__main__":
    main()
