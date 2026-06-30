"""Core functionality for aicommit-cli."""

import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 直接引用新版 SDK，不要放在 try 裡面，如果沒裝就讓它報錯
from google import genai

# 載入 .env
# 策略：優先讀取使用者當前執行目錄下的 .env，其次讀取安裝目錄下的 .env
current_dir_env = Path.cwd() / '.env'
package_dir_env = Path(__file__).parent.parent / '.env'

if current_dir_env.exists():
    load_dotenv(current_dir_env)
elif package_dir_env.exists():
    load_dotenv(package_dir_env)

API_KEY = os.getenv("GEMINI_API_KEY")

def get_api_key():
    """取得 Gemini API 金鑰。"""
    if not API_KEY:
        print("❌ Error: 找不到 GEMINI_API_KEY")
        print("請在當前目錄建立 .env 檔案，內容：GEMINI_API_KEY=你的金鑰")
        return None
    return API_KEY

def get_git_diff():  # 這裡建議改名，因為它抓的是 Diff 不是 Message
    """取得Git暫存區的變更(Diff)。"""
    try:
        # 執行 git diff --staged
        result = subprocess.run(
            ["git", "diff", "--staged"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # 這通常代表不是 git 專案
        return None
    except FileNotFoundError:
        print("❌ 錯誤：找不到 git 指令，請確認已安裝 git。")
        return None

def _smart_truncate_diff(diff_content: str, max_chars: int) -> str:
    """智慧截斷 diff：優先保留 +/- 實際變更行，壓縮多餘的 context 行。"""
    lines = diff_content.splitlines(keepends=True)
    result = []
    total = 0
    skipped_hunks = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # diff 標頭行（diff --git / index / --- / +++）一律保留
        if line.startswith(('diff --git', 'index ', '--- ', '+++ ', 'new file', 'deleted file', 'rename ')):
            chunk = line
            if total + len(chunk) <= max_chars:
                result.append(chunk)
                total += len(chunk)
            i += 1
            continue

        # hunk 標頭行（@@ ... @@）
        if line.startswith('@@'):
            hunk_header = line
            hunk_lines = []
            i += 1
            # 收集此 hunk 的所有行
            while i < len(lines) and not lines[i].startswith(('@@', 'diff --git')):
                hunk_lines.append(lines[i])
                i += 1

            # 分離：changed 行 vs context 行
            changed = [l for l in hunk_lines if l.startswith(('+', '-'))]
            context = [l for l in hunk_lines if not l.startswith(('+', '-'))]

            # 估算只保留 changed 行的大小
            hunk_cost = len(hunk_header) + sum(len(l) for l in changed)

            if total + hunk_cost > max_chars:
                # 已超出上限，記錄跳過的 hunk 數
                skipped_hunks += 1
                continue

            # 還有空間，嘗試加入 context 行
            result.append(hunk_header)
            total += len(hunk_header)

            for hunk_line in hunk_lines:
                is_changed = hunk_line.startswith(('+', '-'))
                cost = len(hunk_line)
                if is_changed:
                    # 變更行一律保留
                    result.append(hunk_line)
                    total += cost
                else:
                    # context 行：有空間才加
                    if total + cost <= max_chars:
                        result.append(hunk_line)
                        total += cost
                    # else: 跳過此 context 行，不影響變更行的完整性
            continue

        # 其他行直接保留（不常見）
        if total + len(line) <= max_chars:
            result.append(line)
            total += len(line)
        i += 1

    truncated = ''.join(result)
    if skipped_hunks > 0:
        truncated += f"\n\n...(因 diff 過大，已略過 {skipped_hunks} 個 hunk，以上為主要變更)..."
    return truncated


def generate_commit_message(diff_content):
    """使用 Gemini 生成 Commit 訊息"""

    if not diff_content:
        return None
        
    key = get_api_key()
    if not key:
        return None

    # 智慧截斷：優先保留實際變更行（+/-），必要時才壓縮 context 行
    MAX_CHARS = 15000
    if len(diff_content) > MAX_CHARS:
        diff_content = _smart_truncate_diff(diff_content, MAX_CHARS)

    prompt = f"""
    你是一個資深的軟體工程師。請根據以下的 git diff 內容，生成一個符合 'Conventional Commits' 規範的 commit message。

    規範要求：
    1. 格式為：<type>: <subject>
    2. type 只能是：feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert
    3. subject 用繁體中文，簡潔有力，不超過 30 個字。
    4. 不要輸出 Markdown 格式 (如 ```)，只輸出純文字訊息。

    type 選擇規則（優先順序由高至低）：
    - 若異動的檔案全部為文件類型（如 .md、.txt、.rst），type 必須使用 docs
    - 若異動包含測試檔案（如 test_*.py、*.test.js），type 優先使用 test
    - 若異動只有設定檔（如 .toml、.yml、.json、.gitignore），type 使用 chore
    - 若異動為修復已知問題，使用 fix；若為新增功能，使用 feat
    - 判斷依據是「檔案路徑與類型」，而非 diff 內容所描述的功能名稱

    Git Diff 內容：
    {diff_content}
    """


    try:
        client = genai.Client(api_key=key)
        # 建議使用穩定版模型，或者統一用 gemini-2.0-flash
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite', 
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"❌ AI 生成失敗: {e}")
        return None

def validate_commit_message(message):
    """驗證 commit 訊息格式"""
    allowed_types = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'perf', 'ci', 'build', 'revert']
    
    if not message or not message.strip():
        return False, "commit 訊息不可為空"
    
    if ':' not in message:
        return False, f"格式錯誤：缺少冒號(:)\n正確格式: <type>: <subject>"
    
    parts = message.split(':', 1)
    commit_type = parts[0].strip()
    
    if commit_type not in allowed_types:
        return False, f"不合法的 type: '{commit_type}'\n允許列表: {', '.join(allowed_types)}"
        
    return True, ""