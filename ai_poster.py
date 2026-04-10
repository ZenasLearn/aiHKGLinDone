import os
import time
from google import genai
from google.genai import types
from supabase import create_client

# 1. 取得環境變數 (確保與 GitHub Secrets 一致)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SB_URL = os.environ.get("SUPABASE_URL")
SB_KEY = os.environ.get("SUPABASE_KEY")

# 2. 初始化 Client
# 使用你清單中最強大的 gemini-2.5-flash
client = genai.Client(api_key=GEMINI_KEY)
supabase = create_client(SB_URL, SB_KEY)

def generate_news_and_discuss():
    target_model = "models/gemini-2.0-flash"
    
    # --- 第一階段：聯網搵新聞並開 Post ---
    try:
        print("--- 🔍 正在搜尋今日香港熱話 ---")
        search_tool = types.Tool(google_search=types.GoogleSearch())
        
        main_prompt = """
        1. 搜尋今日香港最新鮮、最熱門的新聞或連登討論區話題。
        2. 揀一個最吸引人討論的主題。
        3. 以連登活躍用戶的口語（廣東話、港式術語）寫一個標題同內容。
        4. 格式必須是：標題|內容
        """
        
        # 嘗試生成主貼文
        response = client.models.generate_content(
            model=target_model,
            contents=main_prompt,
            config=types.GenerateContentConfig(tools=[search_tool])
        )
        
        raw_text = response.text.strip()
        print(f"AI 生成主貼文: {raw_text}")
        
        if "|" in raw_text:
            title, content = raw_text.split('|', 1)
            # 寫入 Supabase 並獲取 ID
            post_res = supabase.table("posts").insert({
                "title": title.strip(),
                "content": content.strip(),
                "author_name": "AI_新聞特搜"
            }).execute()
            
            post_id = post_res.data[0]['id']
            print(f"✅ 主貼文發布成功！ID: {post_id}")
            
            # --- 第二階段：模擬其他 AI 角色討論 ---
            print("--- 💬 正在模擬 AI 討論 ---")
            
            # 定義兩個截然不同的性格
            roles = [
                {"name": "連登憤青", "style": "憤世嫉俗，鍾意用『樓主拉』、『垃圾』、『0/10』等字眼，講嘢極短。"},
                {"name": "分析大師", "style": "認真撚，會用長篇大論分析呢件事對香港嘅影響，口語得黎帶點老成。"}
            ]
            
            for role in roles:
                reply_prompt = f"原 Post 內容是：{content}\n你是『{role['name']}』，性格：{role['style']}。請針對內容給出一個符合你性格的簡短回覆。"
                
                # 模擬回覆
                reply_response = client.models.generate_content(
                    model=target_model,
                    contents=reply_prompt
                )
                
                # 寫入 comments 資料表
                supabase.table("comments").insert({
                    "post_id": post_id,
                    "commenter": role['name'],
                    "content": reply_response.text.strip()
                }).execute()
                print(f"✅ 角色 [{role['name']}] 已留言")
                time.sleep(2) # 稍微停頓模擬真實感
                
        else:
            print(f"❌ 格式解析失敗: {raw_text}")

    except Exception as e:
        error_msg = str(e)
        if "503" in error_msg or "high demand" in error_msg:
            print("🚨 伺服器爆載，嘗試進入 30 秒冷卻重試...")
            time.sleep(30)
            # 可以在這裡加入一個 loop 讓他重跑一次 generate_news_and_discuss()
        else:
            print(f"🚨 執行出錯: {error_msg}")

if __name__ == "__main__":
    generate_news_and_discuss()
