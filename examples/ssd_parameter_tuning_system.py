"""
SSD Parameter Tuning Analysis - SSDパラメータ調整の課題

現在のSSD実装の問題点:
1. パラメータが各ファイル・クラスに分散
2. 影響度が分からない（κ=100の意味は？）
3. 調整結果の可視化が困難
4. A/Bテストができない

理想的な調整可能構造:
1. 中央集約的パラメータ管理
2. 直感的な数値範囲（0-1, 0-10等）
3. リアルタイム調整・可視化
4. 自動最適化機能
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable
import json
from pathlib import Path

@dataclass 
class SSDParameterConfig:
    """SSD全体のパラメータを一元管理"""
    
    # ===== 直感的パラメータ（0-10スケール） =====
    # 個体差パラメータ
    survival_sensitivity: float = 5.0      # 0=鈍感 10=過敏
    competition_drive: float = 5.0         # 0=無関心 10=闘争心
    strategic_thinking: float = 5.0        # 0=直感的 10=計算的
    risk_tolerance: float = 5.0            # 0=超慎重 10=無謀
    
    # 状況感度パラメータ  
    hp_pressure_scaling: float = 5.0       # HP減少の意味圧倍率
    rank_pressure_scaling: float = 5.0     # 順位の意味圧倍率
    time_pressure_scaling: float = 5.0     # 時間切迫の意味圧倍率
    
    # エンジンパラメータ
    energy_generation_rate: float = 5.0    # E値生成速度
    kappa_learning_rate: float = 5.0       # κ学習速度
    leap_threshold_sensitivity: float = 5.0 # 跳躍しやすさ
    
    # 行動創発パラメータ
    safety_influence_weight: float = 5.0   # 安全志向の影響度
    attack_influence_weight: float = 5.0   # 攻撃志向の影響度
    strategic_influence_weight: float = 5.0 # 戦略の影響度
    
    def to_internal_params(self) -> Dict[str, Any]:
        """直感的パラメータを内部パラメータに変換"""
        return {
            # κ値（0-10 → 適切な内部値に変換）
            'kappa_base': self._scale_to_range(self.survival_sensitivity, 5.0, 50.0),
            'kappa_core': self._scale_to_range(self.competition_drive, 1.0, 10.0), 
            'kappa_upper': self._scale_to_range(self.strategic_thinking, 3.0, 20.0),
            
            # 意味圧スケール
            'hp_pressure_multiplier': self._scale_to_range(self.hp_pressure_scaling, 50.0, 500.0),
            'rank_pressure_multiplier': self._scale_to_range(self.rank_pressure_scaling, 10.0, 100.0),
            
            # 創発係数
            'safety_coefficient': self._scale_to_range(self.safety_influence_weight, 0.05, 0.5),
            'attack_coefficient': self._scale_to_range(self.attack_influence_weight, 0.01, 0.2),
            'strategic_coefficient': self._scale_to_range(self.strategic_influence_weight, 0.02, 0.3),
        }
    
    def _scale_to_range(self, value: float, min_val: float, max_val: float) -> float:
        """0-10の値を指定範囲にスケール"""
        normalized = value / 10.0  # 0-1に正規化
        return min_val + normalized * (max_val - min_val)
    
    def save(self, filepath: str):
        """パラメータをJSONファイルに保存"""
        config_dict = {
            'survival_sensitivity': self.survival_sensitivity,
            'competition_drive': self.competition_drive,
            'strategic_thinking': self.strategic_thinking,
            'risk_tolerance': self.risk_tolerance,
            'hp_pressure_scaling': self.hp_pressure_scaling,
            'rank_pressure_scaling': self.rank_pressure_scaling,
            'time_pressure_scaling': self.time_pressure_scaling,
            'energy_generation_rate': self.energy_generation_rate,
            'kappa_learning_rate': self.kappa_learning_rate,
            'leap_threshold_sensitivity': self.leap_threshold_sensitivity,
            'safety_influence_weight': self.safety_influence_weight,
            'attack_influence_weight': self.attack_influence_weight,
            'strategic_influence_weight': self.strategic_influence_weight,
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, filepath: str) -> 'SSDParameterConfig':
        """JSONファイルからパラメータを読み込み"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls(**config_dict)


class SSDParameterTuner:
    """SSDパラメータの調整・実験支援"""
    
    def __init__(self, base_config: SSDParameterConfig):
        self.base_config = base_config
        self.experiment_results = []
        
    def create_variant(self, **adjustments) -> SSDParameterConfig:
        """基本設定から変更版を作成"""
        config_dict = {
            'survival_sensitivity': self.base_config.survival_sensitivity,
            'competition_drive': self.base_config.competition_drive,
            'strategic_thinking': self.base_config.strategic_thinking,
            'risk_tolerance': self.base_config.risk_tolerance,
            'hp_pressure_scaling': self.base_config.hp_pressure_scaling,
            'rank_pressure_scaling': self.base_config.rank_pressure_scaling,
            'time_pressure_scaling': self.base_config.time_pressure_scaling,
            'energy_generation_rate': self.base_config.energy_generation_rate,
            'kappa_learning_rate': self.base_config.kappa_learning_rate,
            'leap_threshold_sensitivity': self.base_config.leap_threshold_sensitivity,
            'safety_influence_weight': self.base_config.safety_influence_weight,
            'attack_influence_weight': self.base_config.attack_influence_weight,
            'strategic_influence_weight': self.base_config.strategic_influence_weight,
        }
        
        # 調整値を適用
        config_dict.update(adjustments)
        return SSDParameterConfig(**config_dict)
    
    def run_parameter_sweep(self, param_name: str, values: list, 
                          test_function: Callable) -> Dict[float, Any]:
        """パラメータ値を変化させてテスト実行"""
        results = {}
        
        for value in values:
            print(f"Testing {param_name}={value}...")
            variant = self.create_variant(**{param_name: value})
            result = test_function(variant)
            results[value] = result
            
        return results
    
    def find_optimal_balance(self, target_metrics: Dict[str, float],
                           test_function: Callable, max_iterations: int = 20) -> SSDParameterConfig:
        """目標メトリクスに最も近いパラメータ組み合わせを探索"""
        best_config = self.base_config
        best_score = float('inf')
        
        for i in range(max_iterations):
            # ランダムな調整を生成
            adjustments = {
                'survival_sensitivity': np.random.uniform(0, 10),
                'competition_drive': np.random.uniform(0, 10),
                'strategic_thinking': np.random.uniform(0, 10),
                'safety_influence_weight': np.random.uniform(0, 10),
                'attack_influence_weight': np.random.uniform(0, 10),
            }
            
            candidate = self.create_variant(**adjustments)
            result = test_function(candidate)
            
            # スコア計算（目標からの距離）
            score = sum((result.get(key, 0) - target_value) ** 2 
                       for key, target_value in target_metrics.items())
            
            if score < best_score:
                best_score = score
                best_config = candidate
                print(f"Iteration {i}: New best score {score:.3f}")
                
        return best_config


# ===== 調整しやすいApex Player実装 =====

class TunableApexPlayer:
    """パラメータ調整しやすいApex Survivorプレイヤー"""
    
    def __init__(self, name: str, config: SSDParameterConfig):
        self.name = name
        self.config = config
        self.internal_params = config.to_internal_params()
        
        # 動的な内部状態（簡略版）
        self.E_base = 40.0
        self.E_core = 0.5  
        self.E_upper = 4.0
        
        # κ値を設定から取得
        self.kappa_base = self.internal_params['kappa_base']
        self.kappa_core = self.internal_params['kappa_core']
        self.kappa_upper = self.internal_params['kappa_upper']
        
        self.hp = 3
        self.score = 0
        
    def make_choice(self, situation: Dict[str, Any]) -> int:
        """調整可能なパラメータによる選択"""
        
        # ===== 意味圧計算（設定から） =====
        hp_pressure = self._calculate_hp_pressure(situation['hp'])
        rank_pressure = self._calculate_rank_pressure(situation['rank'], situation['score_gap'])
        
        # E値を更新（簡略版）
        self.E_base += hp_pressure * 0.1
        self.E_core += rank_pressure * 0.1
        self.E_upper += (hp_pressure + rank_pressure) * 0.05
        
        # ===== 創発計算（設定から） =====
        safety_drive = max(0, self.E_base - self.kappa_base)
        attack_drive = max(0, self.E_core - self.kappa_core) 
        strategic_drive = max(0, self.E_upper - self.kappa_upper)
        
        # 基準選択値
        base_choice = 5.0
        
        # 各要素の寄与（係数は設定から）
        safety_effect = -safety_drive * self.internal_params['safety_coefficient']
        attack_effect = attack_drive * self.internal_params['attack_coefficient']  
        strategic_effect = strategic_drive * self.internal_params['strategic_coefficient']
        
        final_choice = base_choice + safety_effect + attack_effect + strategic_effect
        
        return max(1, min(10, int(final_choice + 0.5)))
    
    def _calculate_hp_pressure(self, hp: int) -> float:
        """HP状況から意味圧を計算"""
        hp_threat = max(0, (5 - hp) / 4)  # 0-1の脅威度
        return hp_threat * self.internal_params['hp_pressure_multiplier']
    
    def _calculate_rank_pressure(self, rank: int, score_gap: int) -> float:
        """順位状況から意味圧を計算"""
        rank_threat = max(0, (rank - 1) / 6)  # 0-1の脅威度
        gap_threat = min(1.0, score_gap / 200)  # 0-1の脅威度
        total_threat = (rank_threat + gap_threat) / 2
        return total_threat * self.internal_params['rank_pressure_multiplier']
    
    def get_debug_info(self) -> Dict[str, Any]:
        """デバッグ情報を返す"""
        return {
            'E_values': [self.E_base, self.E_core, self.E_upper],
            'kappa_values': [self.kappa_base, self.kappa_core, self.kappa_upper],
            'internal_params': self.internal_params,
            'config_summary': {
                'survival_sensitivity': self.config.survival_sensitivity,
                'competition_drive': self.config.competition_drive,
                'strategic_thinking': self.config.strategic_thinking,
            }
        }


def demo_parameter_tuning():
    """パラメータ調整デモ"""
    print("="*60)
    print("🔧 SSD Parameter Tuning Demo")
    print("="*60)
    
    # ベース設定（全て5.0 = 中間値）
    base_config = SSDParameterConfig()
    
    # 異なる個性の設定を作成
    cautious_config = SSDParameterConfig(
        survival_sensitivity=8.0,  # 高い生存感度
        competition_drive=3.0,     # 低い競争心
        strategic_thinking=7.0,    # 高い戦略性
        safety_influence_weight=8.0,  # 安全重視
        attack_influence_weight=2.0   # 攻撃性低
    )
    
    aggressive_config = SSDParameterConfig(
        survival_sensitivity=3.0,  # 低い生存感度
        competition_drive=8.0,     # 高い競争心
        strategic_thinking=4.0,    # 中程度の戦略性
        safety_influence_weight=2.0,  # 安全軽視
        attack_influence_weight=8.0   # 高攻撃性
    )
    
    # プレイヤー作成
    players = [
        TunableApexPlayer("バランス型", base_config),
        TunableApexPlayer("慎重型", cautious_config), 
        TunableApexPlayer("攻撃型", aggressive_config)
    ]
    
    # テスト状況
    test_situations = [
        {"name": "安全状況", "hp": 4, "rank": 2, "score_gap": 20},
        {"name": "危険状況", "hp": 1, "rank": 5, "score_gap": 100},
        {"name": "競争状況", "hp": 3, "rank": 2, "score_gap": 5}
    ]
    
    for situation in test_situations:
        print(f"\n【{situation['name']}】HP:{situation['hp']}, 順位:{situation['rank']}, 差:{situation['score_gap']}")
        
        for player in players:
            choice = player.make_choice(situation)
            debug = player.get_debug_info()
            
            print(f"  {player.name}: 選択={choice}")
            print(f"    設定: 生存感度={player.config.survival_sensitivity:.1f}, 競争心={player.config.competition_drive:.1f}, 戦略性={player.config.strategic_thinking:.1f}")
            print(f"    内部: κ=[{debug['kappa_values'][0]:.1f},{debug['kappa_values'][1]:.1f},{debug['kappa_values'][2]:.1f}]")
    
    # 設定保存の例
    base_config.save("ssd_config_base.json")
    cautious_config.save("ssd_config_cautious.json") 
    aggressive_config.save("ssd_config_aggressive.json")
    print(f"\n💾 設定ファイルを保存しました")


if __name__ == "__main__":
    demo_parameter_tuning()