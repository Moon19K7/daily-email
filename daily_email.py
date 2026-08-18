import smtplib
import requests
import random
import datetime
import os
from email.mime.text import MIMEText
from email.header import Header

# ---------- 配置 ----------
SENDER = os.environ.get("QQ_EMAIL")
PASSWORD = os.environ.get("QQ_AUTH_CODE")
RECEIVER = "wonbeak4@gmail.com"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

# ---------- 寄语 ----------
QUOTES = [
    {"zh": "你不需要把今天过得很厉害，只需要把它过完。", "en": "You do not have to make today remarkable. You only have to live it."},
    {"zh": "安静地开始一天，比用力地开始更好。", "en": "A quiet start is better than a forced one."},
    {"zh": "你今天不需要证明什么。", "en": "You don't have to prove anything today."},
    {"zh": "阅读不是任务，是陪伴。", "en": "Reading is companionship, not a task."},
    {"zh": "慢慢来，比较快。", "en": "Slow is smooth, and smooth is fast."},
    {"zh": "把自己的生活过好就够了。", "en": "It is enough to live your own life well."},
    {"zh": "秋天适合安静地走路。", "en": "Autumn is for quiet walks."},
    {"zh": "语言是通往另一个世界的门。", "en": "Language is a door to another world."},
]

REMINDERS_CN = [
    "今天可以记一点阿语单词。", "今天可以记一点雅思单词。",
    "今天可以读几页书。", "今天写一句日记。",
    "今天注意饮食，少油少盐。", "今天可以听一点播客。",
    "今天可以存下今天的钱。", "今天活动一下身体。",
]
REMINDERS_EN = [
    "Maybe spend a few minutes on Arabic words.", "Maybe review some IELTS vocabulary.",
    "Maybe read a few pages of a book.", "Maybe write a short diary entry.",
    "Pay attention to your food today—light and clean.", "Maybe listen to a podcast.",
    "Put aside today's savings.", "Move your body a little.",
]

BOOKS = ["钱乘旦《目标、路径与方法》", "赵可金《区域国别学》", "齐世荣《世界史（四卷本）》", "彭树智《中东史》（修订本）"]
BOOKS_EN = ["Qian Chengdan: On Area Studies", "Zhao Kejin: Area Studies", "Qi Shirong: World History (4 vols)", "Peng Shuzhi: History of the Middle East"]

PODCASTS = [
    {"name": "《中东现场》", "desc": "深入中东社会与文化，不学术但有趣。", "en": "On the Ground in the Middle East — insightful and easy to listen."},
    {"name": "《忽左忽右》", "desc": "文化、历史、国际关系，常有中东专题。", "en": "Left and Right — culture, history, IR with Middle East episodes."},
    {"name": "《故事FM》", "desc": "普通人的故事，偶尔有中东旅居者的口述。", "en": "StoryFM — personal stories, including from the Middle East."},
    {"name": "《阿拉伯语入门》播客", "desc": "适合碎片时间学一点阿拉伯语。", "en": "Arabic for Beginners — good for short listening."},
]

CLOSINGS = [
    {"zh": "慢一点，也没有关系。", "en": "It is okay to move slowly."},
    {"zh": "把自己的生活过好就够了。", "en": "It is enough to live your own life well."},
    {"zh": "今天也会平静地过去。", "en": "Today will pass peacefully too."},
    {"zh": "你已经在路上了。", "en": "You are already on your way."},
]

def fetch_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?category=general&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("status") != "ok":
            return []
        articles = data.get("articles", [])
        news_list = []
        for a in articles[:5]:
            title = a.get("title", "")
            desc = a.get("description", "")
            if not title:
                continue
            news_list.append({"zh": f"{title}。{desc}" if desc else title, "en": f"{title}. {desc}" if desc else title})
        return news_list
    except:
        return []

def build_email():
    today = datetime.date.today().strftime("%Y年%m月%d日")
    weekday = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][datetime.date.today().weekday()]
    quote = random.choice(QUOTES)
    news = fetch_news()
    if not news:
        news = [{"zh": "今天没有特别重大的国际事件。", "en": "No major international news today."}]
    num_reminders = random.randint(3, 5)
    indices = random.sample(range(len(REMINDERS_CN)), num_reminders)
    reminders_cn = [REMINDERS_CN[i] for i in indices]
    reminders_en = [REMINDERS_EN[i] for i in indices]
    week_num = datetime.date.today().isocalendar()[1]
    book_idx = week_num % len(BOOKS)
    book_cn = BOOKS[book_idx]
    book_en = BOOKS_EN[book_idx]
    podcast_idx = week_num % len(PODCASTS)
    podcast = PODCASTS[podcast_idx]
    closing = random.choice(CLOSINGS)

    html = f"""
    <html>
    <body style="font-family: sans-serif; max-width: 600px; line-height: 1.6; color: #333;">
    <p style="font-size: 14px; color: #999;">{today} {weekday}</p>
    <h2 style="font-weight: normal;">🌅 今日寄语</h2>
    <p><strong>{quote['zh']}</strong></p>
    <p style="color: #666;"><em>{quote['en']}</em></p>
    <hr>
    <h2 style="font-weight: normal;">🌍 我睡着的时候，世界发生了什么</h2>
    <ul>
    """
    for item in news:
        html += f"<li><p><strong>{item['zh']}</strong></p><p style='color: #666;'>{item['en']}</p></li>"
    html += """
    </ul>
    <hr>
    <h2 style="font-weight: normal;">☕ 今天的生活提醒</h2>
    <ul>
    """
    for i in range(len(reminders_cn)):
        html += f"<li><p>{reminders_cn[i]}</p><p style='color: #666;'>{reminders_en[i]}</p></li>"
    html += f"""
    </ul>
    <hr>
    <h2 style="font-weight: normal;">📖 阅读</h2>
    <p>今晚可以翻几页 <strong>{book_cn}</strong></p>
    <p style="color: #666;">Maybe read a few pages of <em>{book_en}</em></p>
    <hr>
    <h2 style="font-weight: normal;">🎧 每周播客</h2>
    <p><strong>{podcast['name']}</strong> — {podcast['desc']}</p>
    <p style="color: #666;"><em>{podcast['en']}</em></p>
    <hr>
    <p style="font-size: 18px;"><strong>{closing['zh']}</strong></p>
    <p style="color: #666;"><em>{closing['en']}</em></p>
    <p style="font-size: 12px; color: #ccc; margin-top: 30px;">每天早晨，轻轻开始。</p>
    </body>
    </html>
    """
    return html

def send_email(html_content):
    msg = MIMEText(html_content, 'html', 'utf-8')
    msg['Subject'] = Header(f"你的每日邮件 · {datetime.date.today().strftime('%m/%d')}", 'utf-8')
    msg['From'] = SENDER
    msg['To'] = RECEIVER
    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, [RECEIVER], msg.as_string())
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print("发送失败:", e)

if __name__ == "__main__":
    content = build_email()
    send_email(content)
