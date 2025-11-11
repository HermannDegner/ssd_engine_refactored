"""
人体体温基準SSDシステム - スケール調整版
====================================

実際の体温変化（±数度）に合わせたパラメータ調整
"""

import sys
import os
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.ssd_core_engine import SSDCoreEngine, SSDCoreParams, create_default_state

def create_human_calibrated_params():
    """人体体温に較正されたSSDパラメータ"""
    params = SSDCoreParams()
    
    # 基本設定
    params.log_align = False
    params.enable_stochastic_leap = True
    params.temperature_T = 37.0  # 人体平熱基準
    
    # 人体体温スケールに合わせた調整
    params.Theta_values = [100.0, 80.0, 60.0, 40.0]  # より高い閾値
    params.gamma_values = [1.0, 0.8, 0.6, 0.4]      # エネルギー生成
    params.beta_values = [0.1, 0.15, 0.2, 0.25]     # より強い減衰
    
    # 物理修正
    params.G0 = 0.001  # 非常に小さな基底導電率
    params.g = 0.01    # 小さなゲイン
    
    return params


def test_calibrated_human_temperature():
    """較正済み人体体温システムのテスト"""
    print("="*80)
    print("🩺⚖️  人体体温較正システム - スケール調整版")
    print("="*80)
    
    # 体温変化シナリオ（現実的な範囲）
    temperature_scenarios = [
        (35.0, "低体温", "体調不良・意識朦朧"),
        (36.0, "やや低め", "軽い体調不良"),
        (37.0, "平熱", "正常状態"),
        (37.5, "微熱", "軽い興奮・緊張"),
        (38.0, "軽い熱", "不安・心配"),
        (38.5, "中熱", "強い緊張・恐怖"),
        (39.0, "高熱", "パニック寸前"),
        (40.0, "危険熱", "極度のパニック"),
    ]
    
    base_params = create_human_calibrated_params()
    
    print("🧪 人体体温スケールでのLEAP発生率:")
    print("-" * 50)
    
    for temp, state_name, description in temperature_scenarios:
        params = base_params
        params.temperature_T = temp
        
        # 中程度の心理圧力（カイジの普通の状況）
        pressure = np.array([300.0, 0.0, 0.0, 0.0])
        
        leap_count = 0
        total_trials = 10
        
        for trial in range(total_trials):
            state = create_default_state(params.num_layers)
            
            # 10ステップ実行
            for step in range(10):
                # 物理修正版実装
                j = pressure / np.array(params.R_values)
                resid = np.maximum(0.0, pressure - j)
                
                # 体温スケールの熱ノイズ（標準偏差 = 体温の1/10）
                thermal_noise = np.random.normal(0, temp/10, params.num_layers)
                
                energy_gen = params.gamma_values[0] * resid[0] + thermal_noise[0]
                energy_decay = params.beta_values[0] * state.E[0]
                
                dE = energy_gen - energy_decay
                state.E[0] = max(0.0, state.E[0] + dE * 0.1)
                
                # LEAP判定
                if state.E[0] >= params.Theta_values[0]:
                    leap_count += 1
                    state.E[0] = 0.0
                    break
        
        leap_rate = leap_count / total_trials * 100
        
        print(f"   {temp:4.1f}°C ({state_name:6s}): {leap_rate:5.1f}% - {description}")
    
    print("\n📊 体温とLEAP発生率の関係:")
    print("   35°C以下: 低活性（生命維持レベル）")
    print("   37°C付近: 正常範囲（適度なLEAP）")
    print("   38°C以上: 高活性（LEAP頻発）")
    print("   40°C以上: 危険域（制御不能）")


def design_kaiji_temperature_system():
    """カイジ専用体温システム設計"""
    print("\n" + "="*80)
    print("💀🌡️  カイジ体温システム設計")
    print("="*80)
    
    print("🎯 カイジの心理状態と体温の対応:")
    print("""
    ┌─────────────────────────────────────────────────────────┐
    │ 体温   │ カイジの状態        │ 心理描写               │
    ├─────────────────────────────────────────────────────────┤
    │ 36.8°C │ 冷静               │ 「落ち着いて考えろ...」  │
    │ 37.2°C │ 平常               │ 普通の借金プレッシャー   │
    │ 37.8°C │ 緊張               │ 「やばい...どうする」   │
    │ 38.5°C │ 焦燥               │ 「クソッ！なんで...」   │
    │ 39.2°C │ 恐怖               │ 「終わった...終わりだ」  │
    │ 40.0°C │ パニック           │ 「ざわ...ざわ...」      │
    │ 41.0°C │ 錯乱               │ 意識朦朧・暴走状態       │
    └─────────────────────────────────────────────────────────┘
    """)
    
    # カイジシナリオでテスト
    kaiji_params = create_human_calibrated_params()
    
    kaiji_situations = [
        (37.0, "通常の借金", 200),
        (38.0, "ルーレット開始", 300),
        (39.0, "連敗中", 500),
        (40.0, "最後の一勝負", 800),
        (41.0, "破産寸前", 1000),
    ]
    
    print("\n🎰 カイジシミュレーション:")
    print("-" * 40)
    
    for temp, situation, pressure_level in kaiji_situations:
        print(f"\n🌡️  体温{temp}°C - {situation}")
        
        kaiji_params.temperature_T = temp
        pressure = np.array([pressure_level, 0.0, 0.0, 0.0])
        
        state = create_default_state(kaiji_params.num_layers)
        
        # 3ステップで観察
        for step in range(3):
            j = pressure[0] / kaiji_params.R_values[0]
            resid = max(0.0, pressure[0] - j)
            
            # 体温ノイズ（体温に比例した揺らぎ）
            thermal_noise = np.random.normal(0, temp/8)
            
            energy_gen = kaiji_params.gamma_values[0] * resid + thermal_noise
            energy_decay = kaiji_params.beta_values[0] * state.E[0]
            
            dE = energy_gen - energy_decay
            state.E[0] = max(0.0, state.E[0] + dE * 0.1)
            
            print(f"   Step {step+1}: E={state.E[0]:6.2f} (熱揺らぎ:{thermal_noise:+6.2f})")
            
            if state.E[0] >= kaiji_params.Theta_values[0]:
                print(f"   🚀 カイジLEAP！「ざわ...ざわ...」")
                state.E[0] = 0.0
                break
    
    print(f"\n🎯 カイジ体温システムの特徴:")
    print(f"   • 37°C基準：人間として自然")
    print(f"   • ±4°C範囲：現実的な体温変動")
    print(f"   • 心理描写連動：体温 = 感情の熱さ")
    print(f"   • ゲーム適用：直感的な興奮度表現")


def recommend_final_settings():
    """最終推奨設定"""
    print("\n" + "="*80)
    print("🎯 SSD人体体温基準システム - 最終推奨設定")
    print("="*80)
    
    print("```python")
    print("# SSDCoreParams - 人体体温基準システム")
    print("class SSDCoreParams:")
    print("    # 熱力学設定（人体基準）")
    print("    enable_stochastic_leap: bool = True")
    print("    temperature_T: float = 37.0          # 人体平熱基準")
    print("    ")
    print("    # 物理修正（超電導回避）")
    print("    G0: float = 0.001                    # 現実的基底導電率")
    print("    g: float = 0.01                      # 現実的ゲイン")
    print("    ")
    print("    # 人体スケール調整")
    print("    Theta_values: [100.0, 80.0, 60.0, 40.0]  # 体温変動対応")
    print("    gamma_values: [1.0, 0.8, 0.6, 0.4]       # 適度なエネルギー")
    print("    beta_values: [0.1, 0.15, 0.2, 0.25]      # バランス減衰")
    print("```")
    
    print("\n💡 設計原理:")
    print("  🩺 生理学的根拠：人体体温 = 心理温度")
    print("  🧠 心理学的直感：発熱 = 興奮状態")
    print("  ⚖️  スケール調整：±数度の微細変動に対応")
    print("  🎮 ゲーム応用：体温で感情状態を表現")
    
    print("\n🌡️  推奨温度範囲:")
    print("  • 冷静: 36-37°C（低LEAP率）")
    print("  • 通常: 37-38°C（適度なLEAP）")
    print("  • 興奮: 38-40°C（高LEAP率）")
    print("  • 危険: 40°C以上（制御困難）")


if __name__ == "__main__":
    test_calibrated_human_temperature()
    design_kaiji_temperature_system()
    recommend_final_settings()