import os
import requests
import xml.etree.ElementTree as ET
import random

RSS_FEEDS = [
    # 国内
    "https://rss.huxiu.com",
    "https://36kr.com/feed",
    # 国外
    "https://techcrunch.com/feed/",
    "https://venturebeat.com/feed/",
    "https://www.prnewswire.com/news-releases/rss/pet-news-releases.rss",
    "https://www.petfoodindustry.com/Rss",
    "https://www.chinapet365.com/rss/",
    "https://globalpetindustry.com/feed/",
]

PET_KEYWORDS = ["宠物", "猫", "狗", "animal", "pet", "兽医", "动物", "养宠", "宠物食品", "宠物医院"]

SOUP = [
    "🐾 每一个毛孩子都值得被温柔以待。",
    "🐾 养宠不只是责任，更是一场双向奔赴的爱。",
    "🐾 宠物行业的前景，就像毛孩子的笑容一样充满希望。",
    "🐾 今天也是为毛孩子们奋斗的一天！"
]

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

    # 确保只给 AI 最多 6 条，让它严格输出 6 条
    news_text = "\n\n".join([
        f"标题：{n['title']}\n链接：{n['link']}\n简介：{n['desc'][:200]}"
        for n in news_list[:12]  # 给 AI 多一些素材选择
    ])

    prompt = f"""你是一名资深的宠物行业分析师。
以下是从新闻源抓到的宠物相关新闻：

{news_text}

请严格按以下要求输出（中文）：
1. 必须且只能输出【6 条】新闻，不多不少。
2. 每条包含：【标题】、80 字【简介】、40 字【创业点评】。
3. 每条新闻末尾附上原始链接，格式为「📰 来源链接：https://xxx」。
4. 如果新闻不足 6 条，可以加入消费/科技/投资领域与宠物相关的趋势分析来补齐 6 条。
5. 用数字序号标注（1. 2. 3. 4. 5. 6.）。"""

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
        "content": {"text": content}
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
        content = f"🌟【宠物创业精选】\n\n{report}"
    else:
        soup = random.choice(SOUP)
        content = f"🌟【宠物创业精选】\n\n今日未抓取到宠物相关新闻，送上一句：\n\n{soup}"

    send_to_feishu(content)
