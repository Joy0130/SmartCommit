#!/usr/bin/env python3
"""測試 macOS readline/libedit 預填功能"""

import sys

def test_import():
    """測試 readline 導入"""
    try:
        import readline
        print("✅ readline 模組已導入")
        
        # 檢查後端
        backend = getattr(readline, 'backend', 'unknown')
        print(f"   後端: {backend}")
        
        # 檢查可用的 hook
        has_pre_input = hasattr(readline, 'set_pre_input_hook')
        has_startup = hasattr(readline, 'set_startup_hook')
        print(f"   set_pre_input_hook: {'✅' if has_pre_input else '❌'}")
        print(f"   set_startup_hook: {'✅' if has_startup else '❌'}")
        
        return readline
    except ImportError as e:
        print(f"❌ 無法導入 readline: {e}")
        return None

def test_prefill_pre_input(readline):
    """測試 pre_input_hook 預填"""
    if not hasattr(readline, 'set_pre_input_hook'):
        print("\n❌ 跳過 pre_input_hook 測試 - 不支援")
        return False
    
    print("\n📝 測試 1: set_pre_input_hook")
    print("   應該會看到預填的文字：'feat: test pre_input_hook'")
    
    test_text = "feat: test pre_input_hook"
    
    def prefill():
        readline.insert_text(test_text)
        readline.redisplay()
    
    readline.set_pre_input_hook(prefill)
    try:
        result = input("   > ")
        success = test_text in result or result == test_text
        print(f"   結果: {'✅ 成功' if success else '❌ 失敗'} (輸入: {result})")
        return success
    except Exception as e:
        print(f"   ❌ 錯誤: {e}")
        return False
    finally:
        readline.set_pre_input_hook(None)

def test_prefill_startup(readline):
    """測試 startup_hook 預填"""
    if not hasattr(readline, 'set_startup_hook'):
        print("\n❌ 跳過 startup_hook 測試 - 不支援")
        return False
    
    print("\n📝 測試 2: set_startup_hook")
    print("   應該會看到預填的文字：'feat: test startup_hook'")
    
    test_text = "feat: test startup_hook"
    
    def prefill():
        readline.insert_text(test_text)
        readline.redisplay()
    
    readline.set_startup_hook(prefill)
    try:
        result = input("   > ")
        success = test_text in result or result == test_text
        print(f"   結果: {'✅ 成功' if success else '❌ 失敗'} (輸入: {result})")
        return success
    except Exception as e:
        print(f"   ❌ 錯誤: {e}")
        return False
    finally:
        readline.set_startup_hook(None)

def main():
    print("=" * 60)
    print("🧪 macOS readline/libedit 預填功能測試")
    print("=" * 60)
    
    # 測試導入
    readline = test_import()
    if not readline:
        return
    
    print("\n" + "─" * 60)
    
    # 測試預填功能
    pre_input_works = test_prefill_pre_input(readline)
    startup_works = test_prefill_startup(readline)
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    
    if pre_input_works or startup_works:
        print("✅ 至少一種預填方法可用")
        if pre_input_works:
            print("   推薦使用: set_pre_input_hook")
        elif startup_works:
            print("   推薦使用: set_startup_hook")
    else:
        print("❌ 預填功能在您的環境中不可用")
        print("\n💡 替代方案:")
        print("   1. 安裝 GNU readline: brew install readline")
        print("   2. 使用 gnureadline 套件: pip install gnureadline")
        print("   3. 手動複製貼上 AI 建議的訊息")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  測試已中斷")
        sys.exit(1)
