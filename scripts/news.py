"""
行业资讯推送脚本
通过 Google News RSS 抓取中国电信相关最新新闻，推送到企业微信群
"""
import sys
import os
import json
import urllib.request
import urllib.parse
import re
import datetime
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from webhook import send_text, get_date_str


def fetch_google_news_rss(query, hl="zh-CN", gl="CN", ceid="CN:zh-Hans"):
    """从 Google News RSS 获取新闻"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl={hl}&gl={gl}&ceid={ceid}"

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.read().decode("utf-8")
    except Exception as e:
        print(f"[新闻抓取] Google News RSS 请求失败: {e}")
        return None


def parse_rss_items(xml_text):
    """解析RSS XML，返回新闻列表"""
    items = []
    if not xml_text:
        return items

    try:
        root = ET.fromstring(xml_text)
        channel = root.find("channel")
        if channel is None:
            return items

        for item in channel.findall("item"):
            title = item.find("title")
            link = item.find("link")
            pub_date = item.find("pubDate")
            source = item.find("source")
            description = item.find("description")

            title_text = title.text if title is not None else ""
            link_text = link.text if link is not None else ""
            pub_text = pub_date.text if pub_date is not None else ""
            source_text = source.text if source is not None else ""
            desc_text = description.text if description is not None else ""

            # 清理标题中的来源后缀 (如 " - 新华网")
            title_clean = re.sub(r'\s*-\s*[^-]+$', '', title_text).strip()

            items.append({
                "title": title_clean or title_text,
                "link": link_text,
                "pub_date": pub_text,
                "source": source_text,
                "description": desc_text,
            })
    except Exception as e:
        print(f"[新闻抓取] RSS解析失败: {e}")

    return items


def clean_html(text):
    """去除HTML标签"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    return clean.strip()


def deduplicate(items, existing_titles=None):
    """去重"""
    seen = set()
    result = []
    for item in items:
        title = item["title"]
        if title not in seen:
            seen.add(title)
            if existing_titles is None or title not in existing_titles:
                result.append(item)
    return result


def format_date(pub_date_str):
    """格式化发布日期"""
    if not pub_date_str:
        return ""
    try:
        # Google News RSS 日期格式: "Sat, 09 Aug 2026 08:30:00 GMT"
        dt = datetime.datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S GMT")
        tz = datetime.timezone(datetime.timedelta(hours=8))
        dt_beijing = dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz)
        return dt_beijing.strftime("%m月%d日 %H:%M")
    except:
        try:
            dt = datetime.datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
            tz = datetime.timezone(datetime.timedelta(hours=8))
            dt_beijing = dt.astimezone(tz)
            return dt_beijing.strftime("%m月%d日 %H:%M")
        except:
            return pub_date_str[:16] if len(pub_date_str) > 16 else pub_date_str


def fetch_news(queries, max_items=6):
    """从多个关键词获取新闻并去重"""
    all_items = []
    for query in queries:
        print(f"[新闻抓取] 搜索: {query}")
        xml_text = fetch_google_news_rss(query)
        items = parse_rss_items(xml_text)
        print(f"[新闻抓取] 获取到 {len(items)} 条")
        all_items.extend(items)

    # 去重
    unique_items = deduplicate(all_items)

    # 取前 max_items 条
    return unique_items[:max_items]


def push_news(time_label="早报"):
    """推送行业资讯"""
    date_str = get_date_str()

    # 搜索关键词
    queries = [
        "中国电信",
        "中国电信 5G 云网融合 算力",
        "三大运营商 招标 项目",
    ]

    items = fetch_news(queries, max_items=6)

    if not items:
        # 兜底消息
        message = f"📡 中国电信行业{time_label}\n{date_str}\n" + "━" * 20 + "\n\n"
        message += "今日暂未获取到最新资讯，请关注以下渠道获取行业动态：\n\n"
        message += "1. 中国电信官网: www.chinatelecom.com.cn\n"
        message += "2. C114通信网: www.c114.com.cn\n"
        message += "3. 通信世界: www.cww.net.cn\n"
        message += "\n⚠️ 如持续无推送，请检查GitHub Actions运行日志。"
        send_text(message)
        return

    # 构建消息
    message = f"📡 中国电信行业{time_label}\n{date_str}\n" + "━" * 20 + "\n\n"

    for i, item in enumerate(items, 1):
        title = item["title"]
        source = item["source"] or "网络"
        pub_date = format_date(item["pub_date"])
        desc = clean_html(item["description"])

        # 提取摘要（取描述的前100字）
        summary = desc[:120] + "..." if len(desc) > 120 else desc

        message += f"【{i}】{title}\n"
        message += f"摘要：{summary}\n" if summary else ""
        message += f"来源：{source} | {pub_date}\n\n"

    message += "━" * 20 + "\n"
    message += f"📌 以上为{date_str}最新行业资讯"

    # 分段发送（如果超长）
    if len(message.encode('utf-8')) > 3900:
        # 先发送前半部分
        cut_pos = len(message) * 3900 // len(message.encode('utf-8'))
        while cut_pos > 0 and message[cut_pos] != '\n':
            cut_pos -= 1
        if cut_pos == 0:
            cut_pos = min(len(message), 1300)

        part1 = message[:cut_pos]
        part2 = message[cut_pos:]

        send_text(part1)
        if part2:
            send_text(part2)
    else:
        send_text(message)

    print(f"[新闻推送] {time_label} | {date_str} | 共 {len(items)} 条新闻")


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "早报"
    push_news(label)
