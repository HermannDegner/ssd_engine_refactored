#!/usr/bin/env python3
"""
Apex Survivor - キャラクター思考経路解析器

各プレイヤーの内部思考プロセスを詳細に可視化・解析
- 意味圧の生成過程
- E/κバランスの変化
- 競合者分析の結果
- 最終的な選択決定理由
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ssd_core_engine import SSDCoreEngine
from core.ssd_human_module import HumanAgent, HumanPressure, HumanLayer
from examples.apex_survivor_ssd_pure_v3 import ApexPlayerV3, GameConfig
import random

class ThoughtAnalyzer:
    """思考過程解析器"""
    
    @staticmethod
    def analyze_player_decision(player: ApexPlayerV3, situation: dict, other_history: dict = None):
        """プレイヤーの決定過程を詳細解析"""
        
        print(f"\n{'='*80}")
        print(f"🧠 {player.name}の思考解析 - {situation['personality']}派")
        print(f"{'='*80}")
        
        # 状況情報
        print(f"📊 現在状況:")
        print(f"  • HP: {player.hp}/5")
        print(f"  • スコア: {player.score}pts (順位: {situation['rank']}位)")
        print(f"  • リーダースコア: {situation['leader_score']}pts")
        print(f"  • ラウンド: {situation['round']}/{situation['total_rounds']} (セット {situation['set']}/{situation['total_sets']})")
        print(f"  • 生存者数: {situation['alive_count']}人")
        
        # 現在のSSD状態
        print(f"\n🔬 決定前のSSD状態:")
        E_before = player.agent.state.E.copy()
        kappa_before = player.agent.state.kappa.copy()
        print(f"  • E値: BASE={E_before[0]:.1f}, CORE={E_before[1]:.1f}, UPPER={E_before[2]:.1f}")
        print(f"  • κ値: BASE={kappa_before[0]:.1f}, CORE={kappa_before[1]:.1f}, UPPER={kappa_before[2]:.1f}")
        
        # 意味圧生成過程のシミュレーション
        print(f"\n⚡ 意味圧生成過程:")
        pressure = HumanPressure()
        
        # HP による死の恐怖圧力
        hp_pressure = ThoughtAnalyzer._analyze_hp_pressure(player.hp)
        pressure.base += hp_pressure['base']
        pressure.upper += hp_pressure['upper'] 
        pressure.core += hp_pressure['core']
        print(f"  🩸 HP圧力 (HP={player.hp}): BASE+{hp_pressure['base']:.0f}, CORE{hp_pressure['core']:+.0f}, UPPER+{hp_pressure['upper']:.0f}")
        
        # 順位による死の恐怖/勝利圧力
        rank_pressure = ThoughtAnalyzer._analyze_rank_pressure(
            situation['rank'], situation['leader_score'], player.score,
            situation['round'], situation['total_rounds'], 
            situation['set'], situation['total_sets'], player.hp
        )
        pressure.base += rank_pressure['base']
        pressure.core += rank_pressure['core']
        pressure.upper += rank_pressure['upper']
        print(f"  🏆 順位圧力 ({situation['rank']}位): BASE+{rank_pressure['base']:.0f}, CORE+{rank_pressure['core']:.0f}, UPPER+{rank_pressure['upper']:.0f}")
        
        # 競合者分析圧力
        if other_history and situation['round'] > 1:
            competitor_pressure = ThoughtAnalyzer._analyze_competitor_pressure(
                other_history, situation['rank'], situation['leader_score']
            )
            pressure.base += competitor_pressure['risk_assessment']
            pressure.core += competitor_pressure['competitive_pressure']
            pressure.upper += competitor_pressure['strategic_pressure']
            print(f"  🎯 競合者分析: BASE+{competitor_pressure['risk_assessment']:.0f}, CORE+{competitor_pressure['competitive_pressure']:.0f}, UPPER+{competitor_pressure['strategic_pressure']:.0f}")
        
        # セット終盤ボーナス圧力など（その他の圧力も同様に解析可能）
        
        print(f"  📊 総意味圧: BASE+{pressure.base:.0f}, CORE+{pressure.core:.0f}, UPPER+{pressure.upper:.0f}")
        
        # SSDエンジンによるE値更新シミュレーション
        print(f"\n🔄 SSDエンジン処理:")
        player.agent.step(pressure, dt=1.0)
        E_after = player.agent.state.E.copy()
        
        print(f"  • E変化: BASE {E_before[0]:.1f}→{E_after[0]:.1f} ({E_after[0]-E_before[0]:+.1f})")
        print(f"  • E変化: CORE {E_before[1]:.1f}→{E_after[1]:.1f} ({E_after[1]-E_before[1]:+.1f})")
        print(f"  • E変化: UPPER {E_before[2]:.1f}→{E_after[2]:.1f} ({E_after[2]-E_before[2]:+.1f})")
        
        # E/κバランス解析
        print(f"\n⚖️ E/κバランス解析:")
        kappa = player.agent.state.kappa
        
        action_BASE = max(0, E_after[0] - kappa[0])
        action_CORE = max(0, E_after[1] - kappa[1])
        action_UPPER = max(0, E_after[2] - kappa[2])
        
        suppress_BASE = max(0, kappa[0] - E_after[0])
        suppress_CORE = max(0, kappa[1] - E_after[1])
        suppress_UPPER = max(0, kappa[2] - E_after[2])
        
        print(f"  🔥 行動要求: BASE={action_BASE:.1f} (生存行動), CORE={action_CORE:.1f} (攻撃行動), UPPER={action_UPPER:.1f} (戦略行動)")
        print(f"  🧊 行動抑制: BASE={suppress_BASE:.1f} (リスク許容), CORE={suppress_CORE:.1f} (守備), UPPER={suppress_UPPER:.1f} (直感)")
        
        # 性格フィルター解析
        print(f"\n🎭 性格フィルター ({player.personality}派):")
        choice_value = ThoughtAnalyzer._analyze_personality_choice(
            player.personality, action_BASE, action_CORE, action_UPPER
        )
        print(f"  • 計算結果: {choice_value:.2f}")
        
        final_choice = max(1, min(10, int(choice_value + 0.5)))
        crash_rate = GameConfig.CHOICES[final_choice]['crash_rate']
        
        print(f"\n🎯 最終決定:")
        print(f"  • 選択: {final_choice} (クラッシュ率: {crash_rate}%)")
        print(f"  • 期待スコア: {GameConfig.CHOICES[final_choice]['score']}pts")
        
        # 決定理由の要約
        dominant_layer = "BASE" if action_BASE >= max(action_CORE, action_UPPER) else \
                        "CORE" if action_CORE >= action_UPPER else "UPPER"
        
        print(f"\n💭 思考パターン要約:")
        print(f"  • 支配層: {dominant_layer}層 ({'生存本能' if dominant_layer=='BASE' else '勝利欲求' if dominant_layer=='CORE' else '戦略思考'})")
        
        if dominant_layer == "BASE":
            print(f"  • 判断: 生存を最優先。安全な選択を志向")
        elif dominant_layer == "CORE":
            print(f"  • 判断: 勝利への欲求が強い。リスクを取って攻撃的に")
        else:
            print(f"  • 判断: 戦略的思考が働く。計算に基づいた選択")
        
        return {
            'choice': final_choice,
            'crash_rate': crash_rate,
            'dominant_layer': dominant_layer,
            'E_values': E_after.tolist(),
            'action_values': [action_BASE, action_CORE, action_UPPER],
            'pressure_total': pressure.base + pressure.core + pressure.upper
        }
    
    @staticmethod
    def _analyze_hp_pressure(hp: int) -> dict:
        """HP状態による圧力解析"""
        if hp == 1:
            return {'base': 800.0, 'core': -300.0, 'upper': 500.0}
        elif hp == 2:
            return {'base': 400.0, 'core': -150.0, 'upper': 300.0}
        elif hp == 3:
            return {'base': 150.0, 'core': -50.0, 'upper': 150.0}
        elif hp == 4:
            return {'base': 50.0, 'core': 0.0, 'upper': 80.0}
        else:
            return {'base': 0.0, 'core': 0.0, 'upper': 0.0}
    
    @staticmethod
    def _analyze_rank_pressure(rank: int, leader_score: int, player_score: int,
                              round_num: int, total_rounds: int, current_set: int, 
                              total_sets: int, hp: int) -> dict:
        """順位による圧力解析"""
        pressure = {'base': 0.0, 'core': 0.0, 'upper': 0.0}
        
        if rank > 1:  # 2位以下 = 死の恐怖
            score_gap = leader_score - player_score
            remaining_rounds = total_rounds - round_num
            remaining_sets = total_sets - current_set + 1
            
            death_fear_base = 100.0 * remaining_sets
            death_imminence = min(200.0, score_gap * 2.0)
            gap_pressure = death_fear_base + death_imminence
            
            hp1_bonus = 1.3 if hp == 1 else 1.0
            max_gain_rounds = int(100 * remaining_rounds * hp1_bonus)
            max_gain = max_gain_rounds + 50  # セットボーナス考慮
            
            if score_gap <= max_gain:  # 逆転可能
                if rank <= 3:
                    pressure['core'] = 100.0 + gap_pressure * 0.5
                    pressure['upper'] = 200.0
                    pressure['base'] = 80.0
                else:
                    pressure['core'] = 200.0 + gap_pressure * 0.5
                    pressure['upper'] = 250.0
                    pressure['base'] = 150.0
            else:  # 逆転不可能
                if remaining_sets > 1:
                    pressure['core'] = 500.0
                    pressure['upper'] = 200.0
                    pressure['base'] = 2000.0
                else:
                    pressure['core'] = 100.0
                    pressure['upper'] = 50.0
                    pressure['base'] = 3250.0
        
        elif rank == 1:  # 1位 = リード防衛圧力
            remaining_rounds = total_rounds - round_num
            if remaining_rounds <= 1:
                pressure['core'] = 100.0
                pressure['upper'] = 30.0
                pressure['base'] = 30.0
            elif remaining_rounds <= 3:
                pressure['core'] = 200.0
                pressure['upper'] = 80.0
                pressure['base'] = 60.0
            else:
                pressure['core'] = 300.0
                pressure['upper'] = 120.0
                pressure['base'] = 100.0
        
        return pressure
    
    @staticmethod
    def _analyze_competitor_pressure(other_history: dict, current_rank: int, leader_score: int) -> dict:
        """競合者分析圧力（簡易版）"""
        if not other_history:
            return {'strategic_pressure': 0.0, 'competitive_pressure': 0.0, 'risk_assessment': 0.0}
        
        # 他プレイヤーの平均リスク度を計算
        total_choices = 0
        total_risk = 0
        aggressive_count = 0
        conservative_count = 0
        
        for player_name, choices in other_history.items():
            if choices:
                avg_choice = sum(choices) / len(choices)
                total_choices += len(choices)
                total_risk += sum(choices)
                
                if avg_choice >= 7:
                    aggressive_count += 1
                elif avg_choice <= 3:
                    conservative_count += 1
        
        if total_choices == 0:
            return {'strategic_pressure': 0.0, 'competitive_pressure': 0.0, 'risk_assessment': 0.0}
        
        avg_risk = total_risk / total_choices
        competitor_count = len(other_history)
        
        # 基本的な戦略圧力
        strategic_pressure = min(100.0, avg_risk * 10 + competitor_count * 5)
        
        # 競争圧力（攻撃的プレイヤーが多いほど高い）
        competitive_pressure = min(80.0, aggressive_count * 20 + (avg_risk - 4) * 10)
        
        # リスク評価（保守的プレイヤーが多いと安全になりやすい）
        risk_assessment = min(60.0, (7 - avg_risk) * 8 + conservative_count * 10)
        
        return {
            'strategic_pressure': max(0, strategic_pressure),
            'competitive_pressure': max(0, competitive_pressure), 
            'risk_assessment': max(0, risk_assessment)
        }
    
    @staticmethod
    def _analyze_personality_choice(personality: str, action_BASE: float, action_CORE: float, action_UPPER: float) -> float:
        """性格別選択計算の解析"""
        
        if personality == 'cautious':
            safety_drive = action_BASE * 2.0 - action_CORE * 0.5
            
            if action_UPPER > 3.0:
                return 1.5 + action_UPPER * 0.3
            elif safety_drive > 5.0:
                return 2.0
            elif safety_drive > 2.0:
                return 3.0
            elif action_CORE > action_BASE * 1.5:
                return 3.0 + action_CORE * 0.2
            else:
                return 2.5
        
        elif personality == 'aggressive':
            attack_drive = action_CORE * 2.0 - action_BASE * 0.5
            
            if action_UPPER > 5.0:
                return 3.0 + action_UPPER * 0.5 + action_CORE * 0.1
            elif attack_drive > 15.0:
                return 7.0
            elif attack_drive > 8.0:
                return 5.0 + attack_drive * 0.1
            elif action_BASE > action_CORE * 2.0:
                return 3.0 + action_BASE * 0.1
            else:
                return 4.0
        
        else:  # balanced
            strategic_ratio = action_CORE / (action_BASE + 1.0)
            
            if action_UPPER > 5.0:
                return 2.0 + action_UPPER * 0.4
            elif strategic_ratio > 2.5:
                return 4.0 + action_CORE * 0.15
            elif strategic_ratio < 0.4:
                return 2.0 + action_BASE * 0.1
            else:
                return 3.0 + action_UPPER * 0.5


def demo_thought_analysis():
    """思考解析デモ"""
    
    print("🧠 Apex Survivor - キャラクター思考経路解析デモ")
    print("=" * 80)
    
    # テストプレイヤーを作成
    players = [
        ApexPlayerV3("田中", "cautious", "🔵"),
        ApexPlayerV3("佐藤", "aggressive", "🔴"), 
        ApexPlayerV3("鈴木", "balanced", "🟢")
    ]
    
    # 各プレイヤーのスコアとHPを設定（ゲーム中盤想定）
    players[0].score = 200  # 田中: 2位
    players[0].hp = 2       # HP危険
    
    players[1].score = 150  # 佐藤: 3位  
    players[1].hp = 4       # HP安全
    
    players[2].score = 250  # 鈴木: 1位
    players[2].hp = 3       # HP普通
    
    # 選択履歴を設定（過去3ラウンド）
    players[0].choice_history = [3, 4, 2]  # 慎重
    players[1].choice_history = [6, 7, 5]  # 攻撃的
    players[2].choice_history = [4, 5, 4]  # バランス
    
    # テスト状況設定
    test_situation = {
        'round': 4,
        'total_rounds': 5,
        'set': 2, 
        'total_sets': 5,
        'alive_count': 7,
        'leader_score': 250
    }
    
    # 他プレイヤーの履歴
    other_histories_for_tanaka = {
        '佐藤': [6, 7, 5],
        '鈴木': [4, 5, 4]
    }
    
    other_histories_for_sato = {
        '田中': [3, 4, 2],
        '鈴木': [4, 5, 4]
    }
    
    other_histories_for_suzuki = {
        '田中': [3, 4, 2],
        '佐藤': [6, 7, 5]
    }
    
    # 各プレイヤーの思考解析
    for i, player in enumerate(players):
        situation = test_situation.copy()
        situation['personality'] = player.personality
        situation['rank'] = [2, 3, 1][i]  # 田中=2位, 佐藤=3位, 鈴木=1位
        
        other_history = [other_histories_for_tanaka, other_histories_for_sato, other_histories_for_suzuki][i]
        
        result = ThoughtAnalyzer.analyze_player_decision(player, situation, other_history)
        
        print(f"\n🎮 実際にmake_choiceを実行:")
        actual_choice = player.make_choice(
            situation['rank'], situation['leader_score'], 
            situation['round'], situation['total_rounds'],
            situation['alive_count'], situation['set'], 
            situation['total_sets'], other_history
        )
        print(f"  実際の選択: {actual_choice}")
        print(f"  解析予測: {result['choice']}")
        print(f"  予測精度: {'✅ 一致' if actual_choice == result['choice'] else '❌ 不一致'}")


if __name__ == "__main__":
    demo_thought_analysis()