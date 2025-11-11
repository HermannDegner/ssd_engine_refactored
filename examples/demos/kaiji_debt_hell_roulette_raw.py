"""
カイジ的借金地獄ルーレット - Log-Alignment無効化版
===============================================

Log-Alignmentを完全に無効化して、
生の圧力でLEAP発生を観察する実験版。
"""

import sys
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from enum import Enum

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.join(current_dir, "..", "..", "core")
extensions_path = os.path.join(current_dir, "..", "..", "extensions")
sys.path.insert(0, core_path)
sys.path.insert(0, extensions_path)

# SSD Log版エンジンをインポート
from ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, create_default_state
from ssd_human_module import HumanAgent, HumanParams


# カイジ用のRaw（Log-Alignment無効）パラメータ
def create_kaiji_raw_params():
    """Log-Alignment無効化でLEAP発生しやすいパラメータ"""
    params = SSDCoreParams()
    
    # Log-Alignmentを完全無効化
    params.log_align = False
    
    # Theta閾値を適度に設定
    params.Theta_values = [50.0, 30.0, 20.0, 10.0]  
    
    # Dynamic Theta感度を上げる
    params.theta_sensitivity = 0.8
    
    # エネルギー生成を増加
    params.gamma_values = [0.30, 0.25, 0.20, 0.15]  # 2倍増
    
    # エネルギー減衰を半減
    params.beta_values = [0.0005, 0.005, 0.025, 0.05]
    
    # 確率的LEAP有効化
    params.enable_stochastic_leap = True
    params.temperature_T = 2.0
    
    return params


class RouletteColor(Enum):
    RED = "red"
    BLACK = "black"


@dataclass
class KaijiRawPlayer:
    """カイジ的プレイヤー（Log-Alignment無効版）"""
    name: str
    personality: str
    debt: int = 500  # 初期借金500コイン
    hope: float = 1.0  # 希望度
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    total_rounds: int = 0
    
    # SSD関連
    agent: HumanAgent = None
    energy_history: list = None
    pressure_history: list = None
    leap_count: int = 0
    
    def __post_init__(self):
        self.energy_history = []
        self.pressure_history = []
    
    @property
    def despair_level(self) -> float:
        """絶望レベル計算 (0-10)"""
        base_despair = min(self.debt / 200.0, 10.0)
        hope_modifier = max(0.1, 1.0 / max(0.1, self.hope))
        return min(base_despair * hope_modifier, 10.0)
    
    def get_bet_amount(self) -> int:
        """賭け金計算（借金の10%基準、絶望に応じて変動）"""
        base_bet = max(10, int(self.debt * 0.1))
        despair_multiplier = 1.0 + (self.despair_level / 10.0) * 0.5
        return int(base_bet * despair_multiplier)
    
    def choose_color(self) -> RouletteColor:
        """色選択（性格と絶望に基づく）"""
        if self.personality == "cautious":
            # 慎重派: 赤をやや好む
            return RouletteColor.RED if random.random() < 0.6 else RouletteColor.BLACK
        elif self.personality == "aggressive":
            # 攻撃的: 黒を好む（高リスク高リターン的心理）
            return RouletteColor.BLACK if random.random() < 0.6 else RouletteColor.RED
        else:  # balanced
            # バランス派: 五分五分
            return RouletteColor.RED if random.random() < 0.5 else RouletteColor.BLACK
    
    def update_psychology(self, won: bool, amount: int):
        """心理状態更新"""
        if won:
            self.debt = max(0, self.debt - amount)
            self.hope = min(5.0, self.hope * 1.2)
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.debt += amount
            self.hope = max(0.1, self.hope * 0.8)
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        self.total_rounds += 1
    
    def get_status_emoji(self) -> str:
        """状況に応じた絵文字"""
        despair = self.despair_level
        if despair < 2.0:
            return "😊"
        elif despair < 4.0:
            return "😰"
        elif despair < 6.0:
            return "😱"
        elif despair < 8.0:
            return "💀"
        else:
            return "🔥"
    
    def get_status_message(self) -> str:
        """状況メッセージ"""
        despair = self.despair_level
        if despair < 2.0:
            return "まだ余裕がある"
        elif despair < 4.0:
            return "なんとか巻き返したい..."
        elif despair < 6.0:
            return "もう後がない..."
        elif despair < 8.0:
            return "地獄の淵に立っている..."
        else:
            return "完全に絶望の底..."


def create_roulette_result():
    """ルーレット結果生成（0-36、0は緑）"""
    number = random.randint(0, 36)
    if number == 0:
        return number, "GREEN"
    elif number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
        return number, "RED"
    else:
        return number, "BLACK"


def inject_despair_pressure(player: KaijiRawPlayer) -> float:
    """絶望に基づく心理圧力注入（Log-Alignment無効なので直接的）"""
    despair = player.despair_level
    base_pressure = despair * 20.0  # 絶望1レベルあたり20の圧力
    
    # 連敗による圧力増加
    loss_pressure = player.consecutive_losses * 15.0
    
    # 借金による圧力
    debt_pressure = min(player.debt / 10.0, 100.0)
    
    total_pressure = base_pressure + loss_pressure + debt_pressure
    
    # Raw版なので圧力をそのまま返す
    return total_pressure


def run_kaiji_raw_experiment():
    """カイジ借金地獄実験（Log-Alignment無効版）"""
    print("=" * 80)
    print("💀 カイジ的借金地獄ルーレット - Raw版（Log-Alignment無効） 💀")
    print("=" * 80)
    print("【地獄の始まり - Log-Alignment完全無効化】")
    print("・Log-Alignmentを完全無効化")
    print("・生の圧力でLEAP発生観察")
    print("・Theta閾値を現実的レベルに設定")
    print("・極限心理下でのLEAP発生確認")
    print()
    
    # パラメータ設定
    engine_params = create_kaiji_raw_params()
    human_params = HumanParams()
    
    # プレイヤー作成
    players = [
        KaijiRawPlayer("カイジ", "balanced"),
        KaijiRawPlayer("遠藤", "cautious"),
        KaijiRawPlayer("佐原", "aggressive"),
    ]
    
    # エージェント初期化
    for player in players:
        player.agent = HumanAgent(human_params)
        state = create_default_state(engine_params.num_layers)
        player.agent.engine = SSDCoreEngine(engine_params)
        player.agent.engine.current_state = state
        print(f"💀 {player.name}({player.personality})が地獄に参加 - 借金: {player.debt}コイン (絶望レベル{player.despair_level:.1f})")
    
    print()
    
    # 25ラウンドの地獄
    total_leaps = 0
    
    for round_num in range(1, 26):
        print("💀" * 20 + f" 地獄Round {round_num} " + "💀" * 20)
        
        # 各プレイヤーの行動
        round_results = []
        for player in players:
            status = player.get_status_emoji()
            message = player.get_status_message()
            bet_amount = player.get_bet_amount()
            chosen_color = player.choose_color()
            
            print(f"{player.name}: {status} {message}")
            print(f"  💀 現在: {player.debt}コインの借金")
            print(f"  😱 絶望レベル: {player.despair_level:.1f}/10.0, 希望: {player.hope:.1f}")
            print(f"  🎰 {chosen_color.value}に{bet_amount}コイン")
            
            # 心理圧力注入（Raw版 - Log-Alignment無効）
            pressure = inject_despair_pressure(player)
            print(f"  ⚠️  💸 Raw Pressure: {pressure:.1f}")
            
            # SSDエンジンで圧力処理
            old_energy = player.agent.engine.current_state.E[0]
            
            # 圧力をベクトルとして設定（第1レイヤーに注入）
            pressure_vector = np.zeros(engine_params.num_layers)
            pressure_vector[0] = pressure
            
            # ステップ実行
            new_state = player.agent.engine.step(player.agent.engine.current_state, pressure_vector)
            player.agent.engine.current_state = new_state
            
            new_energy = new_state.E[0]
            
            # LEAP判定（手動）
            leap_occurred = False
            for i, (energy, theta) in enumerate(zip(new_state.E, engine_params.Theta_values)):
                if energy >= theta:
                    leap_occurred = True
                    player.leap_count += 1
                    total_leaps += 1
                    print(f"  🚀 LEAP発生! レイヤー{i+1}でE={energy:.2f} >= Theta={theta} (累計{player.leap_count}回)")
                    # LEAPによるエネルギーリセット
                    new_state.E[i] = 0.0
                    break
            
            # エネルギー履歴記録
            player.energy_history.append(new_energy)
            player.pressure_history.append(pressure)
            
            round_results.append((player, bet_amount, chosen_color, pressure))
        
        print()
        
        # ルーレット回転
        number, color = create_roulette_result()
        
        if number == 0:
            print(f"🎰💚 ルーレット結果: {number} 💚 GREEN - 全員敗北...")
            winner_color = None
        else:
            color_emoji = "❤️" if color == "RED" else "🖤"
            special_emoji = "🔥" if number in [7, 13] else ""
            print(f"🎰{special_emoji} ルーレット結果: {number} {color_emoji} {color}{(' - 悪魔の数字...' if special_emoji else '')}")
            winner_color = color
        
        # 勝敗処理
        round_winners = 0
        round_losers = 0
        
        for player, bet_amount, chosen_color, pressure in round_results:
            if winner_color is None:  # Green (0)
                won = False
            else:
                won = chosen_color.value.upper() == winner_color
            
            if won:
                print(f"  🎉 勝利！ +{bet_amount}コイン")
                print(f"  💰 借金: {player.debt}→{max(0, player.debt - bet_amount)}")
                print(f"  😱 絶望: {player.despair_level:.1f}→{max(0.1, (max(0, player.debt - bet_amount) / 200.0) * max(0.1, 1.0 / max(0.1, min(5.0, player.hope * 1.2)))):.1f} (希望の光が見えた)")
                round_winners += 1
                
                player.update_psychology(True, bet_amount)
                
                if player.consecutive_wins >= 2:
                    print(f"  ✨ 奇跡の{player.consecutive_wins}連勝！")
                    
            else:
                print(f"  💀 敗北... -{bet_amount}コイン")
                print(f"  💰 借金: {player.debt - bet_amount}→{player.debt + bet_amount}")
                print(f"  😱 絶望: {player.despair_level:.1f}→{min(10.0, ((player.debt + bet_amount) / 200.0) * max(0.1, 1.0 / max(0.1, max(0.1, player.hope * 0.8)))):.1f} (借金が雪だるま式に...)")
                round_losers += 1
                
                player.update_psychology(False, bet_amount)
                
                if player.consecutive_losses >= 3:
                    print(f"  🔥 地獄の{player.consecutive_losses}連敗...")
        
        # ラウンド総括
        if round_winners == 3:
            print("  ✨ 奇跡の全員勝利！")
        elif round_losers == 3:
            print("  🔥 地獄の3連敗...")
        
        print()
        
        # 10ラウンド毎に中間報告
        if round_num % 10 == 0:
            print(f"💀 地獄{round_num}ラウンド後の状況:")
            for player in players:
                print(f"  {player.name}: {player.debt}コインの借金 (絶望: {player.despair_level:.1f}, LEAP: {player.leap_count}回)")
            print()
    
    # 最終結果
    print("💀" * 58)
    print("💀" * 22 + "                                                                         ⚰️  Raw版実験 - 最終審判")
    print("💀" * 58)
    print("💀" * 22 + "                                                                         ")
    
    for player in players:
        initial_debt = 500
        debt_change = initial_debt - player.debt if player.debt < initial_debt else -(player.debt - initial_debt)
        win_rate = (player.total_rounds - sum(1 for i in range(len(player.energy_history)) if i < len(round_results) and not round_results[i])) / player.total_rounds * 100 if player.total_rounds > 0 else 0
        
        print(f"💀 {player.name} ({player.personality})")
        print(f"  💰 借金変化: {initial_debt}→{player.debt}")
        print(f"  😱 最終絶望レベル: {player.despair_level:.1f}/10.0")
        if player.leap_count > 0:
            print(f"  ⚡ LEAP発生: {player.leap_count}回 🚀🚀🚀")
        else:
            print(f"  ⚡ LEAP発生: {player.leap_count}回 🔥🔥🔥")
        print(f"  🎯 勝率: 計算中")
        print()
    
    print(f"🎯 全体LEAP発生総数: {total_leaps}回")
    
    if total_leaps > 0:
        print("🚀 Raw版でLEAP発生確認！Log-Alignmentが主要阻害因子だった！")
    else:
        print("😱 Raw版でもLEAP未発生...さらなる調査が必要")


if __name__ == "__main__":
    run_kaiji_raw_experiment()