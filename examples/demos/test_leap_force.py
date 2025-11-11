"""
カイジ的借金地獄ルーレット - 極限LEAP実験版
==========================================

残差計算を回避して強制的にLEAP発生を確認する実験版。
"""

import sys
import os
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, create_default_state

def create_leap_force_params():
    """LEAP強制発生用パラメータ"""
    params = SSDCoreParams()
    
    # Log-Alignment無効化
    params.log_align = False
    
    # 電流を圧力より小さくするために抵抗を大幅増加
    params.R_values = [10000.0, 5000.0, 1000.0, 100.0]  # 10倍増
    
    # 導電率を下げる
    params.G0 = 0.1  # 0.5 → 0.1
    params.g = 0.1   # 0.7 → 0.1
    
    # エネルギー生成を大幅増加
    params.gamma_values = [10.0, 8.0, 6.0, 4.0]  # 20倍増
    
    # エネルギー減衰を最小化
    params.beta_values = [0.0001, 0.001, 0.01, 0.05]  # 1/10
    
    # LEAP閾値を現実的に設定
    params.Theta_values = [5.0, 3.0, 2.0, 1.0]
    
    # 確率的LEAP有効化
    params.enable_stochastic_leap = True
    params.temperature_T = 3.0
    
    return params


def test_leap_force():
    """LEAP強制発生テスト"""
    print("="*80)
    print("🚀 極限LEAP実験 - 強制発生版")
    print("="*80)
    
    params = create_leap_force_params()
    engine = SSDCoreEngine(params)
    
    print(f"📊 強制LEAP用パラメータ:")
    print(f"   R値（大幅増加）: {params.R_values}")
    print(f"   G0={params.G0}, g={params.g} （導電率低減）")
    print(f"   Gamma（大幅増加）: {params.gamma_values}")
    print(f"   Beta（最小化）: {params.beta_values}")
    print(f"   Theta（現実的）: {params.Theta_values}")
    print()
    
    # 段階的実験
    for pressure_level in [100.0, 500.0, 1000.0, 2000.0]:
        print(f"🔥 圧力レベル: {pressure_level}")
        
        state = create_default_state(params.num_layers)
        pressure = np.array([pressure_level, 0.0, 0.0, 0.0])
        
        # 内部計算確認
        pressure_hat = engine.apply_log_alignment(state, pressure)
        conductance = params.G0 + params.g * state.kappa
        j = conductance * pressure_hat
        
        resid = np.maximum(0.0, np.abs(pressure_hat) - np.abs(j))
        
        print(f"   導電率: {conductance[0]:.3f}")
        print(f"   電流: {j[0]:.1f}")
        print(f"   残差: {resid[0]:.1f}")
        
        if resid[0] > 0:
            print(f"   ✅ 残差あり！エネルギー生成可能")
            
            # 10ステップ実行
            leap_occurred = False
            for step in range(10):
                old_E = state.E.copy()
                state = engine.step(state, pressure, dt=0.1)
                dE = state.E - old_E
                
                print(f"   Step {step+1}: E={state.E[0]:.3f} (ΔE={dE[0]:.3f})")
                
                # LEAP判定
                for i, (energy, theta) in enumerate(zip(state.E, params.Theta_values)):
                    if energy >= theta:
                        print(f"   🚀 LEAP発生！！！ レイヤー{i+1} E={energy:.3f} >= Theta={theta}")
                        leap_occurred = True
                        state.E[i] = 0.0
                        break
                
                if leap_occurred:
                    break
            
            if not leap_occurred:
                print(f"   😱 10ステップでもLEAP未発生")
        else:
            print(f"   ❌ 残差なし。電流が圧力を完全処理")
        
        print()
    
    print("🎯 結論:")
    print("   残差 = max(0, |圧力| - |電流|)")
    print("   電流 = 導電率 × 圧力")
    print("   導電率 = G0 + g×κ")
    print("   LEAP発生には: 圧力 > 導電率×圧力 = (G0+g×κ)×圧力")
    print("   これは数学的に不可能（導電率 > 1の場合）")
    print()
    print("💡 SSD理論の本質:")
    print("   システムの処理能力（電流）が圧力に比例するため、")
    print("   通常の線形システムではLEAPは発生しない。")
    print("   LEAP発生には非線形性や飽和効果が必要。")


if __name__ == "__main__":
    test_leap_force()