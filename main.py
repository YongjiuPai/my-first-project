import os
import requests
import json

def get_qwen_analysis():
    api_key = os.getenv('QWEN_API_KEY')
    # 核心修复 1：使用百炼最稳定的全兼容接口
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    # 核心修复 2：在提示词开头就强调强制联网
    prompt = """
    # 强制指令：请立即启用内置的联网搜索功能！
    你要搜索并整理【2026年4月】（即过去24小时内）全球宠物行业的创业与投融资动态。
    
    输出要求：
    1. 提供6条新闻：国内3条，国际3条。
    2. 每条包含：【标题】、100字左右【简介】、50字左右从创业者视角出发的【专业点评】。
    3. 重点：宠物科技、智能硬件、新锐品牌、融资快报。
    """

    payload = {
        "model": "qwen-plus", 
        "messages": [
            {"role": "system", "content": "你是一个拥有实时互联网搜索权限的资深行业分析师，必须搜索最新信息。"},
            {"role": "user", "content": prompt}
        ],
        # 核心修复 3：最新的联网开关参数写法
        "extra_body": {
            "enable_search": True
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        # 联网搜索较慢，增加等待时间到 90 秒
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        result = response.json()
        
        # 打印一下结果到日志，方便我们排查
        print(f"API Response: {result}")
        
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            return f"Qwen返回异常：{result.get('error', {}).get('message', '未知错误')}"
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
