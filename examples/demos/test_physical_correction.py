"""
SSD物理的修正版 - 正しいオームの法則実装
======================================

現在の「超電導」問題を修正し、物理的に正しい実装にする。
"""

import sys
import os
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, create_default_state

class PhysicalSSDEngine(SSDCoreEngine):
    """物理的に正しいSSDエンジン"""
    
    def step(self, state, pressure, dt=0.1, interlayer_transfer=None):
        """物理的に正しいステップ実行"""
        
        # 配列化
        R_array = np.array(self.params.R_values)
        gamma_array = np.array(self.params.gamma_values)
        beta_array = np.array(self.params.beta_values)
        eta_array = np.array(self.params.eta_values)
        lambda_array = np.array(self.params.lambda_values)
        kappa_min_array = np.array(self.params.kappa_min_values)
        
        # 新状態作成
        new_state = create_default_state(self.num_layers)
        new_state.t = state.t + dt
        new_state.step_count = state.step_count + 1
        new_state.logalign_state = state.logalign_state.copy()
        
        # Log-Alignment適用
        pressure_hat = self.apply_log_alignment(state, pressure)
        
        # 【修正】正しいオームの法則: j = p̂ / R
        j = pressure_hat / R_array
        
        print(f"🔧 修正版計算:")
        print(f"   圧力 p̂: {pressure_hat}")
        print(f"   抵抗 R: {R_array}")
        print(f"   電流 j = p̂/R: {j}")
        
        # エネルギー残差計算
        if self.params.use_log_residual:
            resid = np.maximum(0.0, np.abs(pressure_hat) - np.abs(j))
        else:
            resid = np.maximum(0.0, np.abs(pressure) - np.abs(j))
        
        print(f"   残差: {resid}")
        
        # エネルギー生成
        energy_generation = gamma_array * resid
        print(f"   エネルギー生成: {energy_generation}")
        
        # エネルギー減衰
        energy_decay = beta_array * state.E
        
        # エネルギー更新
        dE = energy_generation - energy_decay
        
        if interlayer_transfer is not None:
            dE += interlayer_transfer
        
        new_state.E = np.maximum(0.0, state.E + dE * dt)
        
        # κ更新（導電率の概念を除去し、純粋に使用頻度ベース）
        usage_factor = np.abs(j) / (np.abs(j) + 1.0)
        dkappa = eta_array * usage_factor - lambda_array * state.kappa
        new_state.kappa = np.maximum(kappa_min_array, state.kappa + dkappa * dt)
        
        return new_state


def test_physical_correction():
    """物理修正版のテスト"""
    print("="*80)
    print("🔧 SSD物理修正版テスト")
    print("="*80)
    
    # パラメータ設定
    params = SSDCoreParams()
    params.log_align = False
    params.Theta_values = [5.0, 3.0, 2.0, 1.0]
    params.gamma_values = [1.0, 0.8, 0.6, 0.4]
    params.beta_values = [0.001, 0.01, 0.05, 0.1]
    
    print(f"📊 テストパラメータ:")
    print(f"   R値: {params.R_values}")
    print(f"   Gamma: {params.gamma_values}")
    print(f"   Beta: {params.beta_values}")
    print(f"   Theta: {params.Theta_values}")
    print()
    
    # 元の「超電導」エンジンと修正版を比較
    original_engine = SSDCoreEngine(params)
    physical_engine = PhysicalSSDEngine(params)
    
    pressure = np.array([1000.0, 0.0, 0.0, 0.0])
    print(f"🔥 テスト圧力: {pressure[0]}")
    print()
    
    print("📊 【元の超電導版】:")
    state_orig = create_default_state(params.num_layers)
    
    # 元版の内部計算を表示
    pressure_hat = original_engine.apply_log_alignment(state_orig, pressure)
    conductance = params.G0 + params.g * state_orig.kappa
    j_orig = conductance * pressure_hat
    resid_orig = np.maximum(0.0, np.abs(pressure_hat) - np.abs(j_orig))
    
    print(f"   導電率: {conductance[0]:.3f}")
    print(f"   電流 j = 導電率×p̂: {j_orig[0]:.1f}")
    print(f"   残差: {resid_orig[0]:.1f}")
    print(f"   → 超電導状態（電流が圧力を上回る）")
    print()
    
    print("📊 【物理修正版】:")
    state_phys = create_default_state(params.num_layers)
    
    # 修正版テスト（内部で計算表示される）
    new_state = physical_engine.step(state_phys, pressure, dt=0.1)
    print(f"   → 物理的に正しい: j = p̂/R")
    print()
    
    print("🔄 修正版での10ステップ実行:")
    current_state = create_default_state(params.num_layers)
    
    for step in range(10):
        old_E = current_state.E.copy()
        print(f"\nStep {step+1}:")
        current_state = physical_engine.step(current_state, pressure, dt=0.1)
        dE = current_state.E - old_E
        
        print(f"   結果: E={current_state.E[0]:.6f}, ΔE={dE[0]:.6f}")
        
        # LEAP判定
        leap_occurred = False
        for i, (energy, theta) in enumerate(zip(current_state.E, params.Theta_values)):
            if energy >= theta:
                print(f"   🚀 LEAP発生！！！ レイヤー{i+1} E={energy:.6f} >= Theta={theta}")
                leap_occurred = True
                current_state.E[i] = 0.0
                break
        
        if leap_occurred:
            print(f"   🎉 修正版でLEAP成功！")
            break
    
    if not leap_occurred:
        print(f"\n   継続実行で閾値到達まで: {params.Theta_values[0] / dE[0]:.0f}ステップ必要")


if __name__ == "__main__":
    test_physical_correction()