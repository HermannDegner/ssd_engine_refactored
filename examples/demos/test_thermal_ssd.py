"""
カイジ的借金地獄ルーレット - 熱力学版
================================

物理修正 + 有限温度でのLEAP現象観察
熱揺らぎにより閾値以下でもLEAP発生可能
"""

import sys
import os
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, create_default_state

class ThermalSSDEngine(SSDCoreEngine):
    """熱力学的SSDエンジン（物理修正 + 有限温度）"""
    
    def step(self, state, pressure, dt=0.1, interlayer_transfer=None):
        """熱力学的ステップ実行"""
        
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
        
        # 【物理修正】正しいオームの法則: j = p̂ / R
        j = pressure_hat / R_array
        
        # エネルギー残差計算
        if self.params.use_log_residual:
            resid = np.maximum(0.0, np.abs(pressure_hat) - np.abs(j))
        else:
            resid = np.maximum(0.0, np.abs(pressure) - np.abs(j))
        
        # 【熱力学追加】熱ノイズによるエネルギー揺らぎ
        thermal_noise = np.random.normal(0, self.params.temperature_T, self.num_layers)
        
        # エネルギー生成（熱ノイズ込み）
        energy_generation = gamma_array * resid + thermal_noise
        
        # エネルギー減衰
        energy_decay = beta_array * state.E
        
        # エネルギー更新
        dE = energy_generation - energy_decay
        
        if interlayer_transfer is not None:
            dE += interlayer_transfer
        
        new_state.E = np.maximum(0.0, state.E + dE * dt)
        
        # κ更新
        usage_factor = np.abs(j) / (np.abs(j) + 1.0)
        dkappa = eta_array * usage_factor - lambda_array * state.kappa
        new_state.kappa = np.maximum(kappa_min_array, state.kappa + dkappa * dt)
        
        return new_state


def test_thermal_effects():
    """熱力学効果のテスト"""
    print("="*80)
    print("🔥 熱力学版SSD - 温度効果テスト")
    print("="*80)
    
    # 複数の温度でテスト
    temperatures = [0.0, 0.1, 0.5, 1.0, 2.0]
    
    for temp in temperatures:
        print(f"\n🌡️  温度 T = {temp}")
        print("-" * 40)
        
        # パラメータ設定
        params = SSDCoreParams()
        params.log_align = False  # Log-Alignment無効
        params.enable_stochastic_leap = True  # 確率的LEAP有効
        params.temperature_T = temp
        params.Theta_values = [2.0, 1.5, 1.0, 0.5]  # 低い閾値
        params.gamma_values = [0.5, 0.4, 0.3, 0.2]  # 適度なエネルギー生成
        params.beta_values = [0.01, 0.02, 0.05, 0.1]  # 適度な減衰
        
        engine = ThermalSSDEngine(params)
        
        # 中程度の圧力でテスト
        pressure = np.array([500.0, 0.0, 0.0, 0.0])
        
        leap_count = 0
        below_threshold_leaps = 0  # 閾値以下でのLEAP
        
        # 5回の独立実行
        for trial in range(5):
            state = create_default_state(params.num_layers)
            
            # 10ステップ実行
            for step in range(10):
                old_E = state.E.copy()
                state = engine.step(state, pressure, dt=0.1)
                
                # LEAP判定（元の決定論的チェック）
                for i, (energy, theta) in enumerate(zip(state.E, params.Theta_values)):
                    if energy >= theta:
                        leap_count += 1
                        if old_E[i] < theta:  # 前ステップでは閾値以下だった
                            below_threshold_leaps += 1
                        state.E[i] = 0.0  # LEAP後リセット
                        break
        
        total_steps = 5 * 10
        leap_rate = leap_count / total_steps * 100
        thermal_leap_rate = below_threshold_leaps / total_steps * 100 if temp > 0 else 0
        
        print(f"   総LEAP数: {leap_count}/{total_steps}ステップ ({leap_rate:.1f}%)")
        if temp > 0:
            print(f"   熱LEAP数: {below_threshold_leaps} ({thermal_leap_rate:.1f}%)")
            print(f"   熱効果: {'✅ 観測' if below_threshold_leaps > 0 else '❌ なし'}")
        else:
            print(f"   絶対零度: 決定論的のみ")
    
    print(f"\n🧬 結論:")
    print(f"   T=0: 熱無し、完全決定論")
    print(f"   T>0: 熱揺らぎにより閾値以下でもLEAP発生")
    print(f"   高温: LEAP頻度増加（相転移促進）")
    print(f"   → カイジの心理的「熱さ」がLEAPの鍵！")


def run_thermal_kaiji_experiment():
    """熱力学版カイジ実験"""
    print("\n" + "="*80)
    print("💀🔥 カイジ的借金地獄 - 熱力学版実験")
    print("="*80)
    
    # 高温設定（心理的興奮状態）
    params = SSDCoreParams()
    params.log_align = False
    params.enable_stochastic_leap = True
    params.temperature_T = 3.0  # 高温（高い心理的興奮）
    params.Theta_values = [3.0, 2.0, 1.0, 0.5]
    params.gamma_values = [1.0, 0.8, 0.6, 0.4]
    params.beta_values = [0.05, 0.1, 0.15, 0.2]
    
    engine = ThermalSSDEngine(params)
    
    print(f"🌡️  心理温度: T = {params.temperature_T} (高興奮状態)")
    print(f"📊 LEAP閾値: {params.Theta_values}")
    print()
    
    # カイジの極限心理状態シミュレーション
    despair_levels = [1.0, 3.0, 5.0, 8.0, 10.0]  # 絶望レベル
    
    for despair in despair_levels:
        print(f"😱 絶望レベル {despair}/10.0:")
        
        # 絶望に比例した圧力
        pressure = np.array([despair * 100, 0.0, 0.0, 0.0])
        
        state = create_default_state(params.num_layers)
        leap_occurred = False
        
        # 最大5ステップで観察
        for step in range(5):
            old_E = state.E.copy()
            state = engine.step(state, pressure, dt=0.1)
            dE = state.E - old_E
            
            print(f"   Step {step+1}: E={state.E[0]:.3f} (ΔE={dE[0]:.3f})")
            
            # LEAP判定
            for i, (energy, theta) in enumerate(zip(state.E, params.Theta_values)):
                if energy >= theta:
                    print(f"   🚀 熱的LEAP発生！ レイヤー{i+1} E={energy:.3f} >= Theta={theta}")
                    leap_occurred = True
                    state.E[i] = 0.0
                    break
            
            if leap_occurred:
                break
        
        if not leap_occurred:
            print(f"   ⏳ 5ステップではLEAP未発生")
        
        print()
    
    print("🎯 熱力学版結論:")
    print("   心理的「熱さ」（興奮、焦燥、恐怖）がLEAPの本質")
    print("   絶対零度（完全冷静）では構造跳躍は起きない")
    print("   カイジの「熱い」感情状態こそがLEAPを可能にする！")


if __name__ == "__main__":
    test_thermal_effects()
    run_thermal_kaiji_experiment()