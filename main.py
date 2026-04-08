import os
import requests
import json

def get_gemini_news():
    api_key = os.getenv('GEMINI_API_KEY')
    # Gemini 的 API 地址
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = """
    你是一名宠物行业资深投资分析师。请立刻使用内置的 Google 搜索功能，查找过去24小时内全球宠物行业的【创业与投融资】动态。
    
    要求：
    1. 提供6条新闻：国内3条，国际3条。
    2. 每条包含：【标题】、100字左右【简介】、50字左右【专业点评】。
    3. 重点关注：PetTech、智能硬件、新品牌、融资快报。
    4. 必须输出中文。
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        # 开启 Google 搜索工具
        "tools": [{"google_search_retrieval": {}}]
    }
    
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        result = response.json()
        # 解析 Gemini 的返回格式
        content = result['candidates'][0]['content']['parts'][0]['text']
        return content
    except Exception as e:
        return f"获取新闻失败，可能需要检查API或网络。报错：{str(e)}"

def send_to_feishu(content):
    webhook = os.getenv('FEISHU_WEBHOOK')
    if not content: return
    data = {
        "msg_type": "text",
        "content": {"text": f"🌟【Gemini·宠物创业精选】\n\n{content}"}
    }
    requests.post(webhook, json=data)

if __name__ == "__main__":
    report = get_gemini_news()
    send_to_feishu(report)
