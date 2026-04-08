import os
import requests
import xml.etree.ElementTree as ET

RSS_FEEDS = [
    # 国内
    "https://rss.huxiu.com",
    "https://36kr.com/feed",
    # 国外
    "https://techcrunch.com/feed/",
    "https://venturebeat.com/feed/",
    "https://www.prnewswire.com/news-releases/rss/pet-news-releases.rss",
    "https://www.petfoodindustry.com/Rss",
]

PET_KEYWORDS = ["宠物", "猫", "狗", "animal", "pet", "兽医", "动物", "养宠", "宠物食品", "宠物医院"]

def fetch_rss(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        items = []
        root = ET.fromstring(r.content)
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            if title and link:
                items.append({"title": title, "link": link, "desc": desc})
        return items
    except Exception:
        return []

def filter_pet_news(items):
    results = []
    seen = set()
    for item in items:
        text = item["title"] + " " + item["desc"]
        if any(kw.lower() in text.lower() for kw in PET_KEYWORDS):
            key = item["link"]
            if key not in seen:
                seen.add(key)
                results.append(item)
    return results

def ai_summarize(news_list):
    api_key = os.getenv('GROQ_API_KEY')
    url = "https://api.groq.com/openai/v1/chat/completions"

    news_text = "\n\n".join([
        f"标题：{n['title']}\n链接：{n['link']}\n简介：{n['desc'][:200]}"
        for n in news_list
    ])

    prompt = f"""你是一名资深的宠物行业分析师。
以下是从新闻源抓到的{len(news_list)}条宠物相关新闻：

{news_text}

请整理并输出（中文）：
1. 每条保留：【标题】、80字【简介】、40字【创业点评】、以及【📰 来源链接】（用原始链接）。
2. 如果没有抓到任何宠物新闻，就基于以上新闻中与消费/科技/投资相关的内容，分析宠物行业可能受益的方向。
3. 每条新闻后附上原始链接。"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=90)
        result = r.json()
        if result.get("choices"):
            return result["choices"][0]["message"]["content"]
        else:
            return f"Groq 错误：{result.get('error', {}).get('message', '未知错误')}"
    except Exception as e:
        return f"请求异常：{e}"

def send_to_feishu(content):
    webhook = os.getenv('FEISHU_WEBHOOK')
    if not content:
        return
    data = {
        "msg_type": "text",
        "content": {"text": f"🌟【宠物创业精选】\n\n{content}"}
    }
    requests.post(webhook, json=data)

if __name__ == "__main__":
    all_items = []
    for feed in RSS_FEEDS:
        all_items.extend(fetch_rss(feed))

    pet_news = filter_pet_news(all_items)
    print(f"共抓取 {len(all_items)} 条新闻，其中宠物相关 {len(pet_news)} 条")

    if pet_news:
        report = ai_summarize(pet_news)
    else:
        report = "今日未抓取到宠物相关新闻。"

    send_to_feishu(report)
