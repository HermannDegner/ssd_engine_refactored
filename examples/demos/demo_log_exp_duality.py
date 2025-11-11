"""
対数整合と指数跳躍：SSDにおける非線形世界の線形化モデル
==================================================

Log版エンジンによる「対数整合 ↔ 指数跳躍」双対性の実装デモ

理論的基盤：
1. 非線形世界の対数的線形化（ウェーバー・フェヒナー法則）
2. 整合限界を超えた指数的跳躍過程
3. 線形安定化と非連続創発の双対モード
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

import numpy as np
import matplotlib.pyplot as plt
from ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, SSDCoreState
from dataclasses import dataclass
from typing import List, Tuple
import matplotlib

# 日本語フォント設定
matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']


@dataclass
class LogExpDualityParams:
    """対数整合・指数跳躍双対性パラメータ"""
    # 対数整合パラメータ
    weber_constant: float = 0.1  # ウェーバー定数
    linearization_base: float = 10.0  # 対数底
    
    # 指数跳躍パラメータ
    critical_threshold: float = 50.0  # 整合限界閾値 Θ
    exponential_gamma: float = 5.0  # 指数増大定数 γ
    jump_intensity: float = 1.0  # 跳躍強度 h_0
    
    # 双対性制御
    coherence_weight: float = 0.7  # 整合モード重み
    leap_sensitivity: float = 0.3  # 跳躍感度


class LogExpDualityEngine:
    """対数整合・指数跳躍双対性エンジン"""
    
    def __init__(self, ssd_engine: SSDCoreEngine, duality_params: LogExpDualityParams):
        self.ssd_engine = ssd_engine
        self.params = duality_params
        self.history = {
            'time': [],
            'raw_input': [],
            'log_coherent': [],
            'exp_leap': [],
            'coherence_mode': [],
            'leap_probability': [],
            'total_energy': []
        }
    
    def weber_fechner_transform(self, stimulus: np.ndarray) -> np.ndarray:
        """
        ウェーバー・フェヒナー法則による対数変換
        感覚強度 = k * log(刺激強度/閾値)
        """
        k = self.params.weber_constant
        threshold = 1.0
        return k * np.log(np.maximum(stimulus, threshold) / threshold)
    
    def logarithmic_coherence(self, raw_pressure: np.ndarray) -> np.ndarray:
        """
        対数整合：非線形世界の線形化処理
        - 意味圧の対数スケール圧縮
        - 線形的に扱える形への変換
        """
        # ウェーバー・フェヒナー変換
        linearized = self.weber_fechner_transform(raw_pressure)
        
        # 対数整合による安定化
        base = self.params.linearization_base
        coherent_pressure = np.sign(linearized) * np.log(1 + np.abs(linearized)) / np.log(base)
        
        return coherent_pressure
    
    def exponential_leap_probability(self, energy: np.ndarray) -> np.ndarray:
        """
        指数跳躍確率：整合限界超過時の非連続転換
        h = h_0 * exp((E - Θ)/γ)
        """
        Theta = self.params.critical_threshold
        gamma = self.params.exponential_gamma
        h0 = self.params.jump_intensity
        
        # エネルギーが閾値を超えた部分のみ指数増大
        excess_energy = np.maximum(energy - Theta, 0)
        leap_prob = h0 * np.exp(excess_energy / gamma)
        
        return np.minimum(leap_prob, 1.0)  # 確率なので上限1
    
    def dual_mode_processing(self, raw_pressure: np.ndarray, current_state: SSDCoreState) -> Tuple[np.ndarray, dict]:
        """
        双対モード処理：対数整合と指数跳躍の統合
        """
        # 1. 対数整合モード（線形化・安定化）
        coherent_pressure = self.logarithmic_coherence(raw_pressure)
        
        # 2. 現在のエネルギー状態評価
        total_energy = np.sum(current_state.E)
        
        # 3. 指数跳躍確率計算
        leap_probs = self.exponential_leap_probability(current_state.E)
        max_leap_prob = np.max(leap_probs)
        
        # 4. 双対モード重み計算
        coherence_weight = self.params.coherence_weight * (1 - max_leap_prob)
        leap_weight = self.params.leap_sensitivity * max_leap_prob
        
        # 5. 統合圧力計算
        if max_leap_prob > 0.5:  # 跳躍モード優勢
            # 指数的増強による非連続変化
            leap_amplification = 1 + leap_weight * np.exp(total_energy / self.params.exponential_gamma)
            final_pressure = raw_pressure * leap_amplification
            mode = "指数跳躍"
        else:  # 整合モード優勢
            # 対数的安定化による線形処理
            final_pressure = coherence_weight * coherent_pressure + (1 - coherence_weight) * raw_pressure
            mode = "対数整合"
        
        # 診断情報
        diagnostics = {
            'mode': mode,
            'coherent_pressure': coherent_pressure,
            'leap_probability': max_leap_prob,
            'coherence_weight': coherence_weight,
            'leap_weight': leap_weight,
            'total_energy': total_energy
        }
        
        return final_pressure, diagnostics
    
    def step(self, raw_pressure: np.ndarray, state: SSDCoreState, dt: float = 0.1) -> Tuple[SSDCoreState, dict]:
        """双対性エンジンの1ステップ実行"""
        
        # 双対モード処理
        processed_pressure, diagnostics = self.dual_mode_processing(raw_pressure, state)
        
        # SSDコアエンジンで状態更新
        new_state = self.ssd_engine.step(state, processed_pressure, dt)
        
        # 履歴記録
        self.history['time'].append(len(self.history['time']) * dt)
        self.history['raw_input'].append(np.linalg.norm(raw_pressure))
        self.history['log_coherent'].append(np.linalg.norm(diagnostics['coherent_pressure']))
        self.history['exp_leap'].append(diagnostics['leap_probability'])
        self.history['coherence_mode'].append(1 if diagnostics['mode'] == "対数整合" else 0)
        self.history['leap_probability'].append(diagnostics['leap_probability'])
        self.history['total_energy'].append(diagnostics['total_energy'])
        
        return new_state, diagnostics


def demo_nonlinear_world_linearization():
    """非線形世界の線形化デモ"""
    print("=" * 60)
    print("1. 非線形世界の対数的線形化（ウェーバー・フェヒナー法則）")
    print("=" * 60)
    
    # エンジン設定
    params = SSDCoreParams(
        num_layers=4,
        R_values=[100.0, 50.0, 25.0, 10.0],
        gamma_values=[0.15, 0.12, 0.10, 0.08],
        beta_values=[0.01, 0.02, 0.03, 0.04],
        eta_values=[0.8, 0.6, 0.4, 0.3],
        lambda_values=[0.01, 0.02, 0.03, 0.04],
        kappa_min_values=[0.8, 0.6, 0.4, 0.2],
        Theta_values=[50.0, 40.0, 30.0, 20.0],
        log_align=True,
        alpha0=1.0
    )
    
    ssd_engine = SSDCoreEngine(params)
    duality_params = LogExpDualityParams(
        critical_threshold=200.0,  # 非常に高い閾値
        exponential_gamma=10.0,   # 緩やかな指数増大
        coherence_weight=0.9,     # 整合モード優勢
        leap_sensitivity=0.1      # 低い跳躍感度
    )
    dual_engine = LogExpDualityEngine(ssd_engine, duality_params)
    
    # 非線形入力信号（距離の二乗反比例的な「意味圧」）
    time_steps = 100
    distances = np.linspace(1, 10, time_steps)
    nonlinear_inputs = []
    
    for i, d in enumerate(distances):
        # 意味圧は距離の二乗に反比例 + ランダム変動
        meaning_pressure = 100.0 / (d ** 2) + 10 * np.sin(i * 0.1) + np.random.normal(0, 2)
        nonlinear_inputs.append(np.array([meaning_pressure, meaning_pressure*0.8, meaning_pressure*0.6, meaning_pressure*0.4]))
    
    # シミュレーション実行
    state = SSDCoreState(E=np.zeros(4), kappa=np.ones(4))
    
    for i, raw_input in enumerate(nonlinear_inputs):
        state, diagnostics = dual_engine.step(raw_input, state)
        
        if i % 20 == 0:
            print(f"Step {i:3d}: Raw={np.linalg.norm(raw_input):6.2f}, "
                  f"Mode={diagnostics['mode']:8s}, "
                  f"LeapProb={diagnostics['leap_probability']:.3f}")
    
    print("\n✅ 非線形世界の線形化完了")
    return dual_engine


def demo_coherence_to_leap_transition():
    """整合から跳躍への転換デモ"""
    print("\n" + "=" * 60)
    print("2. 線形整合から指数跳躍への転換")
    print("=" * 60)
    
    # 高感度設定
    params = SSDCoreParams(
        num_layers=3,
        R_values=[200.0, 100.0, 50.0],
        gamma_values=[0.2, 0.15, 0.1],
        beta_values=[0.005, 0.01, 0.02],
        eta_values=[0.9, 0.7, 0.5],
        lambda_values=[0.005, 0.01, 0.02],
        kappa_min_values=[0.9, 0.7, 0.5],
        Theta_values=[30.0, 20.0, 10.0],  # 低い閾値で跳躍しやすく
        log_align=True,
        enable_stochastic_leap=True,
        temperature_T=10.0  # 高温で確率的跳躍
    )
    
    ssd_engine = SSDCoreEngine(params)
    duality_params = LogExpDualityParams(
        critical_threshold=100.0,  # 高い閾値で整合モード優勢
        exponential_gamma=8.0,    # 緩やかな指数増大
        leap_sensitivity=0.2      # 低い跳躍感度
    )
    dual_engine = LogExpDualityEngine(ssd_engine, duality_params)
    
    # 段階的に増大する圧力（整合限界のテスト）
    pressure_phases = [
        (30, np.array([5.0, 4.0, 3.0])),    # Phase 1: 整合範囲内
        (30, np.array([15.0, 12.0, 9.0])),  # Phase 2: 整合限界近傍
        (40, np.array([50.0, 40.0, 30.0]))  # Phase 3: 整合限界超過→跳躍
    ]
    
    state = SSDCoreState(E=np.zeros(3), kappa=np.ones(3))
    phase_transitions = []
    
    print(f"{'Phase':<8} {'Step':<6} {'Pressure':<10} {'Energy':<10} {'Mode':<10} {'LeapProb':<10}")
    print("-" * 70)
    
    step_count = 0
    for phase_num, (steps, pressure) in enumerate(pressure_phases, 1):
        phase_start_energy = np.sum(state.E)
        
        for i in range(steps):
            state, diagnostics = dual_engine.step(pressure, state)
            step_count += 1
            
            if i % 10 == 0 or diagnostics['leap_probability'] > 0.3:
                print(f"Phase{phase_num:<3} {step_count:<6} {np.linalg.norm(pressure):<10.2f} "
                      f"{diagnostics['total_energy']:<10.2f} {diagnostics['mode']:<10} "
                      f"{diagnostics['leap_probability']:<10.3f}")
        
        phase_end_energy = np.sum(state.E)
        energy_change = phase_end_energy - phase_start_energy
        phase_transitions.append((phase_num, pressure, energy_change))
        print(f"  → Phase {phase_num} 終了: エネルギー変化 = {energy_change:.2f}")
    
    print("\n✅ 整合→跳躍転換デモ完了")
    return dual_engine, phase_transitions


def demo_knowledge_paradigm_shift():
    """知的パラダイムシフトのモデル化"""
    print("\n" + "=" * 60)
    print("3. 科学的思考におけるパラダイムシフト")
    print("=" * 60)
    
    # 知的システム設定
    params = SSDCoreParams(
        num_layers=3,  # 安全な3層構造
        R_values=[500.0, 200.0, 100.0],
        gamma_values=[0.1, 0.15, 0.2],
        beta_values=[0.001, 0.01, 0.02],
        eta_values=[0.95, 0.8, 0.6],
        lambda_values=[0.001, 0.01, 0.02],
        kappa_min_values=[0.95, 0.8, 0.6],
        Theta_values=[100.0, 80.0, 60.0],
        log_align=True,
        enable_stochastic_leap=True,
        temperature_T=5.0
    )
    
    ssd_engine = SSDCoreEngine(params)
    duality_params = LogExpDualityParams(
        weber_constant=0.05,     # 繊細な知覚
        critical_threshold=200.0,  # 非常に高い知的閾値
        exponential_gamma=15.0,  # 革命的な跳躍
        coherence_weight=0.95,   # 通常は強く整合優勢
        leap_sensitivity=0.1     # 非常に慎重な跳躍
    )
    dual_engine = LogExpDualityEngine(ssd_engine, duality_params)
    
    # 科学的発見シナリオ
    scenarios = [
        ("既存理論での説明", 50, np.array([10.0, 8.0, 6.0])),
        ("矛盾データの蓄積", 100, np.array([25.0, 20.0, 15.0])),
        ("新発見・革命的洞察", 80, np.array([100.0, 80.0, 60.0])),
        ("新パラダイム安定化", 70, np.array([15.0, 12.0, 9.0]))
    ]
    
    state = SSDCoreState(E=np.zeros(3), kappa=np.ones(3))
    paradigm_history = []
    
    print(f"{'Scenario':<20} {'Mode':<12} {'Energy':<8} {'LeapProb':<8} {'Description'}")
    print("-" * 80)
    
    for scenario_name, steps, pressure in scenarios:
        scenario_start = len(dual_engine.history['time'])
        
        for i in range(steps):
            state, diagnostics = dual_engine.step(pressure, state)
            
            if i == steps - 1:  # 各シナリオの最終状態
                if diagnostics['mode'] == "対数整合":
                    description = "安定的知識蓄積"
                else:
                    description = "パラダイム転換！"
                
                print(f"{scenario_name:<20} {diagnostics['mode']:<12} "
                      f"{diagnostics['total_energy']:<8.1f} {diagnostics['leap_probability']:<8.3f} "
                      f"{description}")
        
        scenario_end = len(dual_engine.history['time'])
        paradigm_history.append((scenario_name, scenario_start, scenario_end))
    
    print("\n✅ パラダイムシフトモデル完了")
    return dual_engine, paradigm_history


def visualize_log_exp_duality(dual_engine, title="対数整合と指数跳躍の双対性"):
    """双対性の可視化"""
    
    if not dual_engine.history['time']:
        print("⚠️ 履歴データがありません")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    time = dual_engine.history['time']
    
    # 1. 入力と対数変換
    axes[0, 0].plot(time, dual_engine.history['raw_input'], 'b-', label='生入力（非線形）', linewidth=2)
    axes[0, 0].plot(time, dual_engine.history['log_coherent'], 'g-', label='対数整合', linewidth=2)
    axes[0, 0].set_title('非線形世界の線形化')
    axes[0, 0].set_xlabel('時間')
    axes[0, 0].set_ylabel('圧力強度')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 指数跳躍確率
    axes[0, 1].plot(time, dual_engine.history['exp_leap'], 'r-', label='跳躍確率', linewidth=2)
    axes[0, 1].axhline(y=0.5, color='orange', linestyle='--', label='跳躍閾値')
    axes[0, 1].set_title('指数跳躍確率')
    axes[0, 1].set_xlabel('時間')
    axes[0, 1].set_ylabel('跳躍確率')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. 双対モード切り替え
    axes[1, 0].fill_between(time, dual_engine.history['coherence_mode'], 
                           alpha=0.6, color='green', label='対数整合モード')
    axes[1, 0].fill_between(time, [1-x for x in dual_engine.history['coherence_mode']], 
                           alpha=0.6, color='red', label='指数跳躍モード')
    axes[1, 0].set_title('双対モード切り替え')
    axes[1, 0].set_xlabel('時間')
    axes[1, 0].set_ylabel('モード')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. 総エネルギー変化
    axes[1, 1].plot(time, dual_engine.history['total_energy'], 'purple', linewidth=2)
    axes[1, 1].set_title('システム総エネルギー')
    axes[1, 1].set_xlabel('時間')
    axes[1, 1].set_ylabel('エネルギー')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def main():
    """対数整合・指数跳躍双対性の統合デモ"""
    print("対数整合と指数跳躍：SSDにおける非線形世界の線形化モデル")
    print("=" * 80)
    print("Log版エンジンによる「対数整合 ↔ 指数跳躍」双対性の完全実装")
    print("=" * 80)
    
    # デモ1: 非線形世界の線形化
    dual_engine1 = demo_nonlinear_world_linearization()
    
    # デモ2: 整合→跳躍転換
    dual_engine2, transitions = demo_coherence_to_leap_transition()
    
    # デモ3: パラダイムシフト
    dual_engine3, paradigms = demo_knowledge_paradigm_shift()
    
    # 可視化
    print("\n" + "=" * 60)
    print("可視化結果")
    print("=" * 60)
    
    visualize_log_exp_duality(dual_engine1, "非線形世界の対数的線形化")
    visualize_log_exp_duality(dual_engine2, "整合限界と指数跳躍")
    visualize_log_exp_duality(dual_engine3, "科学的パラダイムシフト")
    
    # 理論的まとめ
    print("\n" + "=" * 80)
    print("【理論的統合】")
    print("=" * 80)
    print("✅ 対数整合（Logarithmic Coherence）:")
    print("   - ウェーバー・フェヒナー法則による非線形→線形変換")
    print("   - 意味圧の最小エネルギー最適化")
    print("   - 安定的な知覚・認知処理")
    print()
    print("✅ 指数跳躍（Exponential Leap）:")
    print("   - 整合限界超過時の h = h₀exp((E-Θ)/γ) 跳躍")
    print("   - 非連続的状態遷移・相転移")
    print("   - 創発・革新・パラダイムシフト")
    print()
    print("✅ 双対性統合（Log-Exp Duality）:")
    print("   - Linearization (log) ↔ Critical Transition (exp)")
    print("   - 生物感覚から科学思考まで貫く統一原理")
    print("   - SSD体系における中核的二軸の数理表現")
    print()
    print("🎯 Log版エンジンは、この理論を完全に実装し、")
    print("   非線形世界の線形化とその破綻を統一的にモデル化しています。")


if __name__ == "__main__":
    main()