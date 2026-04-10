import os
import google.generativeai as genai
from supabase import create_client

# 1. 設定 API 金鑰 (從 GitHub Secrets 讀取)
GEMINI_KEY = os.getenv("GEMINI_KEY")
SB_URL = os.getenv("SB_URL")
SB_KEY = os.getenv("SB_KEY")

# 2. 初始化 Gemini 與 Supabase
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
supabase = create_client(SB_URL, SB_KEY)

def generate_and_post():
    # 3. 讓 AI 生成連登風格內容
    prompt = "你現在是一個連登討論區的活躍用戶，請隨機想一個關於生活、科技或熱話的主題，寫一篇標題和內容。語言要生動，多用香港粵語口語。輸出格式為：標題|內容"
    
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    
    try:
        title, content = raw_text.split('|', 1)
        # 4. 將內容存入 Supabase
        data = {
            "title": title.strip(),
            "content": content.strip(),
            "author_name": "AI_連登仔"
        }
        supabase.table("posts").insert(data).execute()
        print(f"成功發帖: {title}")
    except Exception as e:
        print(f"解析或儲存失敗: {e}")

if __name__ == "__main__":
    generate_and_post()
