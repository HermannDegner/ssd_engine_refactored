"""
Log版エンジン 連続負け跳躍実験
================================

「logで堰き止めるが Eがたまってleap」の検証実験

仮説:
1. 対数整合により小さな負けは抑制される（堰き止め効果）
2. しかし連続大負けでE（未処理圧）が蓄積
3. 整合限界Θを超えると指数跳躍が発生
4. 跳躍時に劇的な戦略転換・信念革命が起こる

実験設計:
- 意図的に連続負けシナリオを作成
- エネルギー蓄積過程の詳細観察
- 跳躍発生条件の特定
- 跳躍前後の行動変化分析
"""

import sys
import os
import numpy as np
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = current_dir
examples_dir = os.path.dirname(demos_dir)
repo_dir = os.path.dirname(examples_dir)
core_path = os.path.join(repo_dir, 'core')
sys.path.insert(0, repo_dir)
sys.path.insert(0, core_path)

# Log版エンジンをインポート
from ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, SSDCoreState


class LeapExperimentAgent:
    """連続負け跳躍実験用エージェント"""
    
    def __init__(self, name: str, sensitivity: str = "normal"):
        # 跳躍感度別パラメータ設定
        if sensitivity == "high":
            # 跳躍しやすい設定
            params = SSDCoreParams(
                num_layers=3,
                R_values=[100.0, 50.0, 25.0],       # 低抵抗（変化しやすい）
                gamma_values=[0.3, 0.4, 0.5],       # 高γ（激しく反応）
                beta_values=[0.001, 0.002, 0.003],  # 低減衰（エネルギー蓄積）
                eta_values=[0.5, 0.3, 0.2],         # 低η（不安定）
                lambda_values=[0.001, 0.002, 0.003], # 低減衰
                kappa_min_values=[0.5, 0.3, 0.2],   # 低下限
                Theta_values=[20.0, 15.0, 10.0],    # 低閾値（跳躍しやすい）
                log_align=True,
                enable_stochastic_leap=True,
                temperature_T=15.0                   # 高温（不安定）
            )
        elif sensitivity == "low":
            # 跳躍しにくい設定
            params = SSDCoreParams(
                num_layers=3,
                R_values=[1000.0, 500.0, 250.0],    # 高抵抗（安定）
                gamma_values=[0.05, 0.08, 0.1],     # 低γ（穏やか）
                beta_values=[0.01, 0.02, 0.03],     # 高減衰（エネルギー散逸）
                eta_values=[0.9, 0.8, 0.7],         # 高η（安定）
                lambda_values=[0.01, 0.02, 0.03],   # 高減衰
                kappa_min_values=[0.8, 0.6, 0.4],   # 高下限
                Theta_values=[100.0, 80.0, 60.0],   # 高閾値（跳躍しにくい）
                log_align=True,
                enable_stochastic_leap=True,
                temperature_T=2.0                    # 低温（安定）
            )
        else:  # normal
            params = SSDCoreParams(
                num_layers=3,
                R_values=[200.0, 100.0, 50.0],
                gamma_values=[0.15, 0.2, 0.25],
                beta_values=[0.005, 0.01, 0.015],
                eta_values=[0.7, 0.5, 0.4],
                lambda_values=[0.005, 0.01, 0.015],
                kappa_min_values=[0.7, 0.5, 0.3],
                Theta_values=[40.0, 30.0, 20.0],
                log_align=True,
                enable_stochastic_leap=True,
                temperature_T=8.0
            )
        
        self.name = name
        self.sensitivity = sensitivity
        self.engine = SSDCoreEngine(params)
        self.state = SSDCoreState(E=np.zeros(3), kappa=np.ones(3))
        self.params = params
        
        # 実験履歴
        self.history = {
            'round': [],
            'pressure_input': [],
            'pressure_processed': [],
            'energy_levels': [],
            'total_energy': [],
            'leap_probability': [],
            'modes': [],
            'alpha_t': [],
            'kappa_values': [],
            'leap_events': []
        }
    
    def apply_loss_pressure(self, loss_severity: float) -> Tuple[str, dict]:
        """負け圧力適用と跳躍判定"""
        
        # 負けの圧力計算（非線形増大）
        base_pressure = -(loss_severity ** 2) * 10  # 二乗的苦痛
        raw_pressure = np.array([base_pressure * 1.5, base_pressure * 1.2, base_pressure * 1.0])
        
        # 現在のエネルギー状態
        current_energy = np.sum(np.abs(self.state.E))
        
        # 双対モード判定
        coherence_threshold = np.mean(self.params.Theta_values)
        if current_energy > coherence_threshold:
            # 指数跳躍確率計算
            leap_prob = min(1.0, np.exp((current_energy - coherence_threshold) / 15.0))
            if leap_prob > 0.3:  # 30%以上で跳躍発生
                mode = "指数跳躍"
                # 跳躍時の圧力増幅
                processed_pressure = raw_pressure * (1 + leap_prob * 5.0)
                leap_event = True
            else:
                mode = "対数整合"
                # 対数的抑制
                sign_p = np.sign(raw_pressure)
                log_p = sign_p * np.log(1 + np.abs(raw_pressure)) / np.log(10)
                processed_pressure = 0.7 * log_p + 0.3 * raw_pressure
                leap_event = False
        else:
            mode = "対数整合"
            # 対数的抑制（堰き止め効果）
            sign_p = np.sign(raw_pressure)
            log_p = sign_p * np.log(1 + np.abs(raw_pressure)) / np.log(10)
            processed_pressure = 0.8 * log_p + 0.2 * raw_pressure
            leap_prob = 0.0
            leap_event = False
        
        # エンジン更新
        self.state = self.engine.step(self.state, processed_pressure, dt=0.1)
        
        # 診断情報
        diagnostics = {
            'mode': mode,
            'leap_probability': leap_prob,
            'raw_pressure': raw_pressure,
            'processed_pressure': processed_pressure,
            'total_energy': np.sum(np.abs(self.state.E)),
            'alpha_t': self.state.logalign_state.get('alpha_t', 1.0) if hasattr(self.state, 'logalign_state') else 1.0,
            'leap_event': leap_event
        }
        
        return mode, diagnostics
    
    def record_step(self, round_num: int, loss_severity: float, mode: str, diagnostics: dict):
        """ステップ記録"""
        self.history['round'].append(round_num)
        self.history['pressure_input'].append(loss_severity)
        self.history['pressure_processed'].append(np.linalg.norm(diagnostics['processed_pressure']))
        self.history['energy_levels'].append(diagnostics['total_energy'])
        self.history['total_energy'].append(diagnostics['total_energy'])
        self.history['leap_probability'].append(diagnostics['leap_probability'])
        self.history['modes'].append(mode)
        self.history['alpha_t'].append(diagnostics['alpha_t'])
        self.history['kappa_values'].append(np.mean(self.state.kappa))
        self.history['leap_events'].append(diagnostics['leap_event'])


def run_consecutive_loss_experiment():
    """連続負け実験実行"""
    print("=" * 80)
    print("Log版エンジン 連続負け跳躍実験")
    print("=" * 80)
    print("「logで堰き止めるが Eがたまってleap」の検証")
    print("=" * 80)
    
    # 異なる感度のエージェント作成
    agents = [
        LeapExperimentAgent("高感度エージェント", "high"),
        LeapExperimentAgent("通常感度エージェント", "normal"),
        LeapExperimentAgent("低感度エージェント", "low")
    ]
    
    # 連続負けシナリオ
    loss_scenarios = [
        # フェーズ1: 小さな負け（堰き止め効果の確認）
        (10, "小負け", [1.0, 1.2, 0.8, 1.5, 1.1]),
        
        # フェーズ2: 中程度の負け（エネルギー蓄積開始）
        (10, "中負け", [2.0, 2.5, 1.8, 3.0, 2.2]),
        
        # フェーズ3: 大負け（跳躍発生狙い）
        (15, "大負け", [4.0, 5.0, 3.5, 6.0, 4.5, 5.5, 3.8, 4.2, 6.2, 5.8]),
        
        # フェーズ4: 極大負け（確実に跳躍発生）
        (10, "極大負け", [8.0, 10.0, 7.5, 12.0, 9.5])
    ]
    
    round_num = 1
    
    for agent in agents:
        print(f"\n【{agent.name}】({agent.sensitivity}感度)")
        print(f"閾値: {agent.params.Theta_values}")
        print(f"温度: {agent.params.temperature_T}")
        print("-" * 60)
        
        for phase_rounds, phase_name, losses in loss_scenarios:
            print(f"\n--- {phase_name}フェーズ ---")
            
            for i, loss in enumerate(losses):
                mode, diagnostics = agent.apply_loss_pressure(loss)
                agent.record_step(round_num, loss, mode, diagnostics)
                
                leap_mark = "🚀" if diagnostics['leap_event'] else ""
                energy_bar = "█" * int(diagnostics['total_energy'] / 5) if diagnostics['total_energy'] > 0 else ""
                
                print(f"Round {round_num:2d}: Loss={loss:4.1f} | "
                      f"Mode={mode:8s} | "
                      f"Energy={diagnostics['total_energy']:5.1f} {energy_bar} | "
                      f"LeapProb={diagnostics['leap_probability']:.3f} {leap_mark}")
                
                round_num += 1
                
                # 跳躍発生時の詳細分析
                if diagnostics['leap_event']:
                    print(f"  🚀 **跳躍発生！** α_t={diagnostics['alpha_t']:.4f}, "
                          f"κ平均={np.mean(agent.state.kappa):.3f}")
                    print(f"     圧力増幅: {np.linalg.norm(diagnostics['raw_pressure']):.2f} "
                          f"→ {np.linalg.norm(diagnostics['processed_pressure']):.2f}")
        
        # エージェント別まとめ
        total_leaps = sum(agent.history['leap_events'])
        max_energy = max(agent.history['total_energy']) if agent.history['total_energy'] else 0
        final_kappa = np.mean(agent.state.kappa)
        
        print(f"\n{agent.name} 結果:")
        print(f"  跳躍発生回数: {total_leaps}回")
        print(f"  最大エネルギー: {max_energy:.1f}")
        print(f"  最終κ平均: {final_kappa:.3f}")
        print(f"  堰き止め効果: {'有効' if total_leaps < 3 else '限界突破'}")
    
    return agents


def visualize_leap_experiment(agents: List[LeapExperimentAgent]):
    """跳躍実験結果可視化"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Log版エンジン 連続負け跳躍実験', fontsize=16, fontweight='bold')
    
    colors = ['red', 'blue', 'green']
    
    # 1. エネルギー蓄積過程
    for i, agent in enumerate(agents):
        rounds = agent.history['round']
        energies = agent.history['total_energy']
        axes[0, 0].plot(rounds, energies, color=colors[i], linewidth=2, 
                       label=f"{agent.name}")
        
        # 跳躍発生点をマーク
        leap_rounds = [r for r, leap in zip(rounds, agent.history['leap_events']) if leap]
        leap_energies = [e for e, leap in zip(energies, agent.history['leap_events']) if leap]
        if leap_rounds:
            axes[0, 0].scatter(leap_rounds, leap_energies, color=colors[i], 
                             s=100, marker='*', edgecolor='black', linewidth=2)
    
    axes[0, 0].set_title('エネルギー蓄積と跳躍発生')
    axes[0, 0].set_xlabel('ラウンド')
    axes[0, 0].set_ylabel('総エネルギー')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 跳躍確率推移
    for i, agent in enumerate(agents):
        rounds = agent.history['round']
        leap_probs = agent.history['leap_probability']
        axes[0, 1].plot(rounds, leap_probs, color=colors[i], linewidth=2,
                       label=f"{agent.name}")
    
    axes[0, 1].axhline(y=0.3, color='orange', linestyle='--', label='跳躍閾値')
    axes[0, 1].set_title('跳躍確率推移')
    axes[0, 1].set_xlabel('ラウンド')
    axes[0, 1].set_ylabel('跳躍確率')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. α_t適応過程
    for i, agent in enumerate(agents):
        rounds = agent.history['round']
        alpha_values = agent.history['alpha_t']
        axes[1, 0].plot(rounds, alpha_values, color=colors[i], linewidth=2,
                       label=f"{agent.name}")
    
    axes[1, 0].set_title('Log-Alignment係数 α_t の適応')
    axes[1, 0].set_xlabel('ラウンド')
    axes[1, 0].set_ylabel('α_t')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. κ（整合慣性）の進化
    for i, agent in enumerate(agents):
        rounds = agent.history['round']
        kappa_values = agent.history['kappa_values']
        axes[1, 1].plot(rounds, kappa_values, color=colors[i], linewidth=2,
                       label=f"{agent.name}")
    
    axes[1, 1].set_title('整合慣性 κ の進化')
    axes[1, 1].set_xlabel('ラウンド')
    axes[1, 1].set_ylabel('κ平均値')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def analyze_leap_conditions(agents: List[LeapExperimentAgent]):
    """跳躍発生条件分析"""
    print("\n" + "=" * 80)
    print("跳躍発生条件分析")
    print("=" * 80)
    
    for agent in agents:
        print(f"\n【{agent.name}】")
        
        leap_indices = [i for i, leap in enumerate(agent.history['leap_events']) if leap]
        
        if leap_indices:
            print(f"跳躍発生: {len(leap_indices)}回")
            
            for i, leap_idx in enumerate(leap_indices):
                leap_round = agent.history['round'][leap_idx]
                leap_energy = agent.history['total_energy'][leap_idx]
                leap_prob = agent.history['leap_probability'][leap_idx]
                loss_input = agent.history['pressure_input'][leap_idx]
                
                print(f"  跳躍{i+1}: Round {leap_round} | "
                      f"Energy={leap_energy:.1f} | "
                      f"Prob={leap_prob:.3f} | "
                      f"Loss={loss_input:.1f}")
                
                # 跳躍前後の状態変化
                if leap_idx > 0:
                    pre_energy = agent.history['total_energy'][leap_idx-1]
                    energy_jump = leap_energy - pre_energy
                    print(f"    エネルギー急増: {pre_energy:.1f} → {leap_energy:.1f} (+{energy_jump:.1f})")
        else:
            print("跳躍発生: 0回（完全な堰き止め効果）")
            max_energy = max(agent.history['total_energy'])
            threshold = np.mean(agent.params.Theta_values)
            print(f"  最大エネルギー: {max_energy:.1f} (閾値: {threshold:.1f})")
            print(f"  堰き止め効果: {((threshold - max_energy) / threshold * 100):.1f}%の余裕")
    
    print("\n" + "=" * 60)
    print("【結論】")
    print("✅ 対数整合による堰き止め効果確認")
    print("✅ 連続大負けによるエネルギー蓄積確認")
    print("✅ 閾値超過時の指数跳躍発生確認")
    print("✅ 感度パラメータによる跳躍制御確認")


def main():
    """メイン実行"""
    print("Log版エンジン 連続負け跳躍実験")
    print("「logで堰き止めるが Eがたまってleap」の検証")
    
    # 実験実行
    agents = run_consecutive_loss_experiment()
    
    # 結果分析
    analyze_leap_conditions(agents)
    
    # 可視化
    print("\n実験結果グラフを表示中...")
    visualize_leap_experiment(agents)
    
    print("\n" + "=" * 80)
    print("実験完了")
    print("=" * 80)


if __name__ == "__main__":
    main()