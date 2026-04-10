import os
from google import genai
from supabase import create_client

# 1. 取得環境變數
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

def generate_and_post():
    try:
        # 【核心修正】強制指定使用 v1 穩定版 API，不讓它亂跑 v1beta
        client = genai.Client(
            api_key=GEMINI_KEY,
            http_options={'api_version': 'v1'}
        )
        supabase = create_client(SB_URL, SB_KEY)

        # 在 v1 API 中，直接使用名稱即可
        target_model = "gemini-1.5-flash"
        
        print(f"正在強制使用 v1 API 連線至: {target_model}")

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
            print(f"✅ 成功寫入 Supabase")
        else:
            print(f"❌ 解析失敗: {raw_text}")
            
    except Exception as e:
        print(f"🚨 執行出錯: {str(e)}")

if __name__ == "__main__":
    generate_and_post()
