import os
import requests
import json

def get_groq_news():
    api_key = os.getenv('GROQ_API_KEY')
    url = "https://api.groq.com/openai/v1/chat/completions"

    prompt = """
    你是一名资深的宠物行业分析师。
    请根据你掌握的最新行业动态，整理6条宠物行业的创业与投融资新闻（3条国内，3条国际）。

    输出要求：
    1. 必须是【2026年】的最新动态。
    2. 每条包含：【标题】、100字左右【简介】、50字左右【创业点评】。
    3. 重点：PetTech、智能硬件、新品牌。
    4. 必须输出中文。
    """

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        result = response.json()

        if result.get('choices'):
            content = result['choices'][0]['message']['content']
            return content
        else:
            error_msg = result.get('error', {}).get('message', '未知错误')
            return f"Groq 报告了一个错误：{error_msg}"

    except Exception as e:
        return f"脚本执行异常：{str(e)}"

def send_to_feishu(content):
    webhook = os.getenv('FEISHU_WEBHOOK')
    if not content:
        return
    data = {
        "msg_type": "text",
        "content": {"text": f"🌟【Groq·宠物创业精选】\n\n{content}"}
    }
    requests.post(webhook, json=data)

if __name__ == "__main__":
    report = get_groq_news()
    send_to_feishu(report)
