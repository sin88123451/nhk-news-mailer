import feedparser
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

CATEGORIES = [
    ("主要ニュース", "https://www3.nhk.or.jp/rss/news/cat0.xml"),
    ("社会",         "https://www3.nhk.or.jp/rss/news/cat1.xml"),
    ("科学・文化",   "https://www3.nhk.or.jp/rss/news/cat2.xml"),
    ("政治",         "https://www3.nhk.or.jp/rss/news/cat3.xml"),
    ("経済",         "https://www3.nhk.or.jp/rss/news/cat4.xml"),
    ("国際",         "https://www3.nhk.or.jp/rss/news/cat5.xml"),
    ("スポーツ",     "https://www3.nhk.or.jp/rss/news/cat6.xml"),
]

SENDER    = os.environ["GMAIL_USER"]
PASSWORD  = os.environ["GMAIL_PASSWORD"]
RECIPIENT = os.environ["RECIPIENT_EMAIL"]
TOP_N     = 5


def fetch_news(url, n=TOP_N):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:n]:
        items.append({
            "title":   entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "link":    entry.get("link", ""),
        })
    return items


def build_html(sections):
    today = datetime.now().strftime("%Y年%m月%d日")
    rows = ""
    for cat_name, items in sections:
        rows += f"""
        <tr>
          <td colspan="2" style="background:#003f88;color:#fff;padding:10px 16px;
              font-size:15px;font-weight:bold;">{cat_name}</td>
        </tr>"""
        for i, it in enumerate(items, 1):
            bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            rows += f"""
        <tr style="background:{bg};">
          <td style="padding:10px 16px;font-size:14px;vertical-align:top;width:30px;
              color:#888;">{i}.</td>
          <td style="padding:10px 16px;font-size:14px;vertical-align:top;">
            <a href="{it['link']}" style="color:#003f88;font-weight:bold;
               text-decoration:none;">{it['title']}</a>
            <div style="color:#555;margin-top:4px;font-size:13px;">{it['summary']}</div>
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#eee;font-family:sans-serif;">
  <table width="640" align="center" cellpadding="0" cellspacing="0"
         style="background:#fff;margin:20px auto;border-radius:8px;overflow:hidden;
                box-shadow:0 2px 8px rgba(0,0,0,.15);">
    <tr>
      <td colspan="2" style="background:#003f88;padding:20px 24px;">
        <div style="color:#fff;font-size:22px;font-weight:bold;">NHK ニュース朝刊</div>
        <div style="color:#aac8ff;font-size:13px;margin-top:4px;">{today} 朝6時版</div>
      </td>
    </tr>
    {rows}
    <tr>
      <td colspan="2" style="padding:14px 16px;font-size:12px;color:#aaa;text-align:center;">
        出典：NHK NEWS WEB RSS / 自動配信
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_email(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER
    msg["To"]      = RECIPIENT
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())


def main():
    sections = []
    for cat_name, url in CATEGORIES:
        items = fetch_news(url)
        if items:
            sections.append((cat_name, items))

    today = datetime.now().strftime("%Y/%m/%d")
    subject = f"【NHKニュース】{today} 朝のまとめ"
    html = build_html(sections)
    send_email(subject, html)
    print(f"送信完了: {subject}")


if __name__ == "__main__":
    main()
