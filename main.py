import os
import requests
import json

def get_gemini_news():
    api_key = os.getenv('GEMINI_API_KEY')
    # 切换回更稳定的模型版本
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    # 优化提示词，让它在没有搜索工具时也能尝试给出最新信息
    prompt = """
    你是一名资深的宠物行业分析师。
    请根据你掌握的最新行业动态，整理6条宠物行业的创业与投融资新闻（3条国内，3条国际）。
    
    输出要求：
    1. 必须是【2026年】的最新动态。
    2. 每条包含：【标题】、100字左右【简介】、50字左右【创业点评】。
    3. 重点：PetTech、智能硬件、新品牌。
    4. 必须输出中文。
    """

    # 简化 payload，去掉可能导致报错的 google_search_retrieval 工具
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        result = response.json()
        
        # 核心改进：如果报错，把完整的错误信息发到飞书，方便定位
        if 'candidates' in result:
            content = result['candidates'][0]['content']['parts'][0]['text']
            return content
        else:
            # 这里的 error 会告诉我们是 API Key 错了，还是区域限制了
            error_msg = result.get('error', {}).get('message', '未知错误')
            return f"Gemini 报告了一个错误：{error_msg}"
            
    except Exception as e:
        return f"脚本执行异常：{str(e)}"

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
