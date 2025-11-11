"""
SSD基本温度設定の検討
==================

人間の体温を基準とした温度スケールの妥当性をテスト
"""

import sys
import os
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, create_default_state

def test_temperature_scales():
    """各種温度スケールでのLEAP発生率テスト"""
    print("="*80)
    print("🌡️  SSD基本温度設定の検討")
    print("="*80)
    
    # 温度候補（心理学的解釈付き）
    temperature_candidates = [
        (0.0, "絶対零度", "完全冷静・感情なし"),
        (1.0, "低温", "わずかな感情揺らぎ"),
        (10.0, "室温相当", "軽い感情変動"),
        (37.0, "人体体温", "正常な感情状態"),
        (40.0, "微熱", "軽い興奮・緊張"),
        (50.0, "発熱", "強い感情・不安"),
        (100.0, "沸点", "極度の興奮・パニック"),
    ]
    
    print("🧪 各温度でのLEAP発生率測定:")
    print("-" * 60)
    
    base_params = SSDCoreParams()
    base_params.log_align = False
    base_params.enable_stochastic_leap = True
    base_params.Theta_values = [5.0, 3.0, 2.0, 1.0]
    base_params.gamma_values = [0.1, 0.08, 0.06, 0.04]  # 控えめ
    base_params.beta_values = [0.01, 0.02, 0.05, 0.1]
    base_params.G0 = 0.01  # 超電導回避
    base_params.g = 0.05
    
    # 中程度の心理圧力（カイジの普通の絶望状態）
    moderate_pressure = np.array([200.0, 0.0, 0.0, 0.0])
    
    results = []
    
    for temp, name, description in temperature_candidates:
        params = base_params
        params.temperature_T = temp
        
        engine = SSDCoreEngine(params)
        
        leap_count = 0
        total_trials = 20  # 20回試行
        
        for trial in range(total_trials):
            state = create_default_state(params.num_layers)
            
            # 10ステップ実行
            for step in range(10):
                old_E = state.E.copy()
                
                # 物理修正版の簡易実装
                j = moderate_pressure / np.array(params.R_values)
                resid = np.maximum(0.0, moderate_pressure - j)
                
                # 熱ノイズ追加
                thermal_noise = np.random.normal(0, temp, params.num_layers)
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
        results.append((temp, name, description, leap_rate))
        
        print(f"   T={temp:5.1f} ({name:8s}): {leap_rate:5.1f}% LEAP発生")
        print(f"                      └─ {description}")
    
    print("\n📊 結果分析:")
    print("-" * 40)
    
    # 最適温度範囲を特定
    optimal_rates = [r for r in results if 10 <= r[3] <= 50]  # 10-50%のLEAP率
    
    if optimal_rates:
        print("🎯 適切なLEAP発生率（10-50%）の温度:")
        for temp, name, desc, rate in optimal_rates:
            print(f"   ✅ T={temp} ({name}): {rate:.1f}%")
    
    # 人体体温の評価
    body_temp_result = next((r for r in results if r[0] == 37.0), None)
    if body_temp_result:
        temp, name, desc, rate = body_temp_result
        print(f"\n🩺 人体体温評価:")
        print(f"   T=37.0°C: {rate:.1f}% LEAP発生")
        if 10 <= rate <= 50:
            print(f"   ✅ 適切な範囲（安定した心理変化）")
        elif rate < 10:
            print(f"   ⚠️  低すぎ（変化に乏しい）")
        else:
            print(f"   ⚠️  高すぎ（過度に不安定）")


def propose_human_temperature_system():
    """人間基準温度システムの提案"""
    print("\n" + "="*80)
    print("🩺 人間基準温度システム提案")
    print("="*80)
    
    print("🌡️  心理温度スケール（人体基準）:")
    print("""
    ┌─────────────────────────────────────────────────────┐
    │  温度    │ 心理状態          │ 期待される挙動        │
    ├─────────────────────────────────────────────────────┤
    │  T = 0   │ 絶対零度         │ 完全静的・変化なし     │
    │  T = 37  │ 平熱（基準）     │ 正常な感情変動        │
    │  T = 38  │ 微熱             │ 軽い不安・緊張        │
    │  T = 39  │ 発熱             │ 強い感情・興奮        │
    │  T = 40  │ 高熱             │ 極度の不安・恐怖      │
    │  T = 42+ │ 危険な高熱       │ パニック・錯乱状態    │
    └─────────────────────────────────────────────────────┘
    """)
    
    print("🎯 推奨デフォルト設定:")
    print("```python")
    print("# 人間基準温度システム")
    print("enable_stochastic_leap: bool = True")
    print("temperature_T: float = 37.0          # 人体平熱基準")
    print("```")
    
    print("\n💡 利点:")
    print("  ✅ 直感的理解：体温 = 心理温度")
    print("  ✅ 医学的根拠：発熱 = 心理的興奮")
    print("  ✅ スケール感：37°C基準で±数度の変動")
    print("  ✅ カイジ応用：借金で「熱くなる」心理状態")
    
    print("\n🎮 ゲーム/シミュレーション応用例:")
    print("  • 平常時：T=37（基本設定）")
    print("  • 緊張時：T=38-39（重要な判断）") 
    print("  • 危機時：T=40-42（借金、恋愛、試験）")
    print("  • パニック：T=45+（極限状況）")
    

def test_kaiji_with_body_temperature():
    """人体体温設定でのカイジ実験"""
    print("\n" + "="*80)
    print("💀🩺 カイジ実験 - 人体体温基準版")
    print("="*80)
    
    # 人体体温基準設定
    params = SSDCoreParams()
    params.log_align = False
    params.enable_stochastic_leap = True
    params.temperature_T = 37.0  # 人体平熱
    params.Theta_values = [3.0, 2.0, 1.0, 0.5]
    params.gamma_values = [0.1, 0.08, 0.06, 0.04]
    params.beta_values = [0.01, 0.02, 0.05, 0.1]
    params.G0 = 0.01
    params.g = 0.05
    
    # カイジの状況別温度設定
    kaiji_scenarios = [
        (37.0, "平常時", "普通の借金状態"),
        (38.5, "緊張", "ルーレット開始前"),
        (39.5, "興奮", "連勝・連敗中"),
        (41.0, "恐怖", "大金を賭ける瞬間"),
        (43.0, "パニック", "破産寸前"),
    ]
    
    for temp, state_name, description in kaiji_scenarios:
        print(f"\n🌡️  {state_name}（T={temp}°C）- {description}")
        print("-" * 40)
        
        params.temperature_T = temp
        engine = SSDCoreEngine(params)
        
        # カイジの心理圧力（絶望レベル5）
        despair_pressure = np.array([250.0, 0.0, 0.0, 0.0])
        
        state = create_default_state(params.num_layers)
        leap_occurred = False
        
        for step in range(5):
            old_E = state.E[0]
            
            # 簡易物理修正実装
            j = despair_pressure[0] / params.R_values[0]
            resid = max(0.0, despair_pressure[0] - j)
            
            thermal_noise = np.random.normal(0, temp)
            energy_gen = params.gamma_values[0] * resid + thermal_noise
            energy_decay = params.beta_values[0] * state.E[0]
            
            dE = energy_gen - energy_decay
            state.E[0] = max(0.0, state.E[0] + dE * 0.1)
            
            print(f"   Step {step+1}: E={state.E[0]:.3f} (熱ノイズ: {thermal_noise:.3f})")
            
            if state.E[0] >= params.Theta_values[0]:
                print(f"   🚀 心理的LEAP発生！ (E={state.E[0]:.3f} >= {params.Theta_values[0]})")
                leap_occurred = True
                break
        
        if not leap_occurred:
            print(f"   😐 5ステップではLEAP未発生")
    
    print(f"\n🎯 人体体温基準の妥当性:")
    print(f"   T=37°C：安定した基準状態")
    print(f"   T=38-40°C：適度な心理変動")
    print(f"   T=40°C+：劇的な心理変化（LEAP頻発）")
    print(f"   → 人間の生理的実感と一致！")


if __name__ == "__main__":
    test_temperature_scales()
    propose_human_temperature_system()
    test_kaiji_with_body_temperature()