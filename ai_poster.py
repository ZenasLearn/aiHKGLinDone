import os
from google import genai
from supabase import create_client

# 1. 取得環境變數 (對齊 GitHub Secrets 名稱)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

def generate_and_post():
    try:
        # 初始化 Client (不強制指定版本，讓 SDK 自動適配)
        client = genai.Client(api_key=GEMINI_KEY)
        supabase = create_client(SB_URL, SB_KEY)

        # 核心修正：嘗試最標準的模型識別碼格式
        target_model = "gemini-1.5-flash"
        
        print(f"正在發送請求至模型: {target_model}")

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
            # 寫入 Supabase
            res = supabase.table("posts").insert(data).execute()
            print(f"✅ 成功寫入 Supabase: {res}")
        else:
            print(f"❌ 格式解析失敗: {raw_text}")
            
    except Exception as e:
        print(f"🚨 執行出錯: {str(e)}")

if __name__ == "__main__":
    generate_and_post()
