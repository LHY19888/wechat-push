"""
ICT知识推送脚本
根据模块和日期选择主题，通过Webhook推送到企业微信群
"""
import sys
import os

# 将当前目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ict_content import MODULES, get_topic, format_message
from webhook import send_text, get_date_str, get_day_of_month


def push_ict(module_key):
    """推送ICT知识"""
    module = MODULES[module_key]
    date_str = get_date_str()
    day = get_day_of_month()

    topic_content = get_topic(module_key, day)
    message = format_message(module_key, date_str, topic_content)

    # 企业微信群文本消息最多4096字节，如果超长则分段发送
    if len(message.encode('utf-8')) > 3900:
        # 分段发送
        header = f"{module['icon']} ICT{module['name']}\n{date_str}\n" + "━" * 20 + "\n\n"
        send_text(header)
        # 发送正文
        remaining = topic_content
        while len(remaining.encode('utf-8')) > 3900:
            # 找到一个合适的分割点
            cut = len(remaining) * 3900 // len(remaining.encode('utf-8'))
            # 往前找一个换行符
            while cut > 0 and remaining[cut] != '\n':
                cut -= 1
            if cut == 0:
                cut = 3900
            send_text(remaining[:cut])
            remaining = remaining[cut:]
        if remaining:
            send_text(remaining)
    else:
        send_text(message)

    print(f"[ICT推送] 模块={module_key}, 日期={date_str}, 主题序号={day}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python ict_push.py <morning|noon|evening|night>")
        sys.exit(1)

    module_key = sys.argv[1]
    if module_key not in MODULES:
        print(f"错误: 未知模块 '{module_key}'，可选: morning, noon, evening, night")
        sys.exit(1)

    push_ict(module_key)
