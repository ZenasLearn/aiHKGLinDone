import os
from google import genai
from supabase import create_client

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

def debug_and_post():
    try:
        # 使用最基礎的初始化
        client = genai.Client(api_key=GEMINI_KEY)
        
        print("--- 🔍 開始偵錯模型清單 ---")
        # 列出所有該 API Key 可以使用的模型
        available_models = []
        for m in client.models.list():
            available_models.append(m.name)
            print(f"找到可用模型: {m.name}")
        
        if not available_models:
            print("🚨 警告：此 API Key 找不到任何可用模型！請檢查 AI Studio 權限。")
            return

        # 優先選擇清單中存在的模型
        target = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
        print(f"--- 🚀 嘗試使用模型: {target} ---")

        response = client.models.generate_content(
            model=target,
            contents="你好，請簡單回覆：測試成功"
        )
        print(f"✅ 生成成功: {response.text}")
        
        # (Supabase 部分暫時保留，先確認 Gemini 能通)
        
    except Exception as e:
        print(f"🚨 偵錯過程出錯: {str(e)}")

if __name__ == "__main__":
    debug_and_post()
