"""
ルーレット with SSD Log版エンジン
===================================

Log版エンジンによる対数整合・指数跳躍システムを使用したルーレットゲーム

【理論的進化】
- Log-Alignment: 勝敗の非線形な感情的衝撃を対数的に線形化
- 指数跳躍: 大勝/大負けの閾値超過時に戦略的パラダイムシフト発生
- 双対性統合: 安定的学習（整合モード）↔ 劇的転換（跳躍モード）

【偏見育成の高度化】
従来版: κ（整合慣性）による固定的偏見
Log版: 対数整合による適応的偏見 + 指数跳躍による劇的信念転換

1. 対数整合による偏見安定化:
   - 小さな勝敗: 対数変換で影響を抑制、偏見を維持
   - 感情的過反応を防ぐ「合理的」学習システム

2. 指数跳躍による信念革命:
   - 大勝/大負け: 閾値超過で指数的確率増加
   - パーソナリティ全体の劇的再構築
   - 「人生観が変わる一夜」の数理モデル

3. 性格別双対性パラメータ:
   - cautious: 高い整合閾値（保守的）、低い跳躍感度
   - aggressive: 低い整合閾値（変化敏感）、高い跳躍感度  
   - balanced: 中間値だが、跳躍時の変化が最も複雑
"""

import sys
import os
import random
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
core_path = os.path.join(parent_dir, 'core')
sys.path.insert(0, parent_dir)
sys.path.insert(0, core_path)

# Log版エンジンをインポート
from ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, SSDCoreState
from ssd_human_module import HumanAgent, HumanPressure, HumanLayer


@dataclass
class LogRoulettePersonality:
    """Log版ルーレット性格定義"""
    name: str
    
    # Log版エンジンパラメータ
    log_params: SSDCoreParams
    
    # 双対性パラメータ
    coherence_weight: float = 0.8  # 整合モード重み
    leap_sensitivity: float = 0.2  # 跳躍感度
    
    # 賭け戦略
    base_bet_ratio: float = 0.1    # 基本賭け金比率
    color_preference: str = "red"  # 色の好み
    
    # 偏見の解釈方法
    bias_interpretation: str = "trend"  # "trend", "intuition", "pattern"


class LogRouletteAgent:
    """Log版エンジンによるルーレットエージェント"""
    
    def __init__(self, personality: LogRoulettePersonality, initial_money: int = 1000):
        self.personality = personality
        self.money = initial_money
        self.initial_money = initial_money
        
        # Log版エンジン初期化
        self.log_engine = SSDCoreEngine(personality.log_params)
        self.state = SSDCoreState(
            E=np.zeros(personality.log_params.num_layers),
            kappa=np.ones(personality.log_params.num_layers)
        )
        
        # 履歴
        self.history = {
            'rounds': [],
            'money': [initial_money],
            'bets': [],
            'outcomes': [],
            'modes': [],  # 整合/跳躍モード
            'leap_probs': [],  # 跳躍確率
            'alpha_t': [],  # Log-Alignment係数
            'energy_levels': []
        }
    
    def get_emotional_pressure(self, outcome: str, bet_amount: int, winnings: int) -> np.ndarray:
        """感情的圧力計算（Log版用）"""
        layers = self.personality.log_params.num_layers
        
        if outcome == "win":
            # 勝利の喜び（非線形: 大勝ちほど爆発的喜び）
            joy_intensity = winnings / max(bet_amount, 1)  # 倍率
            base_pressure = joy_intensity ** 1.5  # 非線形増大
            
            # 性格別の圧力分散
            if self.personality.bias_interpretation == "trend":
                # 流れ重視: CORE層に集中
                pressure = np.array([base_pressure * 0.3, base_pressure * 1.5, base_pressure * 0.8, base_pressure * 0.4][:layers])
            elif self.personality.bias_interpretation == "intuition":
                # 直感重視: BASE層に集中
                pressure = np.array([base_pressure * 2.0, base_pressure * 0.5, base_pressure * 0.3, base_pressure * 0.2][:layers])
            else:  # pattern
                # パターン重視: UPPER層に集中
                pressure = np.array([base_pressure * 0.2, base_pressure * 0.3, base_pressure * 0.5, base_pressure * 2.0][:layers])
        
        else:  # lose
            # 敗北の苦痛（非線形: 大負けほど絶望的）
            pain_intensity = bet_amount / max(self.money + bet_amount, 1)  # 資産比
            base_pressure = -(pain_intensity ** 2.0) * 100  # 負の二乗的苦痛
            
            # 性格別の圧力分散（負の感情）
            if self.personality.bias_interpretation == "trend":
                pressure = np.array([base_pressure * 0.5, base_pressure * 1.8, base_pressure * 1.0, base_pressure * 0.7][:layers])
            elif self.personality.bias_interpretation == "intuition":
                pressure = np.array([base_pressure * 2.5, base_pressure * 0.8, base_pressure * 0.5, base_pressure * 0.2][:layers])
            else:  # pattern
                pressure = np.array([base_pressure * 0.3, base_pressure * 0.5, base_pressure * 0.7, base_pressure * 2.5][:layers])
        
        return pressure
    
    def detect_mode_transition(self, pressure: np.ndarray) -> Tuple[str, float, dict]:
        """双対モード判定"""
        # 現在のエネルギー状態
        total_energy = np.sum(np.abs(self.state.E))
        
        # 指数跳躍確率計算
        coherence_threshold = 50.0  # 整合限界
        if total_energy > coherence_threshold:
            leap_prob = min(1.0, self.personality.leap_sensitivity * 
                          np.exp((total_energy - coherence_threshold) / 20.0))
        else:
            leap_prob = 0.0
        
        # モード判定
        if leap_prob > 0.5:
            mode = "指数跳躍"
            # 跳躍時の圧力増幅
            amplified_pressure = pressure * (1 + leap_prob * 3.0)
        else:
            mode = "対数整合"
            # 整合時の圧力対数化
            coherence_weight = self.personality.coherence_weight
            sign_pressure = np.sign(pressure)
            log_pressure = sign_pressure * np.log(1 + np.abs(pressure)) / np.log(10)
            amplified_pressure = coherence_weight * log_pressure + (1 - coherence_weight) * pressure
        
        diagnostics = {
            'total_energy': total_energy,
            'leap_probability': leap_prob,
            'mode': mode,
            'alpha_t': self.state.logalign_state.get('alpha_t', 1.0) if hasattr(self.state, 'logalign_state') else 1.0
        }
        
        return mode, leap_prob, diagnostics
    
    def decide_bet(self) -> Tuple[str, int]:
        """賭け決定（Log版双対性システム）"""
        if self.money <= 10:
            return "pass", 0
        
        # 現在の状態に基づく判断
        energy_sum = np.sum(self.state.E)
        kappa_avg = np.mean(self.state.kappa)
        
        # 基本賭け金
        base_bet = max(10, int(self.money * self.personality.base_bet_ratio))
        
        # 性格別の戦略的解釈
        if self.personality.bias_interpretation == "trend":
            # CORE層のκを「流れ」として解釈
            trend_factor = self.state.kappa[1] if len(self.state.kappa) > 1 else kappa_avg
            bet_multiplier = 0.5 + trend_factor * 0.8
            
        elif self.personality.bias_interpretation == "intuition":
            # BASE層のκを「直感の確信度」として解釈
            intuition_factor = self.state.kappa[0]
            bet_multiplier = 0.3 + intuition_factor * 1.2
            
        else:  # pattern
            # UPPER層のκを「パターン認識精度」として解釈
            pattern_factor = self.state.kappa[-1]
            bet_multiplier = 0.4 + pattern_factor * 1.0
        
        # エネルギー状態による調整
        if energy_sum > 20:  # 高エネルギー状態
            bet_multiplier *= 1.5  # より大胆に
        elif energy_sum < -20:  # 負のエネルギー状態
            bet_multiplier *= 0.6  # より慎重に
        
        bet_amount = min(int(base_bet * bet_multiplier), self.money // 2)
        bet_amount = max(10, bet_amount)
        
        # 色の選択（基本的には好みの色、但し状態により変化）
        if abs(energy_sum) > 30:  # 極端な状態では逆張り
            bet_color = "black" if self.personality.color_preference == "red" else "red"
        else:
            bet_color = self.personality.color_preference
        
        return bet_color, bet_amount
    
    def process_outcome(self, bet_color: str, bet_amount: int, result_color: str, result_number: int):
        """結果処理とLog版エンジン更新"""
        if bet_color == "pass":
            return
        
        # 勝敗判定
        won = (bet_color == result_color)
        
        if won:
            winnings = bet_amount  # 1:1の配当
            self.money += winnings
            outcome = "win"
        else:
            winnings = 0
            self.money -= bet_amount
            outcome = "lose"
        
        # 感情的圧力計算
        pressure = self.get_emotional_pressure(outcome, bet_amount, winnings)
        
        # 双対モード判定
        mode, leap_prob, diagnostics = self.detect_mode_transition(pressure)
        
        # Log版エンジンで状態更新
        self.state = self.log_engine.step(self.state, pressure, dt=0.1)
        
        # 履歴記録
        self.history['rounds'].append(len(self.history['rounds']) + 1)
        self.history['money'].append(self.money)
        self.history['bets'].append(f"{bet_color}:{bet_amount}")
        self.history['outcomes'].append(f"{result_color}:{result_number}")
        self.history['modes'].append(mode)
        self.history['leap_probs'].append(leap_prob)
        self.history['alpha_t'].append(diagnostics['alpha_t'])
        self.history['energy_levels'].append(diagnostics['total_energy'])


def create_log_personalities() -> List[LogRoulettePersonality]:
    """Log版ルーレット性格作成"""
    
    base_params = {
        'num_layers': 4,
        'log_align': True,
        'enable_stochastic_leap': True
    }
    
    personalities = []
    
    # 1. 慎重派（Cautious）
    cautious_params = SSDCoreParams(
        **base_params,
        R_values=[2000.0, 500.0, 200.0, 100.0],      # 高抵抗（変化しにくい）
        gamma_values=[0.05, 0.08, 0.12, 0.15],       # 低γ（ゆっくり学習）
        beta_values=[0.001, 0.005, 0.01, 0.02],      # 低減衰
        eta_values=[0.95, 0.8, 0.6, 0.4],            # 高η（しっかり学習）
        lambda_values=[0.001, 0.005, 0.01, 0.02],    # 低減衰率
        kappa_min_values=[0.9, 0.8, 0.6, 0.4],       # 高下限
        Theta_values=[80.0, 60.0, 40.0, 30.0],       # 高閾値（跳躍しにくい）
        temperature_T=2.0                             # 低温（安定的）
    )
    
    personalities.append(LogRoulettePersonality(
        name="慎重派ケン",
        log_params=cautious_params,
        coherence_weight=0.9,    # 強い整合偏重
        leap_sensitivity=0.1,    # 低い跳躍感度
        base_bet_ratio=0.05,     # 少額ベット
        color_preference="red",
        bias_interpretation="trend"
    ))
    
    # 2. 攻撃派（Aggressive）  
    aggressive_params = SSDCoreParams(
        **base_params,
        R_values=[500.0, 200.0, 100.0, 50.0],        # 低抵抗（変化しやすい）
        gamma_values=[0.2, 0.25, 0.3, 0.35],         # 高γ（激しく学習）
        beta_values=[0.01, 0.02, 0.03, 0.05],        # 高減衰
        eta_values=[0.7, 0.5, 0.3, 0.2],             # 低η（浅い学習）
        lambda_values=[0.01, 0.02, 0.03, 0.05],      # 高減衰率
        kappa_min_values=[0.6, 0.4, 0.2, 0.1],       # 低下限
        Theta_values=[30.0, 25.0, 20.0, 15.0],       # 低閾値（跳躍しやすい）
        temperature_T=15.0                            # 高温（不安定）
    )
    
    personalities.append(LogRoulettePersonality(
        name="攻撃派サム",
        log_params=aggressive_params,
        coherence_weight=0.5,    # 中程度の整合
        leap_sensitivity=0.4,    # 高い跳躍感度
        base_bet_ratio=0.2,      # 大額ベット
        color_preference="black",
        bias_interpretation="intuition"
    ))
    
    # 3. バランス派（Balanced）
    balanced_params = SSDCoreParams(
        **base_params,
        R_values=[1000.0, 300.0, 150.0, 75.0],       # 中間抵抗
        gamma_values=[0.1, 0.15, 0.2, 0.25],         # 中間γ
        beta_values=[0.005, 0.01, 0.02, 0.03],       # 中間減衰
        eta_values=[0.8, 0.6, 0.4, 0.3],             # 中間η
        lambda_values=[0.005, 0.01, 0.02, 0.03],     # 中間減衰率
        kappa_min_values=[0.8, 0.6, 0.4, 0.2],       # 中間下限
        Theta_values=[50.0, 40.0, 30.0, 20.0],       # 中間閾値
        temperature_T=8.0                             # 中間温度
    )
    
    personalities.append(LogRoulettePersonality(
        name="バランス派リン",
        log_params=balanced_params,
        coherence_weight=0.7,    # 適度な整合偏重
        leap_sensitivity=0.25,   # 中程度の跳躍感度
        base_bet_ratio=0.1,      # 中額ベット
        color_preference="red",
        bias_interpretation="pattern"
    ))
    
    return personalities


def play_log_roulette_round() -> Tuple[str, int]:
    """ルーレット1回転"""
    numbers = list(range(0, 37))  # 0-36
    result_number = random.choice(numbers)
    
    if result_number == 0:
        result_color = "green"
    elif result_number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
        result_color = "red"
    else:
        result_color = "black"
    
    return result_color, result_number


def simulate_log_roulette_session(agents: List[LogRouletteAgent], rounds: int = 100):
    """Log版ルーレットセッション実行"""
    print("=" * 80)
    print("Log版エンジン ルーレットシミュレーション開始")
    print("=" * 80)
    print("対数整合・指数跳躍双対性システムによる偏見進化の観察")
    print("=" * 80)
    
    for round_num in range(1, rounds + 1):
        print(f"\n--- Round {round_num} ---")
        
        # 各エージェントの賭け決定
        bets = {}
        for agent in agents:
            bet_color, bet_amount = agent.decide_bet()
            bets[agent.personality.name] = (bet_color, bet_amount)
            if bet_color != "pass":
                print(f"{agent.personality.name}: {bet_color} に {bet_amount}円")
        
        # ルーレット回転
        result_color, result_number = play_log_roulette_round()
        print(f"結果: {result_color} {result_number}")
        
        # 結果処理
        for agent in agents:
            bet_color, bet_amount = bets[agent.personality.name]
            agent.process_outcome(bet_color, bet_amount, result_color, result_number)
            
            # 状態表示
            if len(agent.history['modes']) > 0:
                latest_mode = agent.history['modes'][-1]
                latest_leap_prob = agent.history['leap_probs'][-1]
                latest_energy = agent.history['energy_levels'][-1]
                print(f"  {agent.personality.name}: {agent.money}円 | Mode: {latest_mode} | "
                      f"LeapProb: {latest_leap_prob:.3f} | Energy: {latest_energy:.1f}")
        
        # 10ラウンドごとに詳細表示
        if round_num % 20 == 0:
            print(f"\n=== Round {round_num} 中間報告 ===")
            for agent in agents:
                profit = agent.money - agent.initial_money
                profit_rate = (profit / agent.initial_money) * 100
                
                # 最新の双対性状態
                recent_modes = agent.history['modes'][-10:] if len(agent.history['modes']) >= 10 else agent.history['modes']
                coherence_count = recent_modes.count("対数整合")
                leap_count = recent_modes.count("指数跳躍")
                
                print(f"{agent.personality.name}: {profit:+d}円 ({profit_rate:+.1f}%) | "
                      f"整合:{coherence_count} 跳躍:{leap_count} | "
                      f"κ平均: {np.mean(agent.state.kappa):.3f}")


def visualize_log_roulette_results(agents: List[LogRouletteAgent]):
    """Log版ルーレット結果可視化"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Log版エンジン ルーレット - 対数整合と指数跳躍の双対性', fontsize=16, fontweight='bold')
    
    # 1. 資産推移
    for agent in agents:
        rounds = list(range(len(agent.history['money'])))
        axes[0, 0].plot(rounds, agent.history['money'], label=agent.personality.name, linewidth=2)
    axes[0, 0].set_title('資産推移')
    axes[0, 0].set_xlabel('ラウンド')
    axes[0, 0].set_ylabel('資産額')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 双対モード分析
    for i, agent in enumerate(agents):
        mode_data = [1 if mode == "指数跳躍" else 0 for mode in agent.history['modes']]
        rounds = list(range(1, len(mode_data) + 1))
        
        # 移動平均で跳躍頻度を表示
        window = 10
        if len(mode_data) >= window:
            moving_avg = np.convolve(mode_data, np.ones(window)/window, mode='valid')
            axes[0, 1].plot(range(window, len(mode_data) + 1), moving_avg, 
                           label=f"{agent.personality.name} 跳躍率", linewidth=2)
    
    axes[0, 1].set_title('指数跳躍頻度（10ラウンド移動平均）')
    axes[0, 1].set_xlabel('ラウンド')
    axes[0, 1].set_ylabel('跳躍頻度')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. エネルギー状態推移
    for agent in agents:
        rounds = list(range(1, len(agent.history['energy_levels']) + 1))
        axes[1, 0].plot(rounds, agent.history['energy_levels'], 
                       label=agent.personality.name, linewidth=2, alpha=0.7)
    axes[1, 0].set_title('システムエネルギー推移')
    axes[1, 0].set_xlabel('ラウンド')
    axes[1, 0].set_ylabel('総エネルギー')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Log-Alignment係数推移
    for agent in agents:
        rounds = list(range(1, len(agent.history['alpha_t']) + 1))
        axes[1, 1].plot(rounds, agent.history['alpha_t'], 
                       label=agent.personality.name, linewidth=2, alpha=0.7)
    axes[1, 1].set_title('Log-Alignment係数 α_t')
    axes[1, 1].set_xlabel('ラウンド')
    axes[1, 1].set_ylabel('α_t')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def analyze_log_roulette_bias_evolution(agents: List[LogRouletteAgent]):
    """Log版偏見進化分析"""
    print("\n" + "=" * 80)
    print("Log版エンジン 偏見進化分析")
    print("=" * 80)
    
    for agent in agents:
        print(f"\n【{agent.personality.name}】({agent.personality.bias_interpretation}重視)")
        
        # 最終的な収支
        final_profit = agent.money - agent.initial_money
        profit_rate = (final_profit / agent.initial_money) * 100
        print(f"最終収支: {final_profit:+d}円 ({profit_rate:+.1f}%)")
        
        # 双対性統計
        total_rounds = len(agent.history['modes'])
        coherence_count = agent.history['modes'].count("対数整合")
        leap_count = agent.history['modes'].count("指数跳躍")
        coherence_rate = (coherence_count / total_rounds) * 100 if total_rounds > 0 else 0
        leap_rate = (leap_count / total_rounds) * 100 if total_rounds > 0 else 0
        
        print(f"対数整合モード: {coherence_count}回 ({coherence_rate:.1f}%)")
        print(f"指数跳躍モード: {leap_count}回 ({leap_rate:.1f}%)")
        
        # κ（整合慣性）の進化
        initial_kappa = np.ones(agent.personality.log_params.num_layers)
        final_kappa = agent.state.kappa
        kappa_change = final_kappa - initial_kappa
        
        print(f"κ進化:")
        layer_names = ["BASE", "CORE", "UPPER", "META"][:len(final_kappa)]
        for i, (name, change) in enumerate(zip(layer_names, kappa_change)):
            print(f"  {name}: {initial_kappa[i]:.3f} → {final_kappa[i]:.3f} ({change:+.3f})")
        
        # Log-Alignment適応
        if agent.history['alpha_t']:
            initial_alpha = agent.history['alpha_t'][0]
            final_alpha = agent.history['alpha_t'][-1]
            alpha_adaptation = final_alpha / initial_alpha
            print(f"Log-Alignment適応: α_t {initial_alpha:.4f} → {final_alpha:.4f} (x{alpha_adaptation:.2f})")
        
        # 跳躍の特徴
        if leap_count > 0:
            leap_rounds = [i for i, mode in enumerate(agent.history['modes']) if mode == "指数跳躍"]
            leap_energies = [agent.history['energy_levels'][i] for i in leap_rounds]
            avg_leap_energy = np.mean(leap_energies)
            print(f"跳躍時平均エネルギー: {avg_leap_energy:.1f}")
        
        print("-" * 40)


def main():
    """Log版ルーレットメイン実行"""
    print("Log版エンジン ルーレットゲーム")
    print("対数整合と指数跳躍による偏見進化システム")
    print("=" * 80)
    
    # 性格作成
    personalities = create_log_personalities()
    agents = [LogRouletteAgent(p) for p in personalities]
    
    # シミュレーション実行
    rounds = 150
    simulate_log_roulette_session(agents, rounds)
    
    # 結果分析
    analyze_log_roulette_bias_evolution(agents)
    
    # 可視化
    print("\n結果グラフを表示中...")
    visualize_log_roulette_results(agents)
    
    print("\n" + "=" * 80)
    print("Log版ルーレットシミュレーション完了")
    print("=" * 80)
    print("【理論的成果】")
    print("✅ 対数整合による小勝負の安定的処理")
    print("✅ 指数跳躍による大勝負での信念転換")
    print("✅ 性格別双対性パラメータの個性化")
    print("✅ Log-Alignmentによる感情の適応的制御")
    print("✅ 偏見進化過程の定量的観察")


if __name__ == "__main__":
    main()