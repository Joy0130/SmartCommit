import os
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

#載入環境變數.env檔案中的變數
load_dotenv()

#取得Gemini API金鑰
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: 找不到 GEMINI_API_KEY，請檢查.env檔案")
    exit(1)
#設定Gemini API金鑰
genai.configure(api_key=API_KEY)

#建立Gemini模型
#model = genai.GenerativeModel("gemini-2.5-flash")

#使用gemini-3-flash-preview模型
model = genai.GenerativeModel("gemini-3-flash-preview")


#取得Git提交訊息
def get_git_commit_message():
    try:
        #執行git log指令取得最後一筆提交訊息
        result = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True,check=True)
        return result.stdout.strip()

    except subprocess.CalledProcessError:
        print("Error: 這似乎不是一個 git 儲存庫，或者沒有安裝 git。")
        return None

#生成Commit訊息
def generate_commit_message(diff_content):
    if not diff_content:
        return None

    # 限制 diff 長度，避免超過 Token 上限 (取前 3000 字元通常夠判斷)
    if len(diff_content) > 3000:
        diff_content = diff_content[:3000] + "\n...(略)..."

    prompt = f"""
    你是一個資深的軟體工程師。請根據以下的 git diff 內容，生成一個符合 'Conventional Commits' 規範的 commit message。

    規範要求：
    1. 格式為：<type>: <subject>
    2. type 只能是：feat, fix, docs, style, refactor, test, chore, perf,ci,chore,revert,test,build
    3. subject 用繁體中文，簡潔有力，不超過 50 個字。
    4. 不要輸出 Markdown 格式 (如 ```)，只輸出純文字訊息。

    Git Diff 內容：
    {diff_content}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error AI生成失敗: {e}")
        return None

#驗證Commit訊息格式
def validate_commit_message(message):
    """
    驗證commit訊息是否符合Conventional Commits規範
    返回: (is_valid: bool, error_message: str)
    """
    # 定義允許的type類型feat, fix, docs, style, refactor, test, chore, perf,ci,chore,revert,test,build
    allowed_types = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'perf', 'ci' , 'chore' , 'revert' , 'test' , 'build']
    
    # 檢查訊息是否為空
    if not message or not message.strip():
        return False, "commit 訊息不可為空"
    
    # 檢查格式是否為 "type: subject"
    if ':' not in message:
        return False, f"格式錯誤：缺少冒號(:)，正確格式為 <type>: <subject>\n   允許的 type: {', '.join(allowed_types)}"
    
    # 分離type和subject
    parts = message.split(':', 1)
    commit_type = parts[0].strip().lower()
    subject = parts[1].strip() if len(parts) > 1 else ""
    
    # 檢查type是否在允許列表中
    if commit_type not in allowed_types:
        return False, f"type '{commit_type}' 不符合規範\n 允許的 type: {', '.join(allowed_types)}"
    
    # 檢查subject是否為空
    if not subject:
        return False, "subject 不可為空"
    
    return True, ""

#執行主程式
def main():
    # 檢查是否有暫存的變更
    diff = get_git_commit_message()
    if not diff:
        print("message: 沒有偵測到暫存的變更(Staged Changes)，如有變更請先執行 git add")
        return
    print("🤖 AI 正在分析程式碼變更，請稍候...")
    #生成Commit訊息
    commit_msg = generate_commit_message(diff)
    #檢查Commit訊息是否生成成功
    if not commit_msg:
        print("Error: 無法生成 Commit 訊息 (可能是 API 錯誤或 Token 限制)")
        return
    #輸出Commit訊息
    print("\n------------------------------------")
    print(f"📝 建議訊息: {commit_msg}")
    print("------------------------------------")
    
    #詢問使用者操作選項
    while True:
        user_input = input("\n請選擇操作 (y=使用/e=編輯/n=取消): ").lower()
        
        if user_input == 'y':
            # 使用AI生成的訊息提交
            subprocess.run(['git', 'commit', '-m', commit_msg])
            print("✅ 提交成功！")
            break
        elif user_input == 'e':
            # 讓使用者編輯訊息
            print("\n請輸入新的 commit 訊息（按 Enter 確認）:")
            edited_msg = input(f"{commit_msg}\n> ").strip()
            
            # 如果使用者有輸入內容，驗證並使用編輯後的訊息
            if edited_msg:
                # 驗證commit訊息格式
                is_valid, error_msg = validate_commit_message(edited_msg)
                
                if not is_valid:
                    # 格式不正確，顯示錯誤訊息
                    print(f"\n{error_msg}")
                    print("請重新編輯或返回選單...\n")
                    continue
                
                # 格式正確，更新訊息
                commit_msg = edited_msg
                print(f"\n✅ 訊息格式正確！")
                print(f"📝 更新後的訊息: {commit_msg}")
                
                # 再次確認是否提交
                confirm = input("\n是否提交此訊息? (y/n): ").lower()
                if confirm == 'y':
                    subprocess.run(['git', 'commit', '-m', commit_msg])
                    print("✅ 提交成功！")
                    break
                else:
                    print("返回選單...")
                    continue
            else:
                print("⚠️ 訊息不可為空，返回選單...")
                continue
        elif user_input == 'n':
            # 取消提交
            print("已取消。")
            break
        else:
            print("無效的選項，請輸入 y、e 或 n")


if __name__ == "__main__":
    main()