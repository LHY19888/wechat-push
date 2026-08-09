"""
企业微信群机器人 Webhook 发送工具
"""
import json
import os
import urllib.request
import datetime

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")


def send_text(content):
    """发送文本消息到企业微信群"""
    if not WEBHOOK_URL:
        print("ERROR: WEBHOOK_URL 环境变量未设置")
        return False

    data = json.dumps(
        {"msgtype": "text", "text": {"content": content}},
        ensure_ascii=False
    ).encode("utf-8")

    req = urllib.request.Request(
        WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        if result.get("errcode") == 0:
            print("发送成功:", result)
            return True
        else:
            print("发送失败:", result)
            return False
    except Exception as e:
        print("发送异常:", e)
        return False


def send_markdown(content):
    """发送Markdown消息到企业微信群"""
    if not WEBHOOK_URL:
        print("ERROR: WEBHOOK_URL 环境变量未设置")
        return False

    data = json.dumps(
        {"msgtype": "markdown", "markdown": {"content": content}},
        ensure_ascii=False
    ).encode("utf-8")

    req = urllib.request.Request(
        WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        if result.get("errcode") == 0:
            print("发送成功:", result)
            return True
        else:
            print("发送失败:", result)
            return False
    except Exception as e:
        print("发送异常:", e)
        return False


def get_date_str():
    """获取当前日期字符串（北京时间）"""
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return f"{now.year}年{now.month}月{now.day}日（{weekdays[now.weekday()]}）"


def get_day_of_month():
    """获取今天是几号"""
    tz = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.now(tz).day


if __name__ == "__main__":
    # 测试
    send_text("测试消息 - webhook.py 工作正常")
