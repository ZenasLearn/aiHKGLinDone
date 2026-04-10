import os
from google import genai
from supabase import create_client

# 1. 取得環境變數
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

# 2. 初始化 Client (強制指定 API 版本為 v1，避開 beta 版的 404 Bug)
client = genai.Client(api_key=GEMINI_KEY, http_options={'api_version': 'v1'})

# 3. 初始化 Supabase
supabase = create_client(SB_URL, SB_KEY)

def generate_and_post():
    prompt = "你現在是一個連登討論區的活躍用戶，請隨機想一個主題，寫一篇標題和內容。多用香港粵語口語。格式：標題|內容"
    
    try:
        # 使用最單純的模型名稱
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
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
            print(f"成功寫入 Supabase: {res}")
        else:
            print(f"格式解析失敗: {raw_text}")
            
    except Exception as e:
        print(f"執行出錯: {str(e)}")

if __name__ == "__main__":
    generate_and_post()
