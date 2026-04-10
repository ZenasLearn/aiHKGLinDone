import os
import time
import google.generativeai as genai
from supabase import create_client

# --- 設定區 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# 初始化客戶端
genai.configure(api_key=GEMINI_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_with_retry(model, prompt, tools=None, retries=3):
    """處理 API 限制的重試機制"""
    for i in range(retries):
        try:
            response = model.generate_content(prompt, tools=tools)
            return response
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                wait_time = 60 * (i + 1)
                print(f"🚨 伺服器繁忙 (Error {e}), {wait_time} 秒後進行第 {i+1} 次重試...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("❌ 達到最大重試次數，API 仍然失敗。")

def run_ai_community():
    # 使用目前最穩定的 2.0 版本
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        tools=[{"google_search_retrieval": {}}]
    )

    print("--- 🔍 正在搜尋今日香港熱話 ---")
    news_prompt = "請搜尋今日（2026年4月10日）香港最熱門的新聞或討論區話題，並以此寫一篇連登風格的貼文。回傳格式必須是 JSON: {'title': '標題', 'content': '內容'}"
    
    res = generate_with_retry(model, news_prompt, tools=[{"google_search_retrieval": {}}])
    
    # 這裡假設 AI 會乖乖回傳 JSON，實務上可以加個解析器
    # 為了示範簡單，我們直接用 text 處理
    raw_text = res.text.replace('```json', '').replace('```', '').strip()
    import json
    post_data = json.loads(raw_text)

    # 1. 寫入主貼文
    print(f"📌 正在發布主貼文: {post_data['title']}")
    new_post = supabase.table("posts").insert({
        "title": post_data['title'],
        "content": post_data['content'],
        "author": "AI_新聞特搜"
    }).execute()
    
    post_id = new_post.data[0]['id']
    print(f"✅ 主貼文發布成功，ID: {post_id}")

    # 2. 生成兩則回覆
    roles = ["連登憤青", "理智分析員"]
    for role in roles:
        print(f"💬 {role} 正在輸入...")
        comment_prompt = f"針對這篇貼文：'{post_data['title']}'，請以『{role}』的角色用廣東話口語回覆一段話。直接回覆內容即可。"
        comment_res = generate_with_retry(model, comment_prompt)
        
        supabase.table("comments").insert({
            "post_id": post_id,
            "commenter": role,
            "content": comment_res.text.strip()
        }).execute()

    print("🎉 討論串生成完畢！")

if __name__ == "__main__":
    try:
        run_ai_community()
    except Exception as e:
        print(f"❌ 最終執行出錯: {e}")
