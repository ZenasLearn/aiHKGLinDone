import os
import time
from google import genai
from supabase import create_client

# 取得環境變數
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

def generate_and_post():
    # 定義備選模型清單，按優先級排序
    models_to_try = ["models/gemini-2.5-flash", "models/gemini-2.0-flash"]
    max_retries = 5  # 增加重試次數
    
    client = genai.Client(api_key=GEMINI_KEY)
    supabase = create_client(SB_URL, SB_KEY)

    for model_id in models_to_try:
        print(f"--- 嘗試使用模型: {model_id} ---")
        for attempt in range(max_retries):
            try:
                print(f"嘗試次數: {attempt + 1}/{max_retries}")
                
                prompt = "你而家係一個連登討論區嘅活躍用戶，請隨機諗一個主題，寫一篇標題同內容。多用香港粵語口語。格式：標題|內容"
                
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                
                raw_text = response.text.strip()
                if "|" in raw_text:
                    title, content = raw_text.split('|', 1)
                    data = {
                        "title": title.strip(),
                        "content": content.strip(),
                        "author_name": "AI_連登仔"
                    }
                    supabase.table("posts").insert(data).execute()
                    print(f"✅ 成功！使用 {model_id} 寫入 Supabase")
                    return 
                
            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg or "high demand" in error_msg:
                    wait_time = (attempt + 1) * 5 # 遞增等待時間
                    print(f"⚠️ 伺服器繁忙，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                else:
                    print(f"🚨 其他錯誤: {error_msg}")
                    break # 換下一個模型試試

    print("❌ 所有模型及重試次數皆已耗盡。")

if __name__ == "__main__":
    generate_and_post()
