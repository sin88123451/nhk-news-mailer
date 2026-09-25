import feedparser
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ─── Google ニュース（日本語トピック別）────────────────────────────────────
GOOGLE_COLOR = "#1a73e8"
GOOGLE_CATEGORIES = [
    ("トップ",       "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"),
    ("国内",         "https://news.google.com/rss/headlines/section/topic/NATION?hl=ja&gl=JP&ceid=JP:ja"),
    ("国際",         "https://news.google.com/rss/headlines/section/topic/WORLD?hl=ja&gl=JP&ceid=JP:ja"),
    ("経済",         "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja"),
    ("テクノロジー", "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja"),
    ("科学",         "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=ja&gl=JP&ceid=JP:ja"),
    ("スポーツ",     "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=ja&gl=JP&ceid=JP:ja"),
]

# ─── Yahoo!ニュース ──────────────────────────────────────────────────────────
YAHOO_COLOR = "#ff0033"
YAHOO_CATEGORIES = [
    ("トップ",   "https://news.yahoo.co.jp/rss/topics/top-picks.xml"),
    ("国内",     "https://news.yahoo.co.jp/rss/topics/domestic.xml"),
    ("国際",     "https://news.yahoo.co.jp/rss/topics/world.xml"),
    ("経済",     "https://news.yahoo.co.jp/rss/topics/business.xml"),
    ("IT・科学", "https://news.yahoo.co.jp/rss/topics/it.xml"),
    ("スポーツ", "https://news.yahoo.co.jp/rss/topics/sports.xml"),
    ("エンタメ", "https://news.yahoo.co.jp/rss/topics/entertainment.xml"),
]

# ─── NHK NEWS WEB（Google News site: フィルター経由）──────────────────────
# 公式 RSS が 2026/08/08 以降更新停止のため代替
NHK_COLOR = "#003f88"
_NHK = "https://news.google.com/rss/search?hl=ja&gl=JP&ceid=JP:ja&q=site:nhk.or.jp+ニュース"
NHK_CATEGORIES = [
    ("主要",     _NHK),
    ("政治",     _NHK + "+政治"),
    ("経済",     _NHK + "+経済"),
    ("国際",     _NHK + "+国際"),
    ("社会",     _NHK + "+社会"),
    ("スポーツ", _NHK + "+スポーツ"),
    ("科学",     _NHK + "+科学"),
]

SENDER    = os.environ["GMAIL_USER"]
PASSWORD  = os.environ["GMAIL_PASSWORD"]
RECIPIENT = os.environ["RECIPIENT_EMAIL"]
TOP_N     = 5


def fetch_news(url, n=TOP_N):
    feed = feedparser.parse(url)
    return [
        {
            "title":   entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "link":    entry.get("link", ""),
        }
        for entry in feed.entries[:n]
    ]


def build_section(label, color, items):
    rows = f"""
        <tr>
          <td colspan="2" style="background:{color};color:#fff;padding:10px 16px;
              font-size:15px;font-weight:bold;">{label}</td>
        </tr>"""
    for i, it in enumerate(items, 1):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        rows += f"""
        <tr style="background:{bg};">
          <td style="padding:10px 16px;font-size:14px;vertical-align:top;width:30px;color:#888;">{i}.</td>
          <td style="padding:10px 16px;font-size:14px;vertical-align:top;">
            <a href="{it['link']}" style="color:{color};font-weight:bold;text-decoration:none;">{it['title']}</a>
            <div style="color:#555;margin-top:4px;font-size:13px;">{it['summary']}</div>
          </td>
        </tr>"""
    return rows


def build_media_header(label, color):
    return f"""
        <tr>
          <td colspan="2" style="background:{color};padding:14px 20px;">
            <div style="color:#fff;font-size:18px;font-weight:bold;letter-spacing:1px;">◆ {label}</div>
          </td>
        </tr>"""


def build_html(google_sections, yahoo_sections, nhk_sections):
    today = datetime.now().strftime("%Y年%m月%d日")
    rows = ""

    rows += build_media_header("Google ニュース（日本語）", GOOGLE_COLOR)
    for cat_name, items in google_sections:
        rows += build_section(f"Google {cat_name}", GOOGLE_COLOR, items)

    rows += """<tr><td colspan="2" style="padding:8px;"></td></tr>"""

    rows += build_media_header("Yahoo!ニュース", YAHOO_COLOR)
    for cat_name, items in yahoo_sections:
        rows += build_section(f"Yahoo! {cat_name}", YAHOO_COLOR, items)

    rows += """<tr><td colspan="2" style="padding:8px;"></td></tr>"""

    rows += build_media_header("NHK NEWS WEB", NHK_COLOR)
    for cat_name, items in nhk_sections:
        rows += build_section(f"NHK {cat_name}", NHK_COLOR, items)

    return f"""<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#eee;font-family:sans-serif;">
  <table width="660" align="center" cellpadding="0" cellspacing="0"
         style="background:#fff;margin:20px auto;border-radius:8px;overflow:hidden;
                box-shadow:0 2px 8px rgba(0,0,0,.15);">
    <tr>
      <td colspan="2" style="background:#222;padding:20px 24px;">
        <div style="color:#fff;font-size:22px;font-weight:bold;">朝の国内ニュース</div>
        <div style="color:#aaa;font-size:13px;margin-top:4px;">{today} 朝6時版　Google + Yahoo! + NHK</div>
      </td>
    </tr>
    {rows}
    <tr>
      <td colspan="2" style="padding:14px 16px;font-size:12px;color:#aaa;text-align:center;">
        出典：Google ニュース / Yahoo!ニュース / NHK NEWS WEB RSS / 自動配信
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
    google_sections = [
        (name, items)
        for name, url in GOOGLE_CATEGORIES
        if (items := fetch_news(url))
    ]
    yahoo_sections = [
        (name, items)
        for name, url in YAHOO_CATEGORIES
        if (items := fetch_news(url))
    ]
    nhk_sections = [
        (name, items)
        for name, url in NHK_CATEGORIES
        if (items := fetch_news(url))
    ]

    if not google_sections and not yahoo_sections and not nhk_sections:
        print("ニュース取得なし")
        return

    today   = datetime.now().strftime("%Y/%m/%d")
    subject = f"【朝刊】{today} Google＋Yahoo!＋NHK"
    html    = build_html(google_sections, yahoo_sections, nhk_sections)
    send_email(subject, html)
    print(f"送信完了: {subject}")


if __name__ == "__main__":
    main()
