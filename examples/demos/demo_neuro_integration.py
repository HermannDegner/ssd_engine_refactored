# -*- coding: utf-8 -*-
"""
SSD神経変調器デモ - ドロップイン接続例
=====================================

既存のSSD Coreエンジンに神経変調層を最小変更で接続するデモ。

機能:
- D1/D2ドーパミン、NE、5HT、AChの受容体別変調
- コアパラメータの非破壊的変調（コピーベース）
- プリセット神経状態（集中/探索/鎮静）での比較
- カイジ借金ルーレット with 神経状態変化

使用方法:
1. 通常のSSDエンジンと同様に初期化
2. engine.neuro_state を設定
3. 自動的に神経変調が適用される
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from dataclasses import dataclass, replace
from core.ssd_core_engine import SSDCoreEngine, SSDCoreParams, SSDCoreState
from extensions.ssd_neuro_modulators import NeuroState, NeuroConfig, modulate_params, neuro_preset


class SSDNeuroEngine(SSDCoreEngine):
    """
    神経変調対応SSDエンジン
    
    既存のSSDCoreEngineを継承し、神経変調機能を追加
    """
    
    def __init__(self, params: SSDCoreParams, neuro_config: NeuroConfig = None):
        super().__init__(params)
        self.base_params = params  # 元のパラメータを保持
        self.neuro_state = NeuroState()  # デフォルト神経状態
        self.neuro_config = neuro_config or NeuroConfig()
        
    def step(self, state: SSDCoreState, pressure, dt: float = 0.1) -> SSDCoreState:
        """
        神経変調を適用してから通常のステップ実行
        """
        # pressureをndarrayに変換（必要に応じて）
        if np.isscalar(pressure):
            pressure_array = np.full(self.base_params.num_layers, pressure)
        else:
            pressure_array = np.array(pressure)
            
        # 神経変調を適用したパラメータで実行
        modulated_params = modulate_params(self.base_params, self.neuro_state, self.neuro_config)
        
        # 一時的にパラメータを置き換え
        original_params = self.params
        self.params = modulated_params
        
        # 通常のステップ実行
        result = super().step(state, pressure_array, dt)
        
        # パラメータを元に戻す
        self.params = original_params
        
        return result


def demo_neuro_comparison():
    """神経状態による動作比較デモ"""
    
    print("=" * 80)
    print("🧠⚡ SSD神経変調器デモ - 受容体別制御")
    print("=" * 80)
    
    # 基本パラメータ（人体体温基準）
    params = SSDCoreParams(
        temperature_T=37.0,  # 人体体温基準
        enable_stochastic_leap=True,
        G0=0.001,  # 超電導回避
        g=0.01,
        Theta_values=[100.0, 80.0, 60.0, 40.0],  # 体温スケール調整済み
        alpha0=1.0,
        log_align=True
    )
    
    # 初期状態
    initial_state = SSDCoreState(
        E=np.array([0.0, 0.0, 0.0, 0.0]),
        kappa=np.array([0.9, 0.8, 0.5, 0.3]),
        t=0.0,
        step_count=0
    )
    
    pressure = 50.0  # 中程度の圧力
    
    print("\n🔬 神経状態別シミュレーション（5ステップ）")
    print("-" * 60)
    
    # 各神経状態での比較
    neuro_states = {
        "ベースライン": NeuroState(),
        "集中モード": neuro_preset("focus"),
        "探索モード": neuro_preset("explore"),
        "鎮静モード": neuro_preset("calm"),
        "ドーパミンHigh": NeuroState(D1=0.8, D2=0.2, NE=0.5, _5HT=0.3, ACh=0.4),
        "セロトニンHigh": NeuroState(D1=0.2, D2=0.4, NE=0.3, _5HT=0.8, ACh=0.5)
    }
    
    for name, neuro_state in neuro_states.items():
        print(f"\n🧠 {name}:")
        print(f"   D1={neuro_state.D1:.1f} D2={neuro_state.D2:.1f} NE={neuro_state.NE:.1f} 5HT={neuro_state._5HT:.1f} ACh={neuro_state.ACh:.1f}")
        
        engine = SSDNeuroEngine(params)
        engine.neuro_state = neuro_state
        
        state = replace(initial_state)
        leap_count = 0
        
        for step in range(5):
            state = engine.step(state, pressure, dt=0.1)
            
            # LEAP検出
            if any(E >= T for E, T in zip(state.E, engine.params.Theta_values)):
                leap_count += 1
                print(f"   Step {step+1}: 🚀LEAP! E={state.E[0]:.1f}")
            else:
                print(f"   Step {step+1}: E={state.E[0]:.1f}")
        
        print(f"   → LEAP回数: {leap_count}/5")


def demo_kaiji_neuro_progression():
    """カイジ借金ルーレット with 神経状態変化"""
    
    print("\n" + "=" * 80)
    print("🎰🧠 カイジ借金ルーレット - 神経状態進行シミュレーション")
    print("=" * 80)
    
    params = SSDCoreParams(
        temperature_T=37.0,
        enable_stochastic_leap=True,
        G0=0.001,
        g=0.01,
        Theta_values=[100.0, 80.0, 60.0, 40.0],
        alpha0=1.0
    )
    
    engine = SSDNeuroEngine(params)
    state = SSDCoreState(
        E=np.array([0.0, 0.0, 0.0, 0.0]),
        kappa=np.array([0.9, 0.8, 0.5, 0.3]),
        t=0.0,
        step_count=0
    )
    
    # カイジの心理状態進行
    stages = [
        ("冷静な計算", 30.0, NeuroState(D1=0.3, D2=0.4, NE=0.3, _5HT=0.6, ACh=0.7)),
        ("ゲーム開始", 45.0, NeuroState(D1=0.5, D2=0.3, NE=0.5, _5HT=0.4, ACh=0.6)),
        ("連敗の焦り", 65.0, NeuroState(D1=0.6, D2=0.2, NE=0.7, _5HT=0.2, ACh=0.4)),
        ("絶望的状況", 85.0, NeuroState(D1=0.8, D2=0.1, NE=0.8, _5HT=0.1, ACh=0.3)),
        ("最後の賭け", 95.0, NeuroState(D1=0.9, D2=0.1, NE=0.9, _5HT=0.1, ACh=0.2))
    ]
    
    print("\n📊 カイジの心理状態とLEAP発生パターン:")
    
    for i, (stage_name, pressure, neuro_state) in enumerate(stages):
        print(f"\n🎯 Stage {i+1}: {stage_name}")
        print(f"   圧力: {pressure:.1f} | 神経: D1={neuro_state.D1:.1f} NE={neuro_state.NE:.1f} 5HT={neuro_state._5HT:.1f}")
        
        engine.neuro_state = neuro_state
        
        leap_occurred = False
        for step in range(3):
            state = engine.step(state, pressure, dt=0.1)
            
            if any(E >= T for E, T in zip(state.E, engine.params.Theta_values)):
                print(f"   Step {step+1}: 🚀 「ざわ...ざわ...」LEAP! E={state.E[0]:.1f}")
                leap_occurred = True
                break
            else:
                print(f"   Step {step+1}: E={state.E[0]:.1f}")
        
        if not leap_occurred:
            print(f"   → {stage_name}では構造変化なし")
        else:
            print(f"   → {stage_name}で心理的転換点に到達！")


def demo_neuro_parameter_effects():
    """神経変調によるパラメータ変化の詳細表示"""
    
    print("\n" + "=" * 80)
    print("🔬⚙️ 神経変調パラメータ効果の詳細分析")
    print("=" * 80)
    
    base_params = SSDCoreParams(
        temperature_T=37.0,
        alpha0=1.0,
        G0=0.001,
        g=0.01,
        Theta_values=[100.0, 80.0, 60.0, 40.0],
        gamma_values=[0.15, 0.10, 0.08, 0.05],
        beta_values=[0.001, 0.01, 0.05, 0.1]
    )
    
    neuro_states = {
        "集中": neuro_preset("focus"),
        "探索": neuro_preset("explore"),
        "鎮静": neuro_preset("calm")
    }
    
    print("\n📊 パラメータ変調効果:")
    print("-" * 60)
    
    for name, neuro_state in neuro_states.items():
        modulated = modulate_params(base_params, neuro_state)
        
        print(f"\n🧠 {name}モード:")
        print(f"   感覚ゲイン alpha0: {base_params.alpha0:.3f} → {modulated.alpha0:.3f}")
        print(f"   LEAP閾値 Theta[0]: {base_params.Theta_values[0]:.1f} → {modulated.Theta_values[0]:.1f}")
        print(f"   活動性 gamma[0]: {base_params.gamma_values[0]:.3f} → {modulated.gamma_values[0]:.3f}")
        print(f"   安定性 beta[0]: {base_params.beta_values[0]:.3f} → {modulated.beta_values[0]:.3f}")
        print(f"   導電性 G0: {base_params.G0:.3f} → {modulated.G0:.3f}")
        print(f"   探索温度 T: {base_params.temperature_T:.1f} → {modulated.temperature_T:.1f}")


if __name__ == "__main__":
    print("🧠⚡ SSD神経変調システム統合デモ")
    
    # 基本比較デモ
    demo_neuro_comparison()
    
    # カイジ進行シミュレーション  
    demo_kaiji_neuro_progression()
    
    # パラメータ効果詳細
    demo_neuro_parameter_effects()
    
    print("\n" + "=" * 80)
    print("✅ 神経変調システム完全統合完了！")
    print("🔗 最小変更でコアエンジンに神経科学的制御を追加")
    print("🧠 D1/D2ドーパミン、NE、5HT、ACh受容体別変調実現")
    print("⚡ 物理エンジン（log整合・熱・E・Θ）と神経層の完全分離")
    print("=" * 80)