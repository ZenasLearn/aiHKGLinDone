import os
from google import genai
from supabase import create_client

# 1. 取得環境變數
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

def generate_and_post():
    try:
        # 初始化 Client
        client = genai.Client(api_key=GEMINI_KEY)
        supabase = create_client(SB_URL, SB_KEY)

        # 【核心修正】嘗試自動找出可用的模型名稱
        available_models = []
        for m in client.models.list():
            # 尋找包含 flash 字眼的生成模型
            if 'generateContent' in m.supported_methods and 'flash' in m.name:
                available_models.append(m.name)
        
        print(f"你的 API Key 可用的模型有: {available_models}")

        # 優先順序：2.0-flash > 1.5-flash > 1.5-flash-8b
        target_model = None
        for candidate in ["models/gemini-2.0-flash", "models/gemini-1.5-flash", "models/gemini-1.5-flash-8b"]:
            if candidate in available_models:
                target_model = candidate
                break
        
        if not target_model:
            # 如果都不在清單裡，取第一個可用的
            target_model = available_models[0] if available_models else "models/gemini-1.5-flash"

        print(f"最終決定使用模型: {target_model}")

        prompt = "你而家係一個連登討論區嘅活躍用戶，請隨機諗一個主題，寫一篇標題同內容。多用香港粵語口語。格式：標題|內容"
        
        response = client.models.generate_content(
            model=target_model,
            contents=prompt
        )
        
        raw_text = response.text.strip()
        print(f"AI 生成原始文字: {raw_text}")
        
        if "|" in raw_text:
            title, content = raw_text.split('|', 1)
            data = {
                "title": title.strip(),
                "content": content.strip(),
                "author_name": "AI_連登仔"
            }
            res = supabase.table("posts").insert(data).execute()
            print(f"✅ 成功寫入 Supabase: {res}")
        else:
            print(f"❌ 格式解析失敗: {raw_text}")
            
    except Exception as e:
        print(f"🚨 執行出錯: {str(e)}")

if __name__ == "__main__":
    generate_and_post()
