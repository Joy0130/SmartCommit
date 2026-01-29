#!/usr/bin/env python3
"""測試 readline 預填功能"""

import readline

def test_prefill():
    """測試 readline 預填"""
    prefill_text = "feat: 編輯 commit 訊息時支援 readline"
    
    def prefill_hook():
        readline.insert_text(prefill_text)
        readline.redisplay()
    
    print("測試 readline 預填功能")
    print("應該會看到預填的文字，可以用方向鍵編輯")
    print()
    
    readline.set_pre_input_hook(prefill_hook)
    try:
        result = input("> ")
        print(f"\n你輸入的是: {result}")
    finally:
        readline.set_pre_input_hook(None)

if __name__ == "__main__":
    test_prefill()
