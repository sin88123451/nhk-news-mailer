import feedparser
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

CATEGORIES = [
    ("トップ",       "https://news.yahoo.co.jp/rss/topics/top-picks.xml"),
    ("国内",         "https://news.yahoo.co.jp/rss/topics/domestic.xml"),
    ("国際",         "https://news.yahoo.co.jp/rss/topics/world.xml"),
    ("経済",         "https://news.yahoo.co.jp/rss/topics/business.xml"),
    ("IT・科学",     "https://news.yahoo.co.jp/rss/topics/it.xml"),
    ("スポーツ",     "https://news.yahoo.co.jp/rss/topics/sports.xml"),
    ("エンタメ",     "https://news.yahoo.co.jp/rss/topics/entertainment.xml"),
]

SENDER    = os.environ["GMAIL_USER"]
PASSWORD  = os.environ["GMAIL_PASSWORD"]
RECIPIENT = os.environ["RECIPIENT_EMAIL"]
TOP_N     = 5
COLOR     = "#ff0033"


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
          <td colspan="2" style="background:{COLOR};color:#fff;padding:10px 16px;
              font-size:15px;font-weight:bold;">Yahoo!ニュース {cat_name}</td>
        </tr>"""
        for i, it in enumerate(items, 1):
            bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            rows += f"""
        <tr style="background:{bg};">
          <td style="padding:10px 16px;font-size:14px;vertical-align:top;width:30px;
              color:#888;">{i}.</td>
          <td style="padding:10px 16px;font-size:14px;vertical-align:top;">
            <a href="{it['link']}" style="color:{COLOR};font-weight:bold;
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
      <td colspan="2" style="background:{COLOR};padding:20px 24px;">
        <div style="color:#fff;font-size:22px;font-weight:bold;">Yahoo!ニュース 朝刊</div>
        <div style="color:rgba(255,255,255,0.8);font-size:13px;margin-top:4px;">{today} 朝6時版</div>
      </td>
    </tr>
    {rows}
    <tr>
      <td colspan="2" style="padding:14px 16px;font-size:12px;color:#aaa;text-align:center;">
        出典：Yahoo!ニュース RSS / 自動配信
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

    if not sections:
        print("ニュース取得なし（RSS変更の可能性）")
        return

    today   = datetime.now().strftime("%Y/%m/%d")
    subject = f"【Yahoo!ニュース】{today} 朝のまとめ"
    html    = build_html(sections)
    send_email(subject, html)
    print(f"送信完了: {subject}")


if __name__ == "__main__":
    main()
