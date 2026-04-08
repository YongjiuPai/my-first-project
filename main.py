import os
import requests
import json

def get_qwen_analysis():
    api_key = os.getenv('QWEN_API_KEY')
    # 使用阿里云百炼的最新标准接口地址
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    prompt = """
    你是一名宠物行业资深投资分析师。请立刻联网搜索【过去24小时内】全球宠物行业的创业与投融资动态。
    输出要求：
    1. 总共提供6条新闻：国内3条，国际3条。
    2. 每条新闻包含：【标题】、100字左右的【简介】、50字左右的从创业者角度出发的【专业点评】。
    3. 重点关注：宠物科技、智能硬件、新锐品牌、融资快报。
    """

    payload = {
        "model": "qwen-plus", 
        "messages": [
            {"role": "system", "content": "你是具备强大联网搜索能力的行业专家。"},
            {"role": "user", "content": prompt}
        ],
        # 💡 核心修复：在这里开启联网搜索开关
        "extra_body": {
            "enable_search": True
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"获取新闻失败，错误原因：{str(e)}"

def send_to_feishu(content):
    webhook = os.getenv('FEISHU_WEBHOOK')
    if not content: return
    data = {
        "msg_type": "text",
        "content": {"text": f"🚀【Qwen·宠物创业内参】\n\n{content}"}
    }
    requests.post(webhook, json=data)

if __name__ == "__main__":
    report = get_qwen_analysis()
    send_to_feishu(report)
