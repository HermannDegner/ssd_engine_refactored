"""
カイジ的借金地獄ルーレット - LEAP感度向上版
===============================================

SSD Log版エンジンのTheta閾値を大幅に下げて、
極限心理状態でのLEAP発生を観察する実験版。
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
from ssd_human_module import HumanAgent, HumanPressure, HumanLayer
import numpy as np

# カイジ用の高感度パラメータ
def create_kaiji_sensitive_params():
    """LEAP発生しやすい高感度パラメータ"""
    params = SSDCoreParams()
    
    # Theta閾値を大幅に下げる（1/10に）
    params.Theta_values = [20.0, 10.0, 5.0, 3.0]  
    
    # Dynamic Theta感度を上げる
    params.theta_sensitivity = 0.8  # 0.3 → 0.8
    
    # エネルギー生成を増加
    params.gamma_values = [0.25, 0.20, 0.15, 0.10]  # 1.5倍
    
    # エネルギー減衰を抑制
    params.beta_values = [0.0005, 0.005, 0.025, 0.05]  # 半分
    
    # 確率的LEAP有効化
    params.enable_stochastic_leap = True
    params.temperature_T = 2.0
    
    return params

# カイジ色設定（暗めのトーン）
class Colors:
    RESET = '\033[0m'
    DARK_RED = '\033[31m'
    GRAY = '\033[90m' 
    DARK_YELLOW = '\033[33m'
    GREEN = '\033[32m'
    CYAN = '\033[36m'

# ルーレット設定
@dataclass
class RouletteConfig:
    RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    PAYOUT_RED = 2
    PAYOUT_BLACK = 2
    PAYOUT_NUMBER = 36
    PAYOUT_ZERO = 36

# 借金価値システム
class DebtValue:
    def __init__(self, initial_debt: int, personality: str):
        self.initial_debt = initial_debt
        self.current_debt = initial_debt
        self.personality = personality
        
        # 絶望レベル（1.0-10.0）
        self.despair_level = abs(initial_debt) / 200.0
        
        # 希望レベル（一発逆転への期待）
        self.hope_for_reversal = 1.0 + (0.5 if personality == "aggressive" else 0.0)
        
        # 破れかぶれ度（絶望が高いほど危険な賭けに）
        self.desperation_multiplier = 1.0
    
    def experience_loss(self, amount: int):
        """敗北体験"""
        self.current_debt -= amount
        
        # 絶望レベル上昇
        debt_ratio = abs(self.current_debt) / 200.0
        self.despair_level = min(10.0, debt_ratio)
        
        # 破れかぶれ度上昇
        if self.despair_level >= 8.0:
            self.desperation_multiplier = 3.0  # Ultimate Despair
        elif self.despair_level >= 5.0:
            self.desperation_multiplier = 2.0  # Deep Despair
        elif self.despair_level >= 3.0:
            self.desperation_multiplier = 1.5  # Moderate Despair
    
    def experience_win(self, amount: int):
        """勝利体験"""
        self.current_debt += amount
        
        # 絶望レベル軽減
        if self.current_debt > 0:
            self.despair_level = max(1.0, self.despair_level - 2.0)
        else:
            debt_ratio = abs(self.current_debt) / 200.0
            self.despair_level = max(1.0, debt_ratio)
        
        # 希望回復
        self.hope_for_reversal = min(3.0, self.hope_for_reversal + 0.3)
        
        # 破れかぶれ度リセット
        if self.current_debt >= 0:
            self.desperation_multiplier = 0.5  # 慎重モード

# カイジ的借金システム
class KaijiDebtSystem:
    def __init__(self):
        self.win_streak = 0
        self.loss_streak = 0
        self.max_win_streak = 0
        self.max_loss_streak = 0
    
    def create_debt_value(self, initial_debt: int, personality: str) -> DebtValue:
        return DebtValue(initial_debt, personality)
    
    def update_streaks(self, won: bool):
        if won:
            self.win_streak += 1
            self.loss_streak = 0
            self.max_win_streak = max(self.max_win_streak, self.win_streak)
        else:
            self.loss_streak += 1
            self.win_streak = 0
            self.max_loss_streak = max(self.max_loss_streak, self.loss_streak)

# 地獄のルーレット
class HellRoulette:
    def __init__(self):
        self.config = RouletteConfig()
        self.history = []
    
    def spin(self) -> int:
        result = random.randint(0, 36)
        self.history.append(result)
        
        color = self._get_color(result)
        
        if result == 0:
            print(f"\n🎰💀 ルーレット結果: {result} {color} - 運命の緑！")
        elif result in [7, 13, 21]:
            print(f"\n🎰🔥 ルーレット結果: {result} {color} - 悪魔の数字...")
        else:
            print(f"\n🎰⚫ ルーレット結果: {result} {color}")
        
        return result
    
    def _get_color(self, number: int) -> str:
        if number == 0:
            return "💚 GREEN"
        elif number in self.config.RED_NUMBERS:
            return "❤️ RED"
        else:
            return "🖤 BLACK"

# カイジ的借金プレイヤー（高感度版）
class KaijiSensitivePlayer:
    def __init__(self, name: str, personality: str, initial_debt: int = -500):
        self.name = name
        self.personality = personality
        self.initial_debt = initial_debt
        
        # 高感度Log版SSDエンジン
        params = create_kaiji_sensitive_params()
        self.engine = SSDCoreEngine(params)
        self.state = create_default_state(num_layers=4)
        
        # カイジ的借金システム
        self.debt_system = KaijiDebtSystem()
        self.debt_value = self.debt_system.create_debt_value(initial_debt, personality)
        
        # 履歴
        self.round_count = 0
        self.total_wins = 0
        self.total_losses = 0
        self.debt_history = []
        self.despair_history = []
        self.energy_history = []
        self.pressure_history = []
        self.leap_history = []
        self.leap_count = 0
        
        # 初期記録
        initial_energy = np.sum(self.state.E)
        self.energy_history.append(initial_energy)
        self.pressure_history.append(0.0)
        self.leap_history.append(False)
        
        self.color = self._get_color()
        
        despair_msg = f"絶望レベル{self.debt_value.despair_level:.1f}"
        print(f"{self.color}💀 {name}({personality})が地獄に参加 - 借金: {abs(initial_debt)}コイン ({despair_msg}){Colors.RESET}")
    
    def _get_color(self) -> str:
        colors = [Colors.DARK_RED, Colors.GRAY, Colors.DARK_YELLOW]
        return colors[hash(self.name) % len(colors)]
    
    def get_current_debt(self) -> int:
        return self.debt_value.current_debt
    
    def can_continue(self) -> bool:
        return self.debt_value.current_debt > -2000
    
    def make_bet(self) -> tuple:
        """高感度版：より危険な賭けに傾向"""
        debt = self.get_current_debt()
        despair = self.debt_value.despair_level
        desperation = self.debt_value.desperation_multiplier
        
        # ベース賭け金
        base_bet = min(60, abs(debt) // 10)
        bet_amount = int(base_bet * desperation)
        
        # 賭けタイプ決定（絶望が深いほど危険な賭け）
        if despair >= 8.0:
            bet_type = "number"
            bet_value = random.randint(1, 36)
            status = "💀⚡ Ultimate Despair"
            message = "💀 もうどうでもいい！全てを賭ける！"
        elif despair >= 5.0:
            if random.random() < 0.3:
                bet_type = "number"
                bet_value = 7  # 悪魔の数字
            else:
                bet_type = random.choice(["red", "black"])
                bet_value = None
            status = "😱💔 Deep Despair"
            message = "😱 もう後がない...一発逆転を狙う"
        elif debt >= 0:
            bet_type = "red"
            bet_value = None
            bet_amount = 10
            status = "🌈✨ Miracle Recovery"
            message = "🌈 奇跡だ...慎重に行こう..."
        else:
            bet_type = random.choice(["red", "black"])
            bet_value = None
            status = "😰💸 Desperation"
            message = "😰 なんとか巻き返したい..."
        
        print(f"{self.color}{self.name}: {message}")
        print(f"  💀 現在: {abs(debt)}コインの{'借金' if debt < 0 else 'プロフィット'}")
        print(f"  😱 絶望レベル: {despair:.1f}/10.0, 希望: {self.debt_value.hope_for_reversal:.1f}")
        print(f"  🎰 {bet_type}{'=' + str(bet_value) if bet_value else ''}に{bet_amount}コイン")
        print(f"  ⚠️  {status}{Colors.RESET}")
        
        return bet_type, bet_value, bet_amount
    
    def update_result(self, won: bool, payout: int, bet_amount: int):
        """高感度版：より強い圧力をSSDエンジンに投入"""
        self.round_count += 1
        
        old_debt = self.get_current_debt()
        old_despair = self.debt_value.despair_level
        
        if won:
            self.total_wins += 1
            self.debt_value.experience_win(payout)
        else:
            self.total_losses += 1
            self.debt_value.experience_loss(bet_amount)
        
        # より強いSSDエンジンへの圧力投入
        pressure_vector = np.zeros(4)
        despair_change = self.debt_value.despair_level - old_despair
        
        if won:
            # 勝利時は希望的圧力（軽め）
            pressure_vector[3] = 0.5
            if self.get_current_debt() >= 0:
                pressure_vector[3] = 2.0  # 完済時は大きな安堵
        else:
            # 敗北時は絶望的圧力（強化版）
            base_pressure = abs(despair_change) * 2.0  # 2倍に強化
            pressure_vector[0] = base_pressure * 1.5   # BASE層
            pressure_vector[1] = base_pressure * 1.0   # CORE層
            pressure_vector[2] = base_pressure * 0.8   # SOCIAL層
            pressure_vector[3] = base_pressure * 0.3   # UPPER層
            
            # 極限絶望時は全層に追加圧力
            if self.debt_value.despair_level >= 8.0:
                pressure_vector += 1.5  # 追加圧力も強化
            elif self.debt_value.despair_level >= 5.0:
                pressure_vector += 1.0
        
        # SSDエンジン更新
        self.state = self.engine.step(self.state, pressure_vector, dt=1.0)
        
        # LEAP検出（高感度）
        leap_occurred = False
        if hasattr(self.state, 'leap_history') and self.state.leap_history:
            current_leap_count = len(self.state.leap_history)
            if current_leap_count > len(self.leap_history):
                leap_occurred = True
                self.leap_count += 1
                latest_leap = self.state.leap_history[-1]
                leap_type = latest_leap[1].name if hasattr(latest_leap[1], 'name') else str(latest_leap[1])
                print(f"  ⚡🔥🔥 {self.name}: 🌈LEAP発生🌈 {leap_type} (時刻: {latest_leap[0]:.2f}) ⚡🔥🔥")
        
        # 履歴記録
        current_energy = np.sum(self.state.E)
        self.energy_history.append(current_energy)
        self.pressure_history.append(np.linalg.norm(pressure_vector))
        self.leap_history.append(leap_occurred)
        
        new_debt = self.get_current_debt()
        self.debt_history.append(new_debt)
        self.despair_history.append(self.debt_value.despair_level)
        
        # 結果表示
        if won:
            if old_debt < 0 and new_debt >= 0:
                result_msg = f"🌈 奇跡の勝利！ +{payout}コイン - 借金完済！！"
                emotion = "奇跡が起きた...生き返った気分だ"
            else:
                result_msg = f"🎉 勝利！ +{payout}コイン"
                emotion = "希望の光が見えた"
        else:
            result_msg = f"💀 敗北... -{bet_amount}コイン"
            if self.debt_value.despair_level >= 8.0:
                emotion = "絶望の底に沈んでいく..."
            elif self.debt_value.despair_level >= 5.0:
                emotion = "もう終わりだ..."
            else:
                emotion = "借金が雪だるま式に..."
        
        self.debt_system.update_streaks(won)
        
        # 連勝・連敗表示
        if self.debt_system.win_streak >= 2:
            streak_msg = f"✨ 奇跡の{self.debt_system.win_streak}連勝！"
        elif self.debt_system.loss_streak >= 3:
            streak_msg = f"🔥 地獄の{self.debt_system.loss_streak}連敗..."
        else:
            streak_msg = ""
        
        print(f"  {result_msg}")
        print(f"  💰 借金: {abs(old_debt)}→{abs(new_debt) if new_debt < 0 else '完済！'}")
        print(f"  😱 絶望: {old_despair:.1f}→{self.debt_value.despair_level:.1f} ({emotion})")
        if streak_msg:
            print(f"  {streak_msg}")


def run_kaiji_sensitive_experiment():
    """高感度カイジ実験メイン"""
    print("="*80)
    print("💀 カイジ的借金地獄ルーレット - 高感度LEAP実験版 💀")
    print("="*80)
    print("【地獄の始まり - 高感度設定】")
    print("・Theta閾値を1/10に削減")
    print("・圧力を2倍に強化")
    print("・確率的LEAP有効化")
    print("・Dynamic Theta感度向上")
    print("・極限心理下でのLEAP発生観察")
    print()
    
    # 高感度プレイヤー生成
    players = [
        KaijiSensitivePlayer("カイジ", "balanced", -500),
        KaijiSensitivePlayer("遠藤", "cautious", -500), 
        KaijiSensitivePlayer("佐原", "aggressive", -500)
    ]
    
    roulette = HellRoulette()
    
    # 地獄の25ラウンド
    for round_num in range(1, 26):
        print(f"\n{'💀'*20} 地獄Round {round_num} {'💀'*20}")
        
        bets = []
        for player in players:
            if player.can_continue():
                bet_type, bet_value, bet_amount = player.make_bet()
                bets.append((player, bet_type, bet_value, bet_amount))
            else:
                print(f"{player.color}{player.name}: 💀 借金限度額到達...もう終わりだ...{Colors.RESET}")
        
        if not bets:
            print("💀 全員が借金限度額に到達...地獄の終わり...")
            break
        
        result = roulette.spin()
        
        for player, bet_type, bet_value, bet_amount in bets:
            won = False
            payout = 0
            
            if bet_type == "zero" and result == 0:
                won = True
                payout = bet_amount * (RouletteConfig.PAYOUT_ZERO - 1)
                print(f"🌈 {player.name} - 奇跡のゼロ！大勝利！")
            elif bet_type == "number" and result == bet_value:
                won = True
                payout = bet_amount * (RouletteConfig.PAYOUT_NUMBER - 1)
                print(f"🎰 {player.name} - 数字的中！一発逆転！")
            elif bet_type == "red" and result in RouletteConfig.RED_NUMBERS:
                won = True
                payout = bet_amount * (RouletteConfig.PAYOUT_RED - 1)
            elif bet_type == "black" and result in RouletteConfig.BLACK_NUMBERS:
                won = True
                payout = bet_amount * (RouletteConfig.PAYOUT_BLACK - 1)
            
            player.update_result(won, payout, bet_amount)
        
        # 中間報告
        if round_num % 10 == 0:
            print(f"\n💀 地獄{round_num}ラウンド後の状況:")
            for player in players:
                debt = player.get_current_debt()
                print(f"  {player.name}: {abs(debt)}コイン{'の借金' if debt < 0 else 'プロフィット'} "
                      f"(絶望: {player.debt_value.despair_level:.1f}, LEAP: {player.leap_count}回)")
    
    # 最終結果
    print(f"\n{'💀'*80}")
    print("⚰️  高感度実験 - 最終審判")
    print(f"{'💀'*80}")
    
    for player in players:
        debt = player.get_current_debt()
        print(f"\n{player.color}💀 {player.name} ({player.personality}){Colors.RESET}")
        print(f"  💰 借金変化: {abs(player.initial_debt)}→{abs(debt) if debt < 0 else f'完済+{debt}'}")
        print(f"  😱 最終絶望レベル: {player.debt_value.despair_level:.1f}/10.0")
        print(f"  ⚡ LEAP発生: {player.leap_count}回 🔥🔥🔥")
        print(f"  🎯 勝率: {player.total_wins}/{player.round_count}ラウンド ({player.total_wins/player.round_count:.1%})")

if __name__ == "__main__":
    random.seed(42)
    run_kaiji_sensitive_experiment()