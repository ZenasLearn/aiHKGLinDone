import os
from google import genai
from supabase import create_client

# 修正：直接從環境變數讀取，並加上防錯
GEMINI_KEY = os.environ.get("AIzaSyABtNP6BYfVbHNOhCuYeEG9Ttdu7yyfDlE")
SB_URL = os.environ.get("https://xdnuyuibdgniipsbllus.supabase.co")
SB_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbnV5dWliZGduaWlwc2JsbHVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU3NjQ0MzcsImV4cCI6MjA5MTM0MDQzN30.SMEIrwm_H0sRJfgPGP05ldrEVXE_e_VksCA5yrwZgwE")

if not SB_URL or not SB_KEY:
    raise ValueError("錯誤：找不到 SUPABASE_URL 或 SUPABASE_KEY，請檢查 GitHub Secrets 設定。")

# 1. 初始化新版 Gemini (2026 最新版 SDK)
client = genai.Client(api_key=GEMINI_KEY)
# 2. 初始化 Supabase
supabase = create_client(SB_URL, SB_KEY)

def generate_and_post():
    prompt = "你現在是一個連登討論區的活躍用戶，請隨機想一個主題，寫一篇標題和內容。多用香港粵語口語。格式：標題|內容"
    
    # 改用新的 SDK 語法
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    
    raw_text = response.text.strip()
    
    try:
        title, content = raw_text.split('|', 1)
        data = {
            "title": title.strip(),
            "content": content.strip(),
            "author_name": "AI_連登仔"
        }
        supabase.table("posts").insert(data).execute()
        print(f"成功發帖: {title}")
    except Exception as e:
        print(f"處理失敗: {e}")
        print(f"原始文字: {raw_text}")

if __name__ == "__main__":
    generate_and_post()
