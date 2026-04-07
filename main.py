import os
import requests
import json

def get_kimi_analysis():
    api_key = os.getenv('KIMI_API_KEY')
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    # 针对创业者的深度定制指令
    prompt = """
    你是一名宠物行业资深投资分析师。请联网搜索过去24小时内全球宠物行业的【创业与投融资】动态。
    
    输出要求：
    1. 总共提供10条新闻：国内5条，国际5条。
    2. 每条新闻必须包含：
       - 【标题】：简洁明了。
       - 【简介】：100字左右，说明核心事件、商业模式或市场数据。
       - 【分析】：50字左右，从创业者角度评价其创新点或趋势意义。
    3. 语言：中文（海外新闻需翻译）。
    4. 重点关注：PetTech（宠物科技）、新品牌、医疗创新、融资快报。
    """

    payload = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "system", "content": "你是具备强大搜索和摘要能力的行业专家。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3 # 降低随机性，让内容更严谨
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"获取新闻失败，错误原因：{str(e)}"

def send_to_feishu(content):
    webhook = os.getenv('FEISHU_WEBHOOK')
    if not content: return
    
    # 使用富文本格式，防止内容过多被折叠
    data = {
        "msg_type": "text",
        "content": {
            "text": f"📅 【宠物行业创业内参】\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{content}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 建议：点击链接或搜索关键词查看详情。"
        }
    }
    requests.post(webhook, json=data)

if __name__ == "__main__":
    report = get_kimi_analysis()
    send_to_feishu(report)
