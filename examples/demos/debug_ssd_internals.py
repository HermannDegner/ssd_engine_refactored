"""
SSDエンジン内部処理の詳細デバッグ
===============================

エネルギー生成が0になる原因を特定する。
"""

import sys
import os
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, create_default_state

def debug_ssd_internals():
    """SSDエンジン内部処理をステップ別にデバッグ"""
    print("="*80)
    print("🔍 SSDエンジン内部処理デバッグ")
    print("="*80)
    
    # パラメータ設定
    params = SSDCoreParams()
    params.log_align = False
    params.Theta_values = [10.0, 5.0, 3.0, 1.0]  # より小さな閾値
    params.gamma_values = [1.0, 0.8, 0.6, 0.4]   # より大きなGamma
    params.beta_values = [0.001, 0.01, 0.05, 0.1]  # 小さなBeta
    
    print(f"📊 デバッグ用パラメータ:")
    print(f"   Theta: {params.Theta_values}")
    print(f"   Gamma: {params.gamma_values}")
    print(f"   Beta: {params.beta_values}")
    print(f"   R: {params.R_values}")
    print(f"   G0: {params.G0}, g: {params.g}")
    print()
    
    # エンジン初期化
    engine = SSDCoreEngine(params)
    state = create_default_state(params.num_layers)
    
    print(f"📋 初期状態:")
    print(f"   E: {state.E}")
    print(f"   κ: {state.kappa}")
    print()
    
    # 高圧力注入
    pressure = np.array([500.0, 0.0, 0.0, 0.0])
    print(f"🔥 注入圧力: {pressure}")
    
    # ステップ実行前にエンジン内部の各段階を手動追跡
    print(f"\n🔬 内部処理追跡:")
    
    # 1. Log-Alignment適用
    pressure_hat = engine.apply_log_alignment(state, pressure)
    print(f"   1. Log-Alignment後: {pressure_hat}")
    print(f"      (log_align={params.log_align}なので変化なし)")
    
    # 2. Ohm's law計算
    conductance = params.G0 + params.g * state.kappa
    print(f"   2. 導電率: {conductance}")
    
    j = conductance * pressure_hat
    print(f"   3. 電流 j: {j}")
    
    # 3. エネルギー残差計算
    if params.use_log_residual:
        resid = np.maximum(0.0, np.abs(pressure_hat) - np.abs(j))
    else:
        resid = np.maximum(0.0, np.abs(pressure) - np.abs(j))
    print(f"   4. 残差 resid: {resid}")
    print(f"      |p̂| = {np.abs(pressure_hat)}")
    print(f"      |j| = {np.abs(j)}")
    print(f"      use_log_residual = {params.use_log_residual}")
    
    # 4. エネルギー生成計算
    R_array = np.array(params.R_values)
    gamma_array = np.array(params.gamma_values)
    energy_generation = gamma_array * resid / R_array
    print(f"   5. エネルギー生成: {energy_generation}")
    print(f"      gamma * resid / R = {gamma_array} * {resid} / {R_array}")
    
    # 5. エネルギー減衰
    beta_array = np.array(params.beta_values)
    energy_decay = beta_array * state.E
    print(f"   6. エネルギー減衰: {energy_decay}")
    
    # 6. 正味エネルギー変化
    dE = energy_generation - energy_decay
    print(f"   7. 正味ΔE: {dE}")
    
    # 7. 時間積分
    dt = 0.1
    new_E = np.maximum(0.0, state.E + dE * dt)
    print(f"   8. 更新後E (dt={dt}): {new_E}")
    
    print(f"\n🚀 実際のステップ実行:")
    
    # 実際のステップ実行と比較
    old_E = state.E.copy()
    new_state = engine.step(state, pressure, dt=dt)
    actual_dE = new_state.E - old_E
    
    print(f"   実際のΔE: {actual_dE}")
    print(f"   実際のE: {new_state.E}")
    print(f"   期待値との差: {new_state.E - new_E}")
    
    # もし大きな乖離があれば原因調査
    if np.max(np.abs(actual_dE - dE * dt)) > 1e-6:
        print(f"\n⚠️  期待値と実際値に乖離あり！追加調査が必要")
        
        # apply_log_alignmentの戻り値を確認
        print(f"   apply_log_alignment戻り値: {engine.apply_log_alignment(state, pressure)}")
        print(f"   パラメータlog_align: {engine.params.log_align}")
    else:
        print(f"\n✅ 期待値と実際値が一致")
    
    # 連続実行テスト
    print(f"\n🔄 10ステップ連続実行:")
    current_state = create_default_state(params.num_layers)
    
    for step in range(10):
        old_E = current_state.E.copy()
        current_state = engine.step(current_state, pressure, dt=dt)
        dE_step = current_state.E - old_E
        
        print(f"   Step {step+1}: E={current_state.E[0]:.6f}, ΔE={dE_step[0]:.6f}")
        
        # LEAP判定
        for i, (energy, theta) in enumerate(zip(current_state.E, params.Theta_values)):
            if energy >= theta:
                print(f"   🚀 LEAP発生！レイヤー{i+1} E={energy:.6f} >= Theta={theta}")
                current_state.E[i] = 0.0
                break

if __name__ == "__main__":
    debug_ssd_internals()