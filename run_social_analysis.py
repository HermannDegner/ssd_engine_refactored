"""
社会分析クイックスタート - すべての社会分析デモを簡単に実行
================================================================

このスクリプトを実行すると、3つの社会分析デモから選択して実行できます。
"""

import sys
import os

def print_menu():
    """メニュー表示"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║          SSDエンジン 社会分析デモ - クイックスタート            ║
║      Structural Subjectivity Dynamics - Social Analysis        ║
╚════════════════════════════════════════════════════════════════╝

以下のデモから選択してください:

【1】基本的な社会分析
    ├─ 意見分極化（Opinion Polarization）
    ├─ リーダーシップの創発
    └─ 規範の形成
    
【2】社会危機分析
    ├─ 集団パニック（Mass Panic）
    ├─ 規範の崩壊
    └─ カリスマ的リーダーシップ
    
【3】現代社会問題分析
    ├─ SNS炎上現象
    └─ 職場パワーハラスメント

【4】すべて実行（推奨: 時間がかかります）

【0】終了
""")

def run_demo(choice):
    """デモ実行"""
    if choice == '1':
        print("\n" + "="*60)
        print("基本的な社会分析デモを起動中...")
        print("="*60)
        os.system(f'{sys.executable} examples/social_analysis_demo.py')
        
    elif choice == '2':
        print("\n" + "="*60)
        print("社会危機分析デモを起動中...")
        print("="*60)
        os.system(f'{sys.executable} examples/social_crisis_analysis.py')
        
    elif choice == '3':
        print("\n" + "="*60)
        print("現代社会問題分析デモを起動中...")
        print("="*60)
        os.system(f'{sys.executable} examples/modern_social_issues.py')
        
    elif choice == '4':
        print("\n" + "="*60)
        print("すべてのデモを順次実行します...")
        print("="*60)
        
        print("\n【1/3】基本的な社会分析")
        os.system(f'{sys.executable} examples/social_analysis_demo.py')
        
        input("\n次のデモに進むにはEnterキーを押してください...")
        
        print("\n【2/3】社会危機分析")
        os.system(f'{sys.executable} examples/social_crisis_analysis.py')
        
        input("\n次のデモに進むにはEnterキーを押してください...")
        
        print("\n【3/3】現代社会問題分析")
        os.system(f'{sys.executable} examples/modern_social_issues.py')
        
        print("\n✅ すべてのデモが完了しました！")
        
    elif choice == '0':
        print("\n終了します。")
        sys.exit(0)
        
    else:
        print("\n❌ 無効な選択です。0-4を選択してください。")

def main():
    """メイン実行"""
    while True:
        print_menu()
        choice = input("選択 (0-4): ").strip()
        run_demo(choice)
        
        if choice in ['1', '2', '3', '4']:
            print("\n" + "="*60)
            cont = input("\n他のデモも実行しますか？ (y/n): ").strip().lower()
            if cont != 'y':
                print("\n終了します。お疲れ様でした！")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n中断されました。")
        sys.exit(0)
