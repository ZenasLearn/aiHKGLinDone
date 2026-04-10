import os
from google import genai
from supabase import create_client

# 1. 取得環境變數
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

# 2. 初始化 Supabase
supabase = create_client(SB_URL, SB_KEY)

def generate_and_post():
    # 這裡我們嘗試最原始的調用方式
    prompt = "你現在是一個連登討論區的活躍用戶，請隨機想一個主題，寫一篇標題和內容。多用香港粵語口語。格式：標題|內容"
    
    # 嘗試不同的 API 版本和路徑組合
    api_configs = [
        {'version': 'v1', 'name': 'gemini-1.5-flash'},
        {'version': 'v1beta', 'name': 'gemini-1.5-flash'}
    ]
    
    last_error = ""
    
    for config in api_configs:
        try:
            print(f"正在嘗試 API 版本: {config['version']}...")
            client = genai.Client(
                api_key=GEMINI_KEY, 
                http_options={'api_version': config['version']}
            )
            
            response = client.models.generate_content(
                model=config['name'],
                contents=prompt
            )
            
            raw_text = response.text.strip()
            print(f"成功！生成原始文字: {raw_text}")
            
            if "|" in raw_text:
                title, content = raw_text.split('|', 1)
                data = {
                    "title": title.strip(),
                    "content": content.strip(),
                    "author_name": "AI_連登仔"
                }
                res = supabase.table("posts").insert(data).execute()
                print(f"成功寫入 Supabase: {res}")
                return # 成功後直接結束
            else:
                print(f"格式解析失敗，原始文字為: {raw_text}")
                return
                
        except Exception as e:
            last_error = str(e)
            print(f"版本 {config['version']} 失敗: {last_error}")
            continue
            
    print(f"❌ 所有嘗試均失敗。最後一個錯誤訊息: {last_error}")

if __name__ == "__main__":
    generate_and_post()
