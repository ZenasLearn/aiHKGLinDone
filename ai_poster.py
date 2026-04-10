import os
from google import genai
from supabase import create_client

# 1. 取得環境變數
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

# 2. 初始化 Gemini (明確指定不使用 beta 版)
# 如果你的 SDK 還是報 404，這行是關鍵
client = genai.Client(api_key=GEMINI_KEY)

# 3. 初始化 Supabase
supabase = create_client(SB_URL, SB_KEY)

def generate_and_post():
    # 使用最穩定的模型名稱，不帶任何後綴
    model_id = "gemini-1.5-flash" 
    
    prompt = "你現在是一個連登討論區的活躍用戶，請隨機想一個關於生活、科技或熱話的主題，寫一篇標題和內容。多用香港粵語口語。格式：標題|內容"
    
    try:
        # 呼叫生成
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        raw_text = response.text.strip()
        
        # 檢查是否有內容
        if "|" in raw_text:
            title, content = raw_text.split('|', 1)
            data = {
                "title": title.strip(),
                "content": content.strip(),
                "author_name": "AI_連登仔"
            }
            supabase.table("posts").insert(data).execute()
            print(f"成功發帖: {title}")
        else:
            print(f"AI 輸出格式不符: {raw_text}")
            
    except Exception as e:
        print(f"執行出錯: {e}")

if __name__ == "__main__":
    generate_and_post()
