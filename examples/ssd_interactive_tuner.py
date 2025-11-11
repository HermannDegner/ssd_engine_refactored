"""
SSD Interactive Parameter Tuner - インタラクティブ調整システム

SSDの本質的問題：「数字のバランス調整が全て」
→ 解決策：直感的・視覚的・段階的調整システム

特徴:
1. 0-10の直感的スケール
2. リアルタイム結果確認
3. A/B比較テスト
4. ベストプラクティス記録
"""

import numpy as np
from typing import Dict, Any, List, Tuple
import json

class SimpleSSDPlayer:
    """最もシンプルなSSDプレイヤー（調整専用）"""
    
    def __init__(self, name: str):
        self.name = name
        
        # ===== 調整可能パラメータ（全て0-10） =====
        self.survival_base = 5.0      # 生存本能の基準値
        self.competition_base = 5.0   # 競争心の基準値  
        self.strategy_base = 5.0      # 戦略性の基準値
        
        # 状況への反応度
        self.hp_sensitivity = 5.0     # HP減少への敏感さ
        self.rank_sensitivity = 5.0   # 順位への敏感さ
        
        # 行動への変換係数
        self.safety_weight = 5.0      # 安全志向の強さ
        self.attack_weight = 5.0      # 攻撃志向の強さ
        
        # 内部状態
        self.reset_state()
    
    def reset_state(self):
        """状態をリセット"""
        self.current_survival = self.survival_base
        self.current_competition = self.competition_base
        self.current_strategy = self.strategy_base
    
    def set_personality(self, personality_type: str):
        """性格プリセット"""
        if personality_type == "cautious":
            self.survival_base = 8.0
            self.competition_base = 3.0
            self.hp_sensitivity = 9.0
            self.safety_weight = 8.0
            self.attack_weight = 2.0
        elif personality_type == "aggressive":
            self.survival_base = 3.0
            self.competition_base = 8.0
            self.rank_sensitivity = 9.0
            self.safety_weight = 2.0
            self.attack_weight = 8.0
        elif personality_type == "strategic":
            self.strategy_base = 8.0
            self.hp_sensitivity = 6.0
            self.rank_sensitivity = 7.0
            self.safety_weight = 4.0
            self.attack_weight = 6.0
        else:  # balanced
            pass  # デフォルト値のまま
    
    def update_from_situation(self, hp: int, rank: int, score_gap: int):
        """状況に基づいて内部状態を更新"""
        
        # HP状況の影響
        hp_threat = (5 - hp) / 4  # 0-1
        hp_impact = hp_threat * self.hp_sensitivity
        
        # 順位状況の影響  
        rank_threat = (rank - 1) / 6  # 0-1
        gap_threat = min(1.0, score_gap / 100)  # 0-1
        rank_impact = (rank_threat + gap_threat) / 2 * self.rank_sensitivity
        
        # 内部状態更新（0-10範囲を維持）
        self.current_survival = min(10.0, self.survival_base + hp_impact)
        self.current_competition = min(10.0, self.competition_base + rank_impact)
        self.current_strategy = min(10.0, self.strategy_base + (hp_impact + rank_impact) / 4)
    
    def make_choice(self) -> int:
        """現在の内部状態から選択を決定"""
        
        # 基準選択（中間リスク）
        base_choice = 5.0
        
        # 各要素の寄与
        safety_pull = -self.current_survival * (self.safety_weight / 10) * 0.5  # 安全方向
        attack_push = self.current_competition * (self.attack_weight / 10) * 0.4  # 攻撃方向
        strategy_adjust = (self.current_strategy - 5.0) * 0.1  # 戦略調整
        
        final_choice = base_choice + safety_pull + attack_push + strategy_adjust
        
        # 1-10に制限
        return max(1, min(10, int(final_choice + 0.5)))
    
    def get_status(self) -> Dict[str, Any]:
        """現在の状態を返す"""
        return {
            'name': self.name,
            'survival': f"{self.current_survival:.1f}",
            'competition': f"{self.current_competition:.1f}",
            'strategy': f"{self.current_strategy:.1f}",
            'settings': {
                'survival_base': self.survival_base,
                'competition_base': self.competition_base,
                'hp_sensitivity': self.hp_sensitivity,
                'rank_sensitivity': self.rank_sensitivity,
                'safety_weight': self.safety_weight,
                'attack_weight': self.attack_weight,
            }
        }


class SSDParameterTester:
    """SSDパラメータのA/Bテスト・最適化"""
    
    def __init__(self):
        self.test_results = []
        
    def run_comparison_test(self, configs: List[Dict[str, float]], 
                          test_situations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """複数の設定を同じ状況でテスト"""
        
        results = {
            'configurations': [],
            'situation_results': [],
            'summary': {}
        }
        
        # 各設定でプレイヤーを作成
        players = []
        for i, config in enumerate(configs):
            player = SimpleSSDPlayer(f"Config{i+1}")
            # 設定を適用
            for key, value in config.items():
                if hasattr(player, key):
                    setattr(player, key, value)
            players.append(player)
            results['configurations'].append(config)
        
        # 各状況でテスト
        for situation in test_situations:
            situation_result = {
                'situation': situation,
                'choices': {},
                'choice_distribution': {}
            }
            
            choices = []
            for player in players:
                player.reset_state()
                player.update_from_situation(
                    situation['hp'], 
                    situation['rank'], 
                    situation['score_gap']
                )
                choice = player.make_choice()
                situation_result['choices'][player.name] = choice
                choices.append(choice)
                
            # 統計情報
            situation_result['choice_distribution'] = {
                'mean': np.mean(choices),
                'std': np.std(choices),
                'min': min(choices), 
                'max': max(choices),
                'choices': choices
            }
            
            results['situation_results'].append(situation_result)
        
        # 全体サマリー
        all_choices = []
        for sr in results['situation_results']:
            all_choices.extend(sr['choice_distribution']['choices'])
        
        results['summary'] = {
            'total_choices': len(all_choices),
            'overall_mean': np.mean(all_choices),
            'overall_std': np.std(all_choices),
            'choice_range': f"{min(all_choices)}-{max(all_choices)}",
            'variance_score': np.std(all_choices)  # 高い方が多様性あり
        }
        
        return results
    
    def find_balanced_config(self, target_choice_range: Tuple[int, int] = (2, 8),
                           max_attempts: int = 100) -> Dict[str, float]:
        """バランスの取れた設定を探索"""
        
        test_situations = [
            {"hp": 4, "rank": 2, "score_gap": 20},   # 安全
            {"hp": 2, "rank": 4, "score_gap": 60},   # 中危険  
            {"hp": 1, "rank": 6, "score_gap": 100},  # 高危険
        ]
        
        best_config = None
        best_score = float('inf')
        
        for attempt in range(max_attempts):
            # ランダム設定生成
            config = {
                'survival_base': np.random.uniform(3, 8),
                'competition_base': np.random.uniform(3, 8),
                'hp_sensitivity': np.random.uniform(5, 10),
                'rank_sensitivity': np.random.uniform(5, 10),
                'safety_weight': np.random.uniform(3, 8),
                'attack_weight': np.random.uniform(3, 8),
            }
            
            # テスト実行
            result = self.run_comparison_test([config], test_situations)
            
            # スコア計算（目標範囲からの距離）
            choices = []
            for sr in result['situation_results']:
                choices.extend(sr['choice_distribution']['choices'])
            
            # 範囲チェック
            in_range = all(target_choice_range[0] <= c <= target_choice_range[1] for c in choices)
            diversity = np.std(choices)  # 多様性重視
            
            if in_range:
                score = -diversity  # 多様性が高いほど良い（負の値なので小さい方が良い）
                if score < best_score:
                    best_score = score
                    best_config = config
                    print(f"Attempt {attempt}: New best config (diversity={diversity:.2f})")
        
        return best_config or config  # 見つからなければ最後の設定


def interactive_tuning_demo():
    """インタラクティブ調整デモ"""
    print("="*70)
    print("🎛️  SSD Interactive Parameter Tuning Demo")
    print("="*70)
    
    # テスト状況の定義
    test_situations = [
        {"name": "序盤安全", "hp": 4, "rank": 2, "score_gap": 20},
        {"name": "中盤危機", "hp": 2, "rank": 4, "score_gap": 80},
        {"name": "終盤絶望", "hp": 1, "rank": 6, "score_gap": 150},
        {"name": "僅差競争", "hp": 3, "rank": 2, "score_gap": 5},
    ]
    
    # A/Bテスト用の設定
    config_a = {  # 安全重視型
        'survival_base': 7.0,
        'competition_base': 4.0,
        'hp_sensitivity': 8.0,
        'rank_sensitivity': 5.0,
        'safety_weight': 7.0,
        'attack_weight': 3.0,
    }
    
    config_b = {  # バランス型
        'survival_base': 5.0,
        'competition_base': 6.0,
        'hp_sensitivity': 6.0,
        'rank_sensitivity': 7.0,
        'safety_weight': 5.0,
        'attack_weight': 5.0,
    }
    
    config_c = {  # 攻撃型
        'survival_base': 3.0,
        'competition_base': 8.0,
        'hp_sensitivity': 4.0,
        'rank_sensitivity': 9.0,
        'safety_weight': 3.0,
        'attack_weight': 7.0,
    }
    
    # A/B/Cテスト実行
    tester = SSDParameterTester()
    result = tester.run_comparison_test(
        [config_a, config_b, config_c], 
        test_situations
    )
    
    # 結果表示
    print("\n📊 A/B/C Test Results:")
    print(f"{'状況':<10} {'Config1':<8} {'Config2':<8} {'Config3':<8} {'平均':<8} {'分散':<8}")
    print("-" * 60)
    
    for sr in result['situation_results']:
        choices = sr['choice_distribution']['choices']
        print(f"{sr['situation']['name']:<10} "
              f"{choices[0]:<8} {choices[1]:<8} {choices[2]:<8} "
              f"{sr['choice_distribution']['mean']:<8.1f} "
              f"{sr['choice_distribution']['std']:<8.2f}")
    
    print(f"\n🎯 Overall Summary:")
    print(f"  Choice Range: {result['summary']['choice_range']}")
    print(f"  Mean Choice: {result['summary']['overall_mean']:.2f}")
    print(f"  Diversity Score: {result['summary']['overall_std']:.2f}")
    
    # 自動最適化デモ
    print(f"\n🔍 Auto-Optimization Demo:")
    print("Finding balanced configuration...")
    
    optimal_config = tester.find_balanced_config(target_choice_range=(2, 8), max_attempts=50)
    
    if optimal_config:
        print(f"✅ Found optimal config:")
        for key, value in optimal_config.items():
            print(f"  {key}: {value:.2f}")
        
        # 最適設定をテスト
        optimal_result = tester.run_comparison_test([optimal_config], test_situations)
        print(f"\n📈 Optimal Config Results:")
        for sr in optimal_result['situation_results']:
            choice = sr['choice_distribution']['choices'][0]
            print(f"  {sr['situation']['name']}: Choice {choice}")
    else:
        print("❌ Could not find optimal config within attempts")


if __name__ == "__main__":
    interactive_tuning_demo()