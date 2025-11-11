"""
LEAP阻害要因の徹底分析
==================

Log-Alignment無効化でもLEAP発生しない原因を特定する。
"""

import sys
import os
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, create_default_state

def analyze_leap_blocking_factors():
    """LEAP阻害要因を徹底分析"""
    print("="*80)
    print("🔬 LEAP阻害要因の徹底分析")
    print("="*80)
    
    # Raw版パラメータ（Log-Alignment無効）
    params = SSDCoreParams()
    params.log_align = False
    params.Theta_values = [50.0, 30.0, 20.0, 10.0]
    params.gamma_values = [0.30, 0.25, 0.20, 0.15]
    params.beta_values = [0.0005, 0.005, 0.025, 0.05]
    
    print(f"📊 設定パラメータ:")
    print(f"   Log-Alignment: {params.log_align}")
    print(f"   Theta閾値: {params.Theta_values}")
    print(f"   Gamma値: {params.gamma_values}")
    print(f"   Beta値: {params.beta_values}")
    print(f"   R値: {params.R_values}")
    print()
    
    # エンジン初期化
    engine = SSDCoreEngine(params)
    state = create_default_state(params.num_layers)
    
    print("🧪 圧力注入実験:")
    
    # 段階的圧力注入実験
    for pressure_level in [100.0, 200.0, 300.0, 500.0, 1000.0]:
        print(f"\n📈 圧力レベル: {pressure_level}")
        
        # 初期状態リセット
        state = create_default_state(params.num_layers)
        
        # 10ステップ実行
        for step in range(10):
            pressure_vector = np.zeros(params.num_layers)
            pressure_vector[0] = pressure_level
            
            old_E = state.E.copy()
            
            # ステップ実行
            state = engine.step(state, pressure_vector, dt=0.1)
            
            # エネルギー変化分析
            dE = state.E - old_E
            
            print(f"   Step {step+1}: E={state.E[0]:.3f} (ΔE={dE[0]:.3f}), Theta={params.Theta_values[0]}")
            
            # LEAP判定
            for i, (energy, theta) in enumerate(zip(state.E, params.Theta_values)):
                if energy >= theta:
                    print(f"   🚀 LEAP発生！レイヤー{i+1} E={energy:.3f} >= Theta={theta}")
                    state.E[i] = 0.0  # LEAP後リセット
                    break
            
            if step == 9:
                print(f"   最終状態: {state.E}")
    
    print("\n🔍 エネルギー生成メカニズム分析:")
    
    # エネルギー生成の詳細分析
    state = create_default_state(params.num_layers)
    pressure_vector = np.zeros(params.num_layers) 
    pressure_vector[0] = 300.0  # 高圧力
    
    # 手動でエネルギー生成を計算
    R_array = np.array(params.R_values)
    gamma_array = np.array(params.gamma_values)
    beta_array = np.array(params.beta_values)
    
    # 簡易的な電流計算（j = pressure / R）
    j = pressure_vector / R_array
    print(f"   電流 j: {j}")
    
    # エネルギー生成計算（簡易）
    energy_gen = gamma_array * pressure_vector / R_array
    print(f"   エネルギー生成: {energy_gen}")
    
    # エネルギー減衰
    energy_decay = beta_array * state.E
    print(f"   エネルギー減衰: {energy_decay}")
    
    # 正味エネルギー変化
    net_dE = energy_gen - energy_decay
    print(f"   正味ΔE: {net_dE}")
    
    print(f"\n💡 分析結果:")
    print(f"   第1レイヤーでの1ステップあたりエネルギー増加: {net_dE[0]:.6f}")
    print(f"   LEAP閾値到達まで必要ステップ数: {params.Theta_values[0] / net_dE[0]:.0f}ステップ")
    print(f"   問題: エネルギー生成が非常に小さい可能性")
    
    print(f"\n🔧 考えられる阻害要因:")
    print(f"   1. R値が大きすぎる（1000.0）→ 電流が小さい")
    print(f"   2. Gamma値が小さすぎる（0.30）→ エネルギー生成が小さい") 
    print(f"   3. Beta値によるエネルギー減衰が大きい")
    print(f"   4. dt（時間刻み）が小さすぎる（0.1）")

if __name__ == "__main__":
    analyze_leap_blocking_factors()