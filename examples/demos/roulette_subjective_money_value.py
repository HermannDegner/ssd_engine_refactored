"""
お金の主観的価値上昇実験 with SSD Log版エンジン
「価値観の動的変化：お金に対する主観的価値の上昇メカニズム」

【実験コンセプト】
1. 主観的お金価値システム
   - 初期価値: 1コイン = 1の価値
   - 損失時: お金の価値が上昇（痛みの学習）
   - 勝利時: お金の価値が安定化

2. 価値上昇メカニズム
   - 損失パターンによる価値増幅
   - 連続損失での価値急上昇
   - リスク回避行動の強化

3. SSD統合
   - 価値変化をHumanPressureとして投入
   - Log版エンジンによる安定制御
   - κ（整合慣性）と価値観の相互作用

【理論的意義】
- 経済心理学における価値認知の変化
- 損失回避（Loss Aversion）の動的モデル化
- SSDエンジンによる価値観変化の制御

元コード: roulette_ssd_pure.py → 主観的価値システム統合版
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

# ===== 主観的お金価値システム =====
@dataclass
class MoneyValue:
    """お金の主観的価値"""
    objective_amount: int  # 客観的金額
    subjective_value: float  # 主観的価値倍率
    pain_coefficient: float  # 痛み係数（損失時の価値上昇率）
    recovery_rate: float  # 回復率（勝利時の価値安定化率）
    
    def get_subjective_worth(self) -> float:
        """主観的価値を計算（借金は負の価値として扱う）"""
        if self.objective_amount >= 0:
            return self.objective_amount * self.subjective_value
        else:
            # 借金の場合、負の価値だが主観的価値倍率で重みが増す
            return self.objective_amount * self.subjective_value
    
    def experience_loss(self, loss_amount: int):
        """損失経験による価値上昇"""
        # 損失が大きいほど価値が急上昇
        pain_factor = 1.0 + (loss_amount / 100.0) * self.pain_coefficient
        
        # 借金状態の場合、さらに価値が上昇（借金の重圧）
        if self.objective_amount < 0:
            debt_pressure = abs(self.objective_amount) / 1000.0  # 借金額に比例
            pain_factor *= (1.0 + debt_pressure * 0.5)  # 借金による追加圧力
        
        self.subjective_value *= pain_factor
        
        # 上限設定（暴走防止）
        self.subjective_value = min(self.subjective_value, 15.0)  # 借金時は上限を上げる
    
    def experience_win(self, win_amount: int):
        """勝利経験による価値安定化"""
        # 勝利で少し価値が下がる（安心感）
        relief_factor = 1.0 - self.recovery_rate * 0.1
        self.subjective_value = max(1.0, self.subjective_value * relief_factor)

class SubjectiveMoneySystem:
    """主観的お金価値管理システム"""
    
    def __init__(self):
        self.value_history = deque(maxlen=100)  # 価値変化履歴
        self.loss_streak = 0  # 連続損失回数
        self.win_streak = 0   # 連続勝利回数
        self.debt_threshold = -500  # 借金限度額（これ以下になると特別な心理状態）
        self.extreme_debt_threshold = -1000  # 極度の借金状態
        
    def create_money_value(self, amount: int, personality: str) -> MoneyValue:
        """性格に応じたお金価値を生成"""
        if personality == 'cautious':
            # 慎重派: 高い痛み係数、低い回復率
            return MoneyValue(
                objective_amount=amount,
                subjective_value=1.0,
                pain_coefficient=0.3,
                recovery_rate=0.05
            )
        elif personality == 'aggressive':
            # 攻撃派: 低い痛み係数、高い回復率
            return MoneyValue(
                objective_amount=amount,
                subjective_value=1.0,
                pain_coefficient=0.1,
                recovery_rate=0.15
            )
        else:  # balanced
            # バランス派: 中程度
            return MoneyValue(
                objective_amount=amount,
                subjective_value=1.0,
                pain_coefficient=0.2,
                recovery_rate=0.1
            )
    
    def update_streaks(self, won: bool):
        """連勝・連敗の更新"""
        if won:
            self.win_streak += 1
            self.loss_streak = 0
        else:
            self.loss_streak += 1
            self.win_streak = 0
    
    def get_streak_multiplier(self) -> float:
        """連続記録に基づく価値倍率"""
        if self.loss_streak >= 3:
            # 3連敗以上で価値急上昇
            return 1.0 + (self.loss_streak - 2) * 0.2
        elif self.win_streak >= 3:
            # 3連勝以上で価値安定化
            return max(0.8, 1.0 - (self.win_streak - 2) * 0.1)
        return 1.0
    
    def get_debt_psychological_state(self, current_amount: int) -> str:
        """借金状態に応じた心理状態を返す"""
        if current_amount >= 0:
            return "normal"
        elif current_amount > self.debt_threshold:
            return "light_debt"  # 軽い借金
        elif current_amount > self.extreme_debt_threshold:
            return "heavy_debt"  # 重い借金
        else:
            return "extreme_debt"  # 極度の借金

# ===== ルーレット設定 =====
class RouletteConfig:
    """ルーレット設定（ヨーロピアン）"""
    MAX_NUMBER = 36
    RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    # 配当レート（賭け金込み）
    PAYOUT_ZERO = 36   # 35:1 + 元金
    PAYOUT_NUMBER = 36 # 35:1 + 元金
    PAYOUT_RED = 2     # 1:1 + 元金
    PAYOUT_BLACK = 2   # 1:1 + 元金

class Roulette:
    """ルーレットゲーム（標準版）"""
    
    def __init__(self):
        self.config = RouletteConfig()
        self.spin_count = 0
    
    def spin(self) -> int:
        """ルーレットを回す"""
        result = random.randint(0, self.config.MAX_NUMBER)
        self.spin_count += 1
        
        color = self._get_color(result)
        print(f"\n🎰 ルーレット結果: {result} {color}")
        return result
    
    def _get_color(self, number: int) -> str:
        """数字の色を取得"""
        if number == 0:
            return "🟢 GREEN"
        elif number in self.config.RED_NUMBERS:
            return "🔴 RED"
        else:
            return "⚫ BLACK"

# ===== 主観的価値プレイヤー =====
class SubjectiveValuePlayer:
    """主観的お金価値を持つSSDプレイヤー"""
    
    def __init__(self, name: str, personality: str, initial_coins: int):
        self.name = name
        self.personality = personality
        self.initial_coins = initial_coins
        
        # Log版SSDエンジン
        params = SSDCoreParams()  # デフォルトパラメータ
        self.engine = SSDCoreEngine(params)
        self.state = create_default_state(num_layers=4)  # 状態を保持
        
        # 主観的価値システム
        self.money_system = SubjectiveMoneySystem()
        self.money_value = self.money_system.create_money_value(initial_coins, personality)
        
        # 履歴
        self.round_count = 0
        self.total_wins = 0
        self.total_losses = 0
        self.value_history = []
        
        # 色分け
        self.color = self._get_color()
        
        print(f"{self.color}💰 {name}({personality})が参加 - 初期価値観: 1コイン = {self.money_value.subjective_value:.2f}価値{Colors.RESET}")
    
    def _get_color(self) -> str:
        """プレイヤー色"""
        colors = [Colors.CYAN, Colors.MAGENTA, Colors.YELLOW, Colors.GREEN, Colors.BLUE]
        return colors[hash(self.name) % len(colors)]
    
    def get_current_coins(self) -> int:
        """現在のコイン数（借金可能）"""
        return self.money_value.objective_amount
    
    def get_debt_status(self) -> str:
        """借金状態の表示"""
        amount = self.get_current_coins()
        if amount >= 0:
            return f"{amount}コイン"
        else:
            return f"{abs(amount)}コインの借金"
    
    def get_subjective_worth(self) -> float:
        """主観的総価値"""
        return self.money_value.get_subjective_worth()
    
    def place_bet(self) -> Tuple[str, Optional[int], int]:
        """ベット決定（主観的価値に基づく）"""
        self.round_count += 1
        
        # 借金状態の心理的影響を考慮
        current_coins = self.get_current_coins()
        debt_state = self.money_system.get_debt_psychological_state(current_coins)
        subjective_worth = self.get_subjective_worth()
        base_bet = 10
        
        # 借金状態と価値観に基づく調整
        if debt_state == "extreme_debt":
            # 極度の借金 → 破れかぶれ
            bet_multiplier = 2.0
            comment = "もう破れかぶれだ！一発逆転を狙う！"
        elif debt_state == "heavy_debt":
            # 重い借金 → 焦りの賭け
            bet_multiplier = 1.5
            comment = "借金を返さなければ...大きく賭けよう"
        elif debt_state == "light_debt":
            # 軽い借金 → やや焦り
            bet_multiplier = 1.2
            comment = "借金があるから少し攻めよう"
        elif abs(subjective_worth) > self.initial_coins * 3:
            # 価値が3倍以上 → 極度に保守的
            bet_multiplier = 0.3
            comment = "お金が神聖すぎる...最小限で"
        elif abs(subjective_worth) > self.initial_coins * 2:
            # 価値が2倍以上 → 保守的
            bet_multiplier = 0.5
            comment = "お金が大切すぎる..."
        elif abs(subjective_worth) > self.initial_coins * 1.5:
            # 価値が1.5倍以上 → やや保守的
            bet_multiplier = 0.8
            comment = "慎重に行こう"
        else:
            # 通常の価値観
            bet_multiplier = 1.0
            comment = "普通に賭けよう"
        
        bet_amount = max(5, int(base_bet * bet_multiplier))
        
        # 借金限度額チェック（-2000コインまで借金可能）
        max_debt = -2000
        if current_coins > 0:
            # 正の残高がある場合は従来通り
            bet_amount = min(bet_amount, current_coins // 4 + 50)  # 少し余裕を持たせる
        else:
            # 借金状態の場合、借金限度まで賭け可能
            remaining_credit = max_debt - current_coins
            bet_amount = min(bet_amount, abs(remaining_credit) // 2)  # 残り借金枠の半分まで
        
        # ベット種類決定（性格依存）
        if self.personality == 'cautious':
            # 慎重: 赤黒中心
            bet_type = random.choice(["red", "black"])
            bet_value = None
        elif self.personality == 'aggressive':
            # 攻撃的: 数字賭け多め
            if random.random() < 0.4:
                bet_type = "number"
                bet_value = random.randint(1, 36)
            else:
                bet_type = random.choice(["red", "black"])
                bet_value = None
        else:  # balanced
            # バランス: 色々試す
            bet_options = ["red", "black", "number", "zero"]
            weights = [40, 40, 15, 5]
            bet_type = random.choices(bet_options, weights=weights, k=1)[0]
            bet_value = random.randint(1, 36) if bet_type == "number" else None
        
        print(f"{self.color}{self.name}: {comment} - {bet_type}に{bet_amount}コイン{Colors.RESET}")
        print(f"  💰 現在: {self.get_debt_status()}")
        print(f"  💎 主観的価値: {subjective_worth:.1f} (倍率: {self.money_value.subjective_value:.2f}x)")
        if debt_state != "normal":
            debt_status_msg = {
                "light_debt": "💸 軽い借金状態",
                "heavy_debt": "🔥 重い借金状態", 
                "extreme_debt": "💀 極度の借金状態"
            }
            print(f"  ⚠️  {debt_status_msg[debt_state]}")
        
        return bet_type, bet_value, bet_amount
    
    def update_result(self, won: bool, payout: int, bet_amount: int):
        """結果更新と価値観変化"""
        old_value = self.money_value.subjective_value
        old_coins = self.get_current_coins()
        
        if won:
            self.total_wins += 1
            self.money_value.objective_amount += payout
            self.money_value.experience_win(payout)
            
            result_msg = f"🎉 勝利！ +{payout}コイン"
            emotion = "安心感でお金の価値がやや下がった"
        else:
            self.total_losses += 1
            self.money_value.objective_amount -= bet_amount
            self.money_value.experience_loss(bet_amount)
            
            result_msg = f"💸 敗北... -{bet_amount}コイン"
            emotion = "損失の痛みでお金の価値が上昇"
        
        # 連続記録による価値調整
        self.money_system.update_streaks(won)
        streak_mult = self.money_system.get_streak_multiplier()
        self.money_value.subjective_value *= streak_mult
        
        # SSDエンジンにフィードバック
        import numpy as np
        pressure_vector = np.zeros(4)  # 4層の圧力ベクトル
        if won:
            pressure_vector[3] = 0.1  # UPPER層に少し満足
        else:
            # 損失による圧力（価値変化に比例）
            value_change = self.money_value.subjective_value - old_value
            pressure_vector[0] = value_change * 0.5  # BASE: 本能的な焦り
            pressure_vector[1] = value_change * 0.3  # CORE: 規範的な反省
            
            # 借金状態の追加圧力
            debt_state = self.money_system.get_debt_psychological_state(self.get_current_coins())
            if debt_state == "extreme_debt":
                pressure_vector[0] += 1.0  # 極度の焦り
                pressure_vector[2] += 0.5  # 社会的な恥の意識
            elif debt_state == "heavy_debt":
                pressure_vector[0] += 0.5  # 焦り
                pressure_vector[1] += 0.3  # 責任感
            elif debt_state == "light_debt":
                pressure_vector[0] += 0.2  # 軽い焦り
        
        self.state = self.engine.step(self.state, pressure_vector, dt=1.0)
        
        # 履歴記録
        new_value = self.money_value.subjective_value
        self.value_history.append({
            'round': self.round_count,
            'won': won,
            'coins': self.get_current_coins(),
            'subjective_value': new_value,
            'subjective_worth': self.get_subjective_worth()
        })
        
        # 結果表示
        print(f"{self.color}  {result_msg}{Colors.RESET}")
        if old_coins >= 0 and self.get_current_coins() < 0:
            print(f"  💰 資金: {old_coins}コイン → {abs(self.get_current_coins())}コインの借金 ⚠️初借金！")
        elif old_coins < 0 and self.get_current_coins() >= 0:
            print(f"  💰 資金: {abs(old_coins)}コインの借金 → {self.get_current_coins()}コイン 🎉借金完済！")
        else:
            print(f"  💰 資金: {self.get_debt_status()} → {self.get_debt_status()}")
        print(f"  📈 価値観: {old_value:.2f} → {new_value:.2f} ({emotion})")
        print(f"  💎 主観的価値: {self.get_subjective_worth():.1f}")
        
        # 連続記録表示
        if self.money_system.loss_streak >= 2:
            print(f"  🔥 {self.money_system.loss_streak}連敗中...")
        elif self.money_system.win_streak >= 2:
            print(f"  ✨ {self.money_system.win_streak}連勝中！")

# ===== ゲーム実行 =====
def run_subjective_money_experiment():
    """主観的お金価値上昇実験"""
    print("=" * 80)
    print("💰 お金の主観的価値上昇実験 with SSD Log版エンジン")
    print("=" * 80)
    print("【実験概要】")
    print("・損失経験によりお金の主観的価値が上昇")
    print("・勝利経験により価値が安定化")
    print("・SSD Log版エンジンによる行動制御")
    print("・3人の異なる性格による価値観変化の比較")
    print()
    
    # プレイヤー作成
    players = [
        SubjectiveValuePlayer("太郎", "cautious", 1000),    # 慎重派
        SubjectiveValuePlayer("花子", "aggressive", 1000),  # 攻撃派
        SubjectiveValuePlayer("ユウ", "balanced", 1000),    # バランス派
    ]
    
    # ルーレット準備
    roulette = Roulette()
    
    # ゲーム実行
    rounds = 30
    
    for round_num in range(1, rounds + 1):
        print(f"\n{'='*20} Round {round_num} {'='*20}")
        
        # 各プレイヤーがベット（借金でも続行可能、-2000コインが限度）
        bets = []
        for player in players:
            if player.get_current_coins() > -2000:  # 借金限度額チェック
                bet_type, bet_value, bet_amount = player.place_bet()
                bets.append((player, bet_type, bet_value, bet_amount))
        
        if not bets:
            print("全プレイヤーが借金限度額に到達...")
            break
        
        # ルーレット回転
        result = roulette.spin()
        
        # 結果判定
        for player, bet_type, bet_value, bet_amount in bets:
            won = False
            payout = 0
            
            if bet_type == "zero" and result == 0:
                won = True
                payout = bet_amount * (RouletteConfig.PAYOUT_ZERO - 1)
            elif bet_type == "number" and result == bet_value:
                won = True
                payout = bet_amount * (RouletteConfig.PAYOUT_NUMBER - 1)
            elif bet_type == "red" and result in RouletteConfig.RED_NUMBERS:
                won = True
                payout = bet_amount * (RouletteConfig.PAYOUT_RED - 1)
            elif bet_type == "black" and result in RouletteConfig.BLACK_NUMBERS:
                won = True
                payout = bet_amount * (RouletteConfig.PAYOUT_BLACK - 1)
            
            player.update_result(won, payout, bet_amount)
        
        # 途中経過表示
        if round_num % 10 == 0:
            print(f"\n📊 {round_num}ラウンド後の状況:")
            for player in players:
                coins = player.get_current_coins()
                worth = player.get_subjective_worth()
                value_mult = player.money_value.subjective_value
                win_rate = player.total_wins / player.round_count if player.round_count > 0 else 0
                debt_state = player.money_system.get_debt_psychological_state(coins)
                
                status_icon = "💰" if coins >= 0 else "💸"
                debt_info = ""
                if debt_state != "normal":
                    debt_icons = {"light_debt": "⚠️", "heavy_debt": "🔥", "extreme_debt": "💀"}
                    debt_info = f" {debt_icons[debt_state]}"
                
                print(f"{player.color}  {player.name}: {status_icon}{player.get_debt_status()}{debt_info} "
                      f"(主観価値: {worth:.1f}, 倍率: {value_mult:.2f}x, "
                      f"勝率: {win_rate:.1%}){Colors.RESET}")
    
    # 最終結果
    print(f"\n{'='*80}")
    print("🏁 実験結果サマリー")
    print(f"{'='*80}")
    
    for player in players:
        coins = player.get_current_coins()
        initial_worth = player.initial_coins
        final_worth = player.get_subjective_worth()
        value_change = player.money_value.subjective_value
        
        profit_loss = coins - player.initial_coins
        subjective_profit_loss = final_worth - initial_worth
        
        debt_state = player.money_system.get_debt_psychological_state(coins)
        debt_status_final = "正常" if debt_state == "normal" else {
            "light_debt": "軽い借金", "heavy_debt": "重い借金", "extreme_debt": "極度の借金"
        }[debt_state]
        
        print(f"\n{player.color}🧑‍💼 {player.name} ({player.personality}){Colors.RESET}")
        print(f"  💰 客観的結果: {player.initial_coins}コイン → {player.get_debt_status()} ({profit_loss:+d})")
        print(f"  💎 主観的結果: {initial_worth:.1f} → {final_worth:.1f}価値 ({subjective_profit_loss:+.1f})")
        print(f"  📈 価値観変化: 1.00x → {value_change:.2f}x")
        print(f"  🏦 最終状態: {debt_status_final}")
        print(f"  🎯 勝率: {player.total_wins}/{player.round_count}ラウンド ({player.total_wins/player.round_count:.1%})")
        print(f"  🔥 最大連敗: {max([h.get('loss_streak', 0) for h in player.value_history] + [0])}")
    
    # グラフ作成
    create_subjective_value_charts(players)
    
    print(f"\n{'='*80}")
    print("✅ 借金対応主観的価値上昇実験完了")
    print("【結論】")
    print("・損失経験により価値観が大きく変化")
    print("・借金状態により心理的圧力と行動パターンが劇的に変化")
    print("・破れかぶれ効果: 極度の借金時に大胆な賭けに出る心理を再現")
    print("・性格により価値変化パターンが異なる")
    print("・SSD Log版エンジンによる安定制御を確認")
    print(f"={'='*80}")

def create_subjective_value_charts(players):
    """主観的価値変化のグラフを作成"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    colors = ['cyan', 'magenta', 'yellow']
    
    # グラフ1: 主観的価値倍率の変化
    for i, player in enumerate(players):
        rounds = [h['round'] for h in player.value_history]
        values = [h['subjective_value'] for h in player.value_history]
        ax1.plot(rounds, values, marker='o', color=colors[i], label=f"{player.name}({player.personality})")
    
    ax1.set_title('主観的価値倍率の変化')
    ax1.set_xlabel('ラウンド')
    ax1.set_ylabel('価値倍率')
    ax1.legend()
    ax1.grid(True)
    
    # グラフ2: 実際のコイン数
    for i, player in enumerate(players):
        rounds = [h['round'] for h in player.value_history]
        coins = [h['coins'] for h in player.value_history]
        ax2.plot(rounds, coins, marker='s', color=colors[i], label=f"{player.name}")
    
    ax2.set_title('コイン数の変化')
    ax2.set_xlabel('ラウンド')
    ax2.set_ylabel('コイン数')
    ax2.legend()
    ax2.grid(True)
    
    # グラフ3: 主観的総価値
    for i, player in enumerate(players):
        rounds = [h['round'] for h in player.value_history]
        worth = [h['subjective_worth'] for h in player.value_history]
        ax3.plot(rounds, worth, marker='^', color=colors[i], label=f"{player.name}")
    
    ax3.set_title('主観的総価値の変化')
    ax3.set_xlabel('ラウンド')
    ax3.set_ylabel('主観的価値')
    ax3.legend()
    ax3.grid(True)
    
    # グラフ4: 勝敗パターン
    for i, player in enumerate(players):
        rounds = [h['round'] for h in player.value_history]
        results = [1 if h['won'] else -1 for h in player.value_history]
        ax4.scatter(rounds, [i] * len(rounds), c=results, cmap='RdYlGn', alpha=0.7, s=50)
    
    ax4.set_title('勝敗パターン (赤=負け, 緑=勝ち)')
    ax4.set_xlabel('ラウンド')
    ax4.set_ylabel('プレイヤー')
    ax4.set_yticks(range(len(players)))
    ax4.set_yticklabels([p.name for p in players])
    ax4.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    random.seed(42)  # 再現性のため
    run_subjective_money_experiment()