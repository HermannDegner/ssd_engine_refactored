"""
カイジ的借金地獄ルーレット with SSD Log版エンジン
「絶望からの一発逆転：全員借金スタートの地獄ルーレット」

【カイジ世界観】
1. 全員借金からスタート（-500コイン）
2. 借金地獄の心理的圧迫感
3. 一発逆転への渇望と絶望
4. 破れかぶれの大胆な賭け

【心理状態の変遷】
- 初期絶望: 借金の重圧で冷静な判断力を失う
- 破れかぶれ: 大きな賭けに出る心理
- 一発逆転夢: 高配当への執着
- 更なる絶望: 負けが続くとさらに追い込まれる

【SSD統合】
- 借金圧力をHumanPressureとして投入
- 絶望状態でのLog版エンジンの制御力テスト
- 極限状態でのκ（整合慣性）の変化観察

【理論的意義】
- 極限状況での人間心理のモデル化
- 債務者心理学の実証的研究
- ギャンブル依存症メカニズムの解明

元コード: roulette_subjective_money_value.py → カイジ的借金地獄版
"""

import sys
import os
import random
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
from collections import deque

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
examples_dir = os.path.dirname(current_dir)
repo_dir = os.path.dirname(examples_dir)
core_path = os.path.join(repo_dir, 'core')
sys.path.insert(0, core_path)

# SSD Log版エンジンをインポート
from ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, create_default_state
from ssd_human_module import HumanAgent, HumanPressure, HumanLayer
import numpy as np

# ANSIカラーコード
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DARK_RED = '\033[31m'
    DARK_YELLOW = '\033[33m'
    GRAY = '\033[90m'

# ===== カイジ的借金価値システム =====
@dataclass
class DebtValue:
    """借金の主観的価値（カイジ的絶望モデル）"""
    debt_amount: int  # 借金額（負の値）
    despair_level: float  # 絶望レベル（1.0〜10.0）
    desperation_coefficient: float  # 破れかぶれ係数
    hope_for_reversal: float  # 一発逆転への希望
    
    def get_subjective_debt_weight(self) -> float:
        """主観的借金の重み"""
        return abs(self.debt_amount) * self.despair_level
    
    def experience_loss(self, loss_amount: int):
        """さらなる損失による絶望の深化"""
        # 借金が増えるほど絶望も深まる
        despair_increase = (loss_amount / 100.0) * self.desperation_coefficient
        self.despair_level = min(10.0, self.despair_level + despair_increase)
        
        # 絶望が深まると一発逆転への希望も歪む
        if self.despair_level > 7.0:
            self.hope_for_reversal = min(5.0, self.hope_for_reversal + 0.3)
        
        # 借金額更新
        self.debt_amount -= loss_amount
    
    def experience_win(self, win_amount: int):
        """勝利による一時的な希望"""
        # 借金減少
        self.debt_amount += win_amount
        
        if self.debt_amount >= 0:
            # 借金完済！奇跡の復活
            self.despair_level = max(1.0, self.despair_level * 0.3)
            self.hope_for_reversal = 1.0
        else:
            # まだ借金中だが少し希望が
            self.despair_level = max(1.0, self.despair_level * 0.9)
            self.hope_for_reversal = max(1.0, self.hope_for_reversal * 0.8)

class KaijiDebtSystem:
    """カイジ的借金地獄管理システム"""
    
    def __init__(self):
        self.despair_history = deque(maxlen=100)
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        self.total_debt_increase = 0  # 借金増加総額
        self.miracle_recoveries = 0   # 奇跡的回復回数
        
    def create_debt_value(self, initial_debt: int, personality: str) -> DebtValue:
        """性格に応じた借金価値を生成"""
        if personality == 'cautious':
            # 慎重派: 高い絶望感、低い破れかぶれ度
            return DebtValue(
                debt_amount=initial_debt,
                despair_level=3.0,  # 高めの初期絶望
                desperation_coefficient=0.4,
                hope_for_reversal=1.2
            )
        elif personality == 'aggressive':
            # 攻撃派: 中程度の絶望感、高い破れかぶれ度
            return DebtValue(
                debt_amount=initial_debt,
                despair_level=2.0,  # 低めの初期絶望
                desperation_coefficient=0.6,
                hope_for_reversal=1.8
            )
        else:  # balanced
            # バランス派: 中程度だが不安定
            return DebtValue(
                debt_amount=initial_debt,
                despair_level=2.5,
                desperation_coefficient=0.5,
                hope_for_reversal=1.5
            )
    
    def update_streaks(self, won: bool):
        """連勝・連敗の更新"""
        if won:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.total_debt_increase += 1
    
    def get_psychological_state(self, debt_amount: int, despair_level: float) -> str:
        """心理状態の判定"""
        if debt_amount >= 0:
            return "miracle_recovery"  # 奇跡の回復
        elif debt_amount > -200:
            if despair_level < 3.0:
                return "cautious_hope"  # 慎重な希望
            else:
                return "desperate_hope"  # 絶望的希望
        elif debt_amount > -800:
            if despair_level < 5.0:
                return "deep_despair"  # 深い絶望
            else:
                return "suicidal_despair"  # 自滅的絶望
        else:
            return "ultimate_despair"  # 究極の絶望

# ===== ルーレット設定 =====
class RouletteConfig:
    """ルーレット設定（ヨーロピアン）"""
    MAX_NUMBER = 36
    RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    # カイジ的高配当設定
    PAYOUT_ZERO = 36   # 35:1 + 元金
    PAYOUT_NUMBER = 36 # 35:1 + 元金
    PAYOUT_RED = 2     # 1:1 + 元金
    PAYOUT_BLACK = 2   # 1:1 + 元金

class KaijiRoulette:
    """カイジ的地獄ルーレット"""
    
    def __init__(self):
        self.config = RouletteConfig()
        self.spin_count = 0
        self.total_despair_generated = 0.0
    
    def spin(self) -> int:
        """ルーレットを回す（カイジ的演出付き）"""
        result = random.randint(0, self.config.MAX_NUMBER)
        self.spin_count += 1
        
        color = self._get_color(result)
        
        # カイジ的演出
        if result == 0:
            print(f"\n🎰💀 ルーレット結果: {result} {color} - 運命の緑！")
        elif result in [7, 13, 21]:  # 特別な数字
            print(f"\n🎰🔥 ルーレット結果: {result} {color} - 悪魔の数字...")
        else:
            print(f"\n🎰⚫ ルーレット結果: {result} {color}")
        
        return result
    
    def _get_color(self, number: int) -> str:
        """数字の色を取得"""
        if number == 0:
            return "💚 GREEN"
        elif number in self.config.RED_NUMBERS:
            return "❤️ RED"
        else:
            return "🖤 BLACK"

# ===== カイジ的借金プレイヤー =====
class KaijiDebtPlayer:
    """カイジ的借金地獄プレイヤー"""
    
    def __init__(self, name: str, personality: str, initial_debt: int = -500):
        self.name = name
        self.personality = personality
        self.initial_debt = initial_debt
        
        # Log版SSDエンジン
        params = SSDCoreParams()
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
        self.energy_history = []  # SSDエンジンエネルギー履歴
        self.pressure_history = []  # 投入圧力履歴
        self.leap_history = []  # leap発生履歴
        self.leap_count = 0  # 総leap回数
        
        # 色分け（暗めのトーン）
        self.color = self._get_color()
        
        # 初期エネルギー記録
        initial_energy = np.sum(self.state.E)
        self.energy_history.append(initial_energy)
        self.pressure_history.append(0.0)  # 初期圧力は0
        self.leap_history.append(False)  # 初期はleap無し
        
        despair_msg = f"絶望レベル{self.debt_value.despair_level:.1f}"
        print(f"{self.color}💀 {name}({personality})が地獄に参加 - 借金: {abs(initial_debt)}コイン ({despair_msg}){Colors.RESET}")
    
    def _get_color(self) -> str:
        """プレイヤー色（暗いトーン）"""
        colors = [Colors.DARK_RED, Colors.GRAY, Colors.DARK_YELLOW]
        return colors[hash(self.name) % len(colors)]
    
    def get_current_debt(self) -> int:
        """現在の借金額"""
        return self.debt_value.debt_amount
    
    def get_debt_status(self) -> str:
        """借金状態の表示"""
        amount = self.get_current_debt()
        if amount >= 0:
            return f"奇跡の{amount}コイン"
        else:
            return f"{abs(amount)}コインの借金"
    
    def place_bet(self) -> Tuple[str, Optional[int], int]:
        """ベット決定（絶望に基づく）"""
        self.round_count += 1
        
        # 心理状態分析
        debt_amount = self.get_current_debt()
        despair_level = self.debt_value.despair_level
        hope_level = self.debt_value.hope_for_reversal
        psych_state = self.debt_system.get_psychological_state(debt_amount, despair_level)
        
        base_bet = 20  # カイジ的に高めのベット
        
        # 心理状態に基づく賭けパターン
        if psych_state == "miracle_recovery":
            # 奇跡の回復！慎重になる
            bet_multiplier = 0.5
            comment = "🌈 奇跡だ...慎重に行こう..."
            bet_preference = "safe"
        elif psych_state == "ultimate_despair":
            # 究極の絶望：完全に破れかぶれ
            bet_multiplier = 3.0
            comment = "💀 もうどうでもいい！全てを賭ける！"
            bet_preference = "desperate"
        elif psych_state == "suicidal_despair":
            # 自滅的絶望：大きく賭ける
            bet_multiplier = 2.5
            comment = "🔥 地獄の底まで落ちてやる！"
            bet_preference = "aggressive"
        elif psych_state == "deep_despair":
            # 深い絶望：やや攻撃的
            bet_multiplier = 1.8
            comment = "😱 もう後がない...一発逆転を狙う"
            bet_preference = "risky"
        elif psych_state == "desperate_hope":
            # 絶望的希望：中程度の賭け
            bet_multiplier = 1.3
            comment = "😰 まだ希望はある...はず"
            bet_preference = "moderate"
        else:  # cautious_hope
            # 慎重な希望：控えめ
            bet_multiplier = 0.8
            comment = "😟 慎重に...慎重に..."
            bet_preference = "cautious"
        
        bet_amount = max(10, int(base_bet * bet_multiplier))
        
        # 借金限度額チェック（-2000コインまで）
        max_debt = -2000
        if debt_amount > max_debt:
            remaining_credit = abs(max_debt - debt_amount)
            bet_amount = min(bet_amount, remaining_credit)
        else:
            bet_amount = 10  # 最低限
        
        # ベット種類決定（心理状態依存）
        if bet_preference == "desperate":
            # 破れかぶれ：ゼロか数字狙い
            if random.random() < 0.3:
                bet_type = "zero"
                bet_value = None
            else:
                bet_type = "number"
                bet_value = random.choice([7, 13, 21, 6, 9])  # 「特別な」数字
        elif bet_preference == "aggressive":
            # 攻撃的：数字多め
            if random.random() < 0.6:
                bet_type = "number"
                bet_value = random.randint(1, 36)
            else:
                bet_type = random.choice(["red", "black"])
                bet_value = None
        elif bet_preference == "risky":
            # リスキー：数字と色の混合
            bet_options = ["red", "black", "number"]
            weights = [30, 30, 40]
            bet_type = random.choices(bet_options, weights=weights, k=1)[0]
            bet_value = random.randint(1, 36) if bet_type == "number" else None
        else:
            # その他：安全な色賭け中心
            bet_options = ["red", "black", "number"]
            weights = [45, 45, 10]
            bet_type = random.choices(bet_options, weights=weights, k=1)[0]
            bet_value = random.randint(1, 36) if bet_type == "number" else None
        
        print(f"{self.color}{self.name}: {comment}{Colors.RESET}")
        print(f"  💀 現在: {self.get_debt_status()}")
        print(f"  😱 絶望レベル: {despair_level:.1f}/10.0, 希望: {hope_level:.1f}")
        print(f"  🎰 {bet_type}に{bet_amount}コイン")
        
        # 心理状態アイコン
        state_icons = {
            "miracle_recovery": "🌈✨",
            "cautious_hope": "😟💭",
            "desperate_hope": "😰🙏",
            "deep_despair": "😱💔",
            "suicidal_despair": "🔥💀",
            "ultimate_despair": "💀⚡"
        }
        if psych_state in state_icons:
            print(f"  ⚠️  {state_icons[psych_state]} {psych_state.replace('_', ' ').title()}")
        
        return bet_type, bet_value, bet_amount
    
    def update_result(self, won: bool, payout: int, bet_amount: int):
        """結果更新と絶望の深化"""
        old_debt = self.get_current_debt()
        old_despair = self.debt_value.despair_level
        
        if won:
            self.total_wins += 1
            self.debt_value.experience_win(payout)
            
            if old_debt < 0 and self.get_current_debt() >= 0:
                result_msg = f"🌈 奇跡の勝利！ +{payout}コイン - 借金完済！！"
                emotion = "奇跡が起きた...生き返った気分だ"
            else:
                result_msg = f"🎉 勝利！ +{payout}コイン"
                emotion = "希望の光が見えた"
        else:
            self.total_losses += 1
            self.debt_value.experience_loss(bet_amount)
            
            result_msg = f"💀 敗北... -{bet_amount}コイン"
            if self.debt_value.despair_level >= 8.0:
                emotion = "絶望の底に沈んでいく..."
            elif self.debt_value.despair_level >= 5.0:
                emotion = "もう終わりだ..."
            else:
                emotion = "借金が雪だるま式に..."
        
        # 連続記録更新
        self.debt_system.update_streaks(won)
        
        # SSDエンジンにフィードバック（絶望による圧力）
        import numpy as np
        pressure_vector = np.zeros(4)
        
        despair_change = self.debt_value.despair_level - old_despair
        if won:
            pressure_vector[3] = 0.2  # UPPER: 希望
            if self.get_current_debt() >= 0:
                pressure_vector[3] = 1.0  # 奇跡の回復
        else:
            # 絶望による多層圧力
            pressure_vector[0] = despair_change * 0.8  # BASE: 絶望的な焦り
            pressure_vector[1] = despair_change * 0.5  # CORE: 責任と後悔
            pressure_vector[2] = despair_change * 0.3  # SOCIAL: 社会的地位の不安
            
            # 究極の絶望状態では全層に圧力
            if self.debt_value.despair_level >= 8.0:
                pressure_vector += 0.5
        
        self.state = self.engine.step(self.state, pressure_vector, dt=1.0)
        
        # エネルギーと圧力の履歴記録
        current_energy = np.sum(self.state.E)  # 総エネルギー
        self.energy_history.append(current_energy)
        self.pressure_history.append(np.linalg.norm(pressure_vector))  # 圧力の大きさ
        
        # leap発生チェック
        leap_occurred = False
        if hasattr(self.state, 'leap_history') and self.state.leap_history:
            # 前回チェック時より新しいleapがあるかチェック
            current_leap_count = len(self.state.leap_history)
            if current_leap_count > len(self.leap_history):
                leap_occurred = True
                self.leap_count += 1
                latest_leap = self.state.leap_history[-1]
                leap_type = latest_leap[1].name if hasattr(latest_leap[1], 'name') else str(latest_leap[1])
                print(f"  ⚡🔥 {self.name}: LEAP発生！ {leap_type} (時刻: {latest_leap[0]:.2f})")
        
        # このラウンドのleap状態を記録
        self.leap_history.append(leap_occurred)
        
        # 履歴記録
        new_debt = self.get_current_debt()
        new_despair = self.debt_value.despair_level
        self.debt_history.append(new_debt)
        self.despair_history.append(new_despair)
        
        # 結果表示
        print(f"{self.color}  {result_msg}{Colors.RESET}")
        print(f"  💰 借金: {abs(old_debt)}→{abs(new_debt) if new_debt < 0 else '完済！'}")
        print(f"  😱 絶望: {old_despair:.1f}→{new_despair:.1f} ({emotion})")
        
        # 連続記録表示
        if self.debt_system.consecutive_losses >= 3:
            print(f"  🔥 地獄の{self.debt_system.consecutive_losses}連敗...")
        elif self.debt_system.consecutive_wins >= 2:
            print(f"  ✨ 奇跡の{self.debt_system.consecutive_wins}連勝！")

# ===== カイジ的地獄ゲーム実行 =====
def run_kaiji_debt_hell_experiment():
    """カイジ的借金地獄実験"""
    print("=" * 80)
    print("💀 カイジ的借金地獄ルーレット with SSD Log版エンジン")
    print("=" * 80)
    print("【地獄の始まり】")
    print("・全員500コインの借金からスタート")
    print("・絶望レベルが行動を支配")
    print("・一発逆転か、更なる地獄か")
    print("・SSD Log版エンジンによる極限心理制御")
    print("・借金限度額: 2000コイン（それ以上は...）")
    print()
    
    # プレイヤー作成
    players = [
        KaijiDebtPlayer("カイジ", "balanced", -500),    # 主人公
        KaijiDebtPlayer("遠藤", "cautious", -500),      # 慎重派
        KaijiDebtPlayer("佐原", "aggressive", -500),    # 攻撃派
    ]
    
    # 地獄のルーレット準備
    roulette = KaijiRoulette()
    
    # 地獄ラウンド実行
    rounds = 25  # カイジ的に長期戦
    
    for round_num in range(1, rounds + 1):
        print(f"\n{'💀'*20} 地獄Round {round_num} {'💀'*20}")
        
        # 各プレイヤーがベット（借金限度まで）
        bets = []
        for player in players:
            if player.get_current_debt() > -2000:  # まだ限度額に達していない
                bet_type, bet_value, bet_amount = player.place_bet()
                bets.append((player, bet_type, bet_value, bet_amount))
            else:
                print(f"{player.color}{player.name}: 💀 借金限度額到達...もう終わりだ...{Colors.RESET}")
        
        if not bets:
            print("💀 全員が借金限度額に到達...地獄の終わり...")
            break
        
        # 地獄のルーレット回転
        result = roulette.spin()
        
        # 運命の判定
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
        
        # 地獄の中間報告
        if round_num % 10 == 0:
            print(f"\n💀 地獄{round_num}ラウンド後の絶望状況:")
            for player in players:
                debt = player.get_current_debt()
                despair = player.debt_value.despair_level
                hope = player.debt_value.hope_for_reversal
                win_rate = player.total_wins / player.round_count if player.round_count > 0 else 0
                
                if debt >= 0:
                    status_icon = "🌈"
                    status = f"奇跡の{debt}コイン"
                elif debt > -1000:
                    status_icon = "😱"
                    status = f"{abs(debt)}コインの借金"
                else:
                    status_icon = "💀"
                    status = f"地獄の{abs(debt)}コインの借金"
                
                print(f"{player.color}  {player.name}: {status_icon}{status} "
                      f"(絶望: {despair:.1f}, 希望: {hope:.1f}, "
                      f"勝率: {win_rate:.1%}){Colors.RESET}")
    
    # 地獄の最終審判
    print(f"\n{'💀'*80}")
    print("⚰️  地獄の最終審判")
    print(f"{'💀'*80}")
    
    for player in players:
        debt = player.get_current_debt()
        initial_debt = player.initial_debt
        debt_change = debt - initial_debt
        despair = player.debt_value.despair_level
        hope = player.debt_value.hope_for_reversal
        
        if debt >= 0:
            final_state = "🌈 奇跡の生還"
            judgement = "地獄から這い上がった英雄"
        elif debt > -1000:
            final_state = "😱 絶望の淵"
            judgement = "まだ希望は残っている"
        elif debt > -1800:
            final_state = "💀 地獄の住人"
            judgement = "絶望の底に沈んだ"
        else:
            final_state = "⚰️  永遠の呪い"
            judgement = "もう戻れない深淵に"
        
        print(f"\n{player.color}💀 {player.name} ({player.personality}){Colors.RESET}")
        print(f"  💰 借金変化: {abs(initial_debt)}→{abs(debt) if debt < 0 else f'完済+{debt}'} ({debt_change:+d})")
        print(f"  😱 最終絶望レベル: {despair:.1f}/10.0")
        print(f"  🙏 最終希望レベル: {hope:.1f}")
        print(f"  ⚖️  最終状態: {final_state}")
        print(f"  📜 審判: {judgement}")
        print(f"  🎯 勝率: {player.total_wins}/{player.round_count}ラウンド ({player.total_wins/player.round_count:.1%})")
        print(f"  🔥 最大連敗: 0")
        print(f"  ⚡ LEAP発生: {player.leap_count}回")
    
    # 地獄のグラフ作成
    create_kaiji_despair_charts(players)
    
    print(f"\n{'💀'*80}")
    print("⚰️  カイジ的借金地獄実験完了")
    print("【地獄の教訓】")
    print("・借金は絶望を生み、絶望は判断力を奪う")
    print("・一発逆転への希望が更なる地獄への入り口となる")
    print("・SSD Log版エンジンは極限の絶望状態でも制御可能")
    print("・性格により絶望への耐性と破れかぶれ度が異なる")
    print("・カイジの世界観：希望と絶望が交錯する人間ドラマ")
    print(f"{'💀'*80}")

def create_kaiji_despair_charts(players):
    """カイジ的絶望変化のグラフを作成"""
    fig, ((ax1, ax2, ax5), (ax3, ax4, ax6)) = plt.subplots(2, 3, figsize=(20, 10))
    
    colors = ['darkred', 'gray', 'darkorange']
    
    # グラフ1: 借金額の変化
    for i, player in enumerate(players):
        rounds = list(range(1, len(player.debt_history) + 1))
        debts = player.debt_history
        ax1.plot(rounds, debts, marker='o', color=colors[i], 
                label=f"{player.name}({player.personality})", linewidth=2)
        ax1.axhline(y=0, color='green', linestyle='--', alpha=0.5, label='完済ライン' if i == 0 else "")
        ax1.axhline(y=-2000, color='red', linestyle='--', alpha=0.5, label='限度額' if i == 0 else "")
    
    ax1.set_title('借金地獄の変遷', fontsize=14, fontweight='bold')
    ax1.set_xlabel('ラウンド')
    ax1.set_ylabel('借金額（負の値）')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # グラフ2: 絶望レベルの変化
    for i, player in enumerate(players):
        rounds = list(range(1, len(player.despair_history) + 1))
        despair = player.despair_history
        ax2.plot(rounds, despair, marker='s', color=colors[i], 
                label=f"{player.name}", linewidth=2)
        ax2.axhline(y=5.0, color='orange', linestyle='--', alpha=0.5, label='危険域' if i == 0 else "")
        ax2.axhline(y=8.0, color='red', linestyle='--', alpha=0.5, label='絶望域' if i == 0 else "")
    
    ax2.set_title('絶望レベルの深化', fontsize=14, fontweight='bold')
    ax2.set_xlabel('ラウンド')
    ax2.set_ylabel('絶望レベル (1-10)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # グラフ3: 借金vs絶望の相関
    for i, player in enumerate(players):
        ax3.scatter(player.debt_history, player.despair_history, 
                   color=colors[i], alpha=0.6, s=50, label=f"{player.name}")
    
    ax3.set_title('借金額 vs 絶望レベル', fontsize=14, fontweight='bold')
    ax3.set_xlabel('借金額')
    ax3.set_ylabel('絶望レベル')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # グラフ4: SSDエンジンエネルギー推移
    for i, player in enumerate(players):
        rounds = list(range(1, len(player.energy_history) + 1))
        ax4.plot(rounds, player.energy_history, 
                color=colors[i], marker='o', markersize=3,
                label=f"{player.name} Energy", linewidth=2)
    
    ax4.set_title('SSDエンジン エネルギー(E)推移', fontsize=14, fontweight='bold')
    ax4.set_xlabel('ラウンド')
    ax4.set_ylabel('総エネルギー')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # グラフ5: 投入圧力の推移
    for i, player in enumerate(players):
        rounds = list(range(1, len(player.pressure_history) + 1))
        ax5.plot(rounds, player.pressure_history, 
                color=colors[i], marker='s', markersize=3,
                label=f"{player.name} Pressure", linewidth=2)
    
    ax5.set_title('投入圧力推移', fontsize=14, fontweight='bold')
    ax5.set_xlabel('ラウンド')
    ax5.set_ylabel('圧力強度')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # グラフ6: E vs 圧力の相関
    for i, player in enumerate(players):
        ax6.scatter(player.pressure_history, player.energy_history, 
                   color=colors[i], alpha=0.6, s=50, label=f"{player.name}")
    
    ax6.set_title('投入圧力 vs エネルギー応答', fontsize=14, fontweight='bold')
    ax6.set_xlabel('投入圧力')
    ax6.set_ylabel('エネルギー')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    random.seed(42)  # カイジも運命には逆らえない
    run_kaiji_debt_hell_experiment()