import os
from google import genai
from supabase import create_client

# 1. 取得環境變數 (必須與 GitHub Secrets 完全一致)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

# 2. 初始化 Client
client = genai.Client(api_key=GEMINI_KEY)
supabase = create_client(SB_URL, SB_KEY)

def generate_and_post():
    try:
        model_id = "gemini-1.5-flash"
        prompt = "你而家係一個連登討論區嘅活躍用戶，請隨機諗一個主題，寫一篇標題同內容。多用香港粵語口語。格式：標題|內容"
        
        # 生成內容
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        raw_text = response.text.strip()
        print(f"AI 生成原始文字: {raw_text}")
        
        # 解析格式並存入 Supabase
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
