import os
import requests
import json

def get_qwen_analysis():
    # 从保险箱拿钥匙
    api_key = os.getenv('QWEN_API_KEY')
    # Qwen 的新地址
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    prompt = """
    你是一名宠物行业资深投资分析师。请联网搜索过去24小时内全球宠物行业的【创业与投融资】动态。
    输出要求：
    1. 总共提供6条新闻：国内3条，国际3条。
    2. 每条新闻包含：【标题】、80字左右的【简介】、30字左右的【专业分析】。
    3. 重点关注：宠物科技、新品牌、融资快报。
    """

    payload = {
        "model": "qwen-plus", # 使用通义千问 plus 模型，能力很强
        "messages": [
            {"role": "system", "content": "你是具备强大联网搜索能力的行业专家。"},
            {"role": "user", "content": prompt}
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    # 提取 Qwen 的回答
    if 'choices' in result:
        return result['choices'][0]['message']['content']
    else:
        return f"Qwen老师闹情绪了，错误消息：{result}"

def send_to_feishu(content):
    webhook = os.getenv('FEISHU_WEBHOOK')
    if not content: return
    data = {
        "msg_type": "text",
        "content": {"text": f"🚀【Qwen版·宠物创业内参】\n\n{content}"}
    }
    requests.post(webhook, json=data)

if __name__ == "__main__":
    report = get_qwen_analysis()
    send_to_feishu(report)
