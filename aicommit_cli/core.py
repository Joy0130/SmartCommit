"""Core functionality for aicommit-cli."""

import os
import subprocess
import time
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

def get_git_diff():
    """取得Git暫存區的變更(Diff)。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        print("❌ 錯誤：找不到 git 指令，請確認已安裝 git。")
        return None


def _parse_diff_into_hunks(diff_content: str) -> list:
    """將 diff 內容解析成結構化的 hunk 列表。

    修正點：每遇到 'diff --git' 新檔案時，正確重置 current_file_headers，
    確保每個 hunk 只帶自己所屬檔案的標頭行，避免標頭無限累積浪費截斷預算。
    """
    lines = diff_content.splitlines(keepends=True)
    hunks = []
    current_file_headers = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 遇到新檔案的 diff 起始行，重置標頭收集器
        if line.startswith('diff --git'):
            current_file_headers = [line]
            i += 1
            continue

        # 收集同一檔案的其他標頭行（index / --- / +++ / new file / deleted file / rename）
        if line.startswith(('index ', '--- ', '+++ ', 'new file', 'deleted file', 'rename ')):
            current_file_headers.append(line)
            i += 1
            continue

        # 遇到 hunk 標頭（@@ ... @@），收集整個 hunk 的內容
        if line.startswith('@@'):
            hunk_header = line
            hunk_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith(('@@', 'diff --git')):
                hunk_lines.append(lines[i])
                i += 1

            changed = [l for l in hunk_lines if l.startswith(('+', '-'))]
            context = [l for l in hunk_lines if not l.startswith(('+', '-'))]
            hunks.append({
                'file_headers': list(current_file_headers),  # 只含此檔案的標頭
                'hunk_header': hunk_header,
                'changed': changed,
                'context': context,
            })
            continue

        i += 1

    return hunks


def _smart_truncate_diff(diff_content: str, max_chars: int) -> str:
    """智慧截斷 diff：將預算按比例分配給所有 hunk，確保每個檔案的變更都能被 AI 看到。

    修正點：每個 hunk 的 changed 行寫入受 allocated 上限控制（per-hunk 限額），
    防止前面大型 hunk 吃掉全部預算，讓後面小型 hunk 完全沒有空間。
    """
    hunks = _parse_diff_into_hunks(diff_content)
    if not hunks:
        return diff_content[:max_chars]

    # 計算每個 hunk 只保留 changed 行的最小成本
    def hunk_min_cost(h):
        return len(h['hunk_header']) + sum(len(l) for l in h['changed'])

    total_min_cost = sum(hunk_min_cost(h) for h in hunks)

    result_parts = []
    total_written = 0
    skipped_hunks = 0
    last_file_headers = None  # 用於判斷是否需要寫入檔案標頭

    for h in hunks:
        min_cost = hunk_min_cost(h)
        if min_cost == 0:
            continue

        # 按比例計算此 hunk 的字元預算上限
        if total_min_cost > 0:
            allocated = int(max_chars * min_cost / total_min_cost)
        else:
            allocated = max_chars // max(len(hunks), 1)

        # 保證每個 hunk 至少有最小可用空間（避免比例過小導致完全跳過）
        allocated = max(allocated, min(min_cost, 500))

        # 全局預算不足時跳過此 hunk
        if total_written + min_cost > max_chars:
            skipped_hunks += 1
            continue

        hunk_written = 0  # 此 hunk 已寫入的字元數

        # 寫入 diff 檔案標頭（只在換檔案時寫入，避免重複）
        file_header_str = ''.join(h['file_headers'])
        if h['file_headers'] != last_file_headers:
            if total_written + len(file_header_str) <= max_chars:
                result_parts.append(file_header_str)
                total_written += len(file_header_str)
                hunk_written += len(file_header_str)
            last_file_headers = h['file_headers']

        # 寫入 hunk 標頭
        if total_written + len(h['hunk_header']) <= max_chars:
            result_parts.append(h['hunk_header'])
            total_written += len(h['hunk_header'])
            hunk_written += len(h['hunk_header'])

        # 寫入 changed 行，受 per-hunk allocated 上限控制
        for cl in h['changed']:
            if total_written + len(cl) <= max_chars and hunk_written + len(cl) <= allocated:
                result_parts.append(cl)
                total_written += len(cl)
                hunk_written += len(cl)

        # 有剩餘空間才加入 context 行（非必要）
        for ctx in h['context']:
            if total_written + len(ctx) <= max_chars and hunk_written + len(ctx) <= allocated:
                result_parts.append(ctx)
                total_written += len(ctx)
                hunk_written += len(ctx)

    truncated = ''.join(result_parts)
    if skipped_hunks > 0:
        truncated += f"\n\n...(因 diff 過大，已略過 {skipped_hunks} 個 hunk，以上為主要變更)..."
    return truncated


def _classify_error(error) -> str:
    """將錯誤分類，讓呼叫端決定處理策略。

    回傳值：
    - 'content_too_large'：輸入超出 token 上限，需縮減內容後重試
    - 'retryable'        ：伺服器暫時性錯誤（429/5xx），稍後重試即可
    - 'fatal'            ：不可恢復的錯誤，直接放棄
    """
    code = getattr(error, 'code', None) or getattr(error, 'status_code', None)
    msg = str(error).lower()

    # token / 內容過大（400 INVALID_ARGUMENT + 相關關鍵字）
    content_too_large_keywords = (
        'too large', 'token', 'context', 'exceed',
        'request payload', 'content size', 'invalid argument',
    )
    if code == 400 or any(kw in msg for kw in content_too_large_keywords):
        return 'content_too_large'

    # 伺服器暫時性錯誤
    if code in (429, 500, 502, 503, 504):
        return 'retryable'
    retryable_keywords = (
        '503', '502', '500', '429', 'unavailable',
        'overloaded', 'high demand', 'rate limit', 'deadline', 'timeout',
    )
    if any(kw in msg for kw in retryable_keywords):
        return 'retryable'

    return 'fatal'


def _build_prompt(diff_content: str) -> str:
    """組裝送給 AI 的 prompt。"""
    return f"""
    你是一個資深的軟體工程師。請根據以下的 git diff 內容，生成一個符合 'Conventional Commits' 規範的 commit message。

    規範要求：
    1. 格式為：<type>: <subject>
    2. type 只能是：feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert
    3. subject 用繁體中文，簡潔有力，不超過 40 個字。
    4. 不要輸出 Markdown 格式 (如 ```)，只輸出純文字訊息。
    5. 請綜合考量 diff 中**所有**被修改的檔案與變更內容，產生能概括整體修改意圖的 commit message，不要只描述某一個檔案的變更。

    type 選擇規則（優先順序由高至低）：
    - 若異動的檔案全部為文件類型（如 .md、.txt、.rst），type 必須使用 docs
    - 若異動包含測試檔案（如 test_*.py、*.test.js），type 優先使用 test
    - 若異動只有設定檔（如 .toml、.yml、.json、.gitignore），type 使用 chore
    - 若異動為修復已知問題，使用 fix；若為新增功能，使用 feat
    - 判斷依據是「檔案路徑與類型」，而非 diff 內容所描述的功能名稱

    Git Diff 內容：
    {diff_content}
    """


def generate_commit_message(diff_content):
    """使用 Gemini 生成 Commit 訊息。

    策略：
    - 預設將 diff 截斷至 MAX_CHARS（12000）送出
    - 若 AI 回傳 token 超限錯誤（400），自動縮減至 FALLBACK_CHARS 再重試
    - 若為伺服器暫時性錯誤（429/5xx），指數退避重試最多 3 次
    """
    if not diff_content:
        return None

    key = get_api_key()
    if not key:
        return None

    # 不同層級的截斷上限；遇到 token 超限時依序降級
    CHAR_LIMITS = [12000, 8000, 6000]

    client = genai.Client(api_key=key)
    MAX_SERVER_RETRIES = 3   # 伺服器錯誤最大重試次數
    BASE_DELAY = 2           # 指數退避基礎延遲（秒）

    for limit_idx, max_chars in enumerate(CHAR_LIMITS):
        # 根據當前允許的字元上限截斷 diff
        if len(diff_content) > max_chars:
            current_diff = _smart_truncate_diff(diff_content, max_chars)
        else:
            current_diff = diff_content

        prompt = _build_prompt(current_diff)

        last_error = None
        for attempt in range(MAX_SERVER_RETRIES):
            try:
                response = client.models.generate_content(
                    model='gemini-3.1-flash-lite', #gemini-2.5-flash-lite
                    contents=prompt
                )
                return response.text.strip()

            except Exception as e:
                last_error = e
                error_type = _classify_error(e)

                if error_type == 'content_too_large':
                    # 內容過大，跳出重試迴圈，降級到更小的 max_chars
                    next_limit = CHAR_LIMITS[limit_idx + 1] if limit_idx + 1 < len(CHAR_LIMITS) else None
                    if next_limit:
                        print(f"⚠️  diff 內容過大（超出 AI token 限制），自動縮減至 {next_limit} 字元後重試...")
                    break  # 退出 server-retry 迴圈，進入下一個 limit

                elif error_type == 'retryable' and attempt < MAX_SERVER_RETRIES - 1:
                    delay = BASE_DELAY * (2 ** attempt)
                    print(f"⏳ AI 服務忙碌中，{delay} 秒後重試 (第 {attempt + 1}/{MAX_SERVER_RETRIES - 1} 次)...")
                    time.sleep(delay)
                    continue

                else:
                    # fatal 或已用盡重試次數
                    print(f"❌ AI 生成失敗: {last_error}")
                    return None
        else:
            # server-retry 迴圈正常結束（沒有 break）代表重試全部失敗
            print(f"❌ AI 生成失敗: {last_error}")
            return None

    # 三個層級全部失敗
    print(f"❌ AI 生成失敗：即使縮減至最小 diff，仍超出 token 限制。請減少暫存的變更後再試。")
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