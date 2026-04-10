import os
from google import genai
from supabase import create_client

# 1. 取得環境變數 (確保與你的截圖 GEMINI_API_KEY 一致)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

# 初始化
client = genai.Client(api_key=GEMINI_KEY)
supabase = create_client(SB_URL, SB_KEY)

def generate_and_post():
    # 這裡的寫法微調：確保它是最乾淨的 ID
    model_id = 'gemini-1.5-flash' 
    
    prompt = "你現在是一個連登用戶，請想一個主題發帖。必須嚴格遵守此格式輸出：標題|內容。語言：香港粵語。"
    
    try:
        # 修正：直接呼叫 generate
        response = client.models.generate_content(
            model=model_id,
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
        # 如果還是 404，這裡會印出詳細原因
        print(f"執行出錯: {str(e)}")

if __name__ == "__main__":
    generate_and_post()
