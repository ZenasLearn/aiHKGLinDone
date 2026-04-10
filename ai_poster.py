import os
from google import genai
from supabase import create_client

# 1. 直接讀取 GitHub Secrets (名稱必須完全對齊 image_299519.png 顯示的名稱)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

# 2. 初始化 Client 與 Supabase
# 這裡不加 http_options，讓 SDK 自行決定最適合 Actions 環境的 v1 版本
client = genai.Client(api_key=GEMINI_KEY)
supabase = create_client(SB_URL, SB_KEY)

def generate_and_post():
    # 核心修正：新版 SDK 在 generate_content 時模型名稱不建議加 'models/' 前綴
    model_id = "gemini-1.5-flash"
    
    prompt = "你而家係一個連登討論區嘅活躍用戶，請隨機諗一個主題，寫一篇標題同內容。多用香港粵語口語。格式：標題|內容"
    
    try:
        print(f"正在連線至 Gemini 使用模型: {model_id}")
        
        # 執行生成
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
            # 寫入資料庫
            res = supabase.table("posts").insert(data).execute()
            print(f"✅ 成功寫入 Supabase: {res}")
        else:
            print(f"❌ 格式解析失敗，請檢查 AI 輸出內容是否符合 '標題|內容'")
            
    except Exception as e:
        # 如果還是 404，這裡會印出 Google 伺服器實際要求的路徑
        print(f"🚨 執行出錯: {str(e)}")

if __name__ == "__main__":
    generate_and_post()
