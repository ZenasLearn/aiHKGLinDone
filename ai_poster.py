import os
import time
from google import genai
from supabase import create_client

# 1. 取得環境變數
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

def generate_and_post():
    # 核心修正：使用你偵測到的可用模型
    target_model = "models/gemini-2.5-flash"
    max_retries = 3  # 最大重試次數
    
    client = genai.Client(api_key=GEMINI_KEY)
    supabase = create_client(SB_URL, SB_KEY)

    for attempt in range(max_retries):
        try:
            print(f"正在嘗試發帖 (第 {attempt + 1} 次)...")
            
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
                print(f"✅ 成功發帖並寫入資料庫！")
                return # 成功後退出函式
            else:
                print(f"❌ 格式錯誤: {raw_text}")
                return

        except Exception as e:
            if "503" in str(e) or "high demand" in str(e):
                print(f"⚠️ 伺服器繁忙 (503)，等待 10 秒後重試...")
                time.sleep(10) # 等待 10 秒
            else:
                print(f"🚨 發生非預期錯誤: {str(e)}")
                break # 其他錯誤則停止重試

if __name__ == "__main__":
    generate_and_post()
