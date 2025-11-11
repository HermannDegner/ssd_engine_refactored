"""
【APEX SURVIVOR - Thermal Edition v1】

v3をベースに熱力学的効果を統合:
- 心理的興奮度に応じた「体温」変化
- 熱ノイズによる決断の揺らぎ
- 興奮状態（高温）での衝動的行動
- 冷静状態（低温）での慎重な判断

熱力学的解釈:
- 体温 = 心理的興奮度（死の恐怖、勝利欲求、競争圧）
- 熱ノイズ = 感情の揺らぎ、直感的判断
- 温度上昇 = ストレス、危機感、競争激化
- 温度低下 = 冷静、計算的、理性的判断
"""

import sys
from pathlib import Path
import random
import numpy as np

# パス設定
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from core import HumanAgent, HumanParams, HumanPressure, HumanLayer
from core.ssd_core_engine import SSDCoreEngine, SSDCoreParams, create_default_state


# ===== 熱力学的SSDエンジンの統合 =====
class ThermalSSDEngine(SSDCoreEngine):
    """熱力学的SSDエンジン（apex_survivor用に適応）"""
    
    def step(self, state, pressure, dt=0.1, interlayer_transfer=None):
        """熱力学的ステップ実行"""
        # 配列化
        R_array = np.array(self.params.R_values)
        gamma_array = np.array(self.params.gamma_values)
        beta_array = np.array(self.params.beta_values)
        eta_array = np.array(self.params.eta_values)
        lambda_array = np.array(self.params.lambda_values)
        kappa_min_array = np.array(self.params.kappa_min_values)
        
        # 新状態作成
        new_state = create_default_state(self.num_layers)
        new_state.t = state.t + dt
        new_state.step_count = state.step_count + 1
        
        # Log-Alignment適用（必要に応じて）
        if self.params.log_align:
            pressure_hat = self.apply_log_alignment(state, pressure)
        else:
            pressure_hat = pressure
        
        # 【物理修正】正しいオームの法則: j = p̂ / R
        j = pressure_hat / R_array
        
        # エネルギー残差計算
        resid = np.maximum(0.0, np.abs(pressure_hat) - np.abs(j))
        
        # 【熱力学追加】熱ノイズによるエネルギー揺らぎ
        thermal_noise = np.random.normal(0, self.params.temperature_T * 0.1, self.num_layers)
        
        # エネルギー生成（熱ノイズ込み）
        energy_generation = gamma_array * resid + thermal_noise
        
        # エネルギー減衰
        energy_decay = beta_array * state.E
        
        # エネルギー更新
        dE = energy_generation - energy_decay
        
        if interlayer_transfer is not None:
            dE += interlayer_transfer
        
        new_state.E = np.maximum(0.0, state.E + dE * dt)
        
        # κ更新
        usage_factor = np.abs(j) / (np.abs(j) + 1.0)
        dkappa = eta_array * usage_factor - lambda_array * state.kappa
        new_state.kappa = np.maximum(kappa_min_array, state.kappa + dkappa * dt)
        
        return new_state


class ThermalHumanAgent(HumanAgent):
    """熱力学効果を持つHumanAgent"""
    
    def __init__(self, params=None, agent_id="ThermalAgent", enable_nonlinear_transfer=True):
        super().__init__(params, agent_id, enable_nonlinear_transfer)
        self.base_temperature = 37.0  # 人体基準温度
        self.current_temperature = self.base_temperature
        self.temperature_history = []
        
        # 熱力学的SSDエンジンに置き換え
        thermal_params = SSDCoreParams()
        thermal_params.enable_stochastic_leap = True
        thermal_params.temperature_T = self.current_temperature
        thermal_params.Theta_values = [100.0, 80.0, 60.0, 40.0]  # 人体体温スケール
        thermal_params.gamma_values = [1.0, 0.8, 0.6, 0.4]
        thermal_params.beta_values = [0.1, 0.15, 0.2, 0.25]
        thermal_params.G0 = 0.001  # 現実的基底導電率
        thermal_params.g = 0.01   # 現実的ゲイン
        
        self.core_engine = ThermalSSDEngine(thermal_params)
    
    def update_temperature(self, pressure_intensity: float, stress_level: float = 0.0):
        """心理状態に基づく体温更新
        
        Args:
            pressure_intensity: 意味圧の強度（0-1000）
            stress_level: ストレスレベル（0-1.0）
        """
        # 基本体温からの変動計算
        pressure_factor = np.clip(pressure_intensity / 500.0, 0.0, 2.0)  # 0-2倍
        stress_factor = stress_level * 4.0  # 最大+4度
        
        # 体温更新（35-42度の範囲）
        target_temp = self.base_temperature + pressure_factor + stress_factor
        self.current_temperature = np.clip(target_temp, 35.0, 42.0)
        
        # SSDエンジンの温度も更新
        self.core_engine.params.temperature_T = self.current_temperature
        
        # 履歴記録
        self.temperature_history.append(self.current_temperature)
        
        return self.current_temperature
    
    def get_thermal_state(self) -> dict:
        """熱状態の取得"""
        temp_category = "normal"
        if self.current_temperature < 36.0:
            temp_category = "hypothermia"
        elif self.current_temperature < 37.0:
            temp_category = "cool"
        elif self.current_temperature > 39.0:
            temp_category = "fever"
        elif self.current_temperature > 37.5:
            temp_category = "warm"
        
        return {
            'temperature': self.current_temperature,
            'base_temperature': self.base_temperature,
            'delta': self.current_temperature - self.base_temperature,
            'category': temp_category,
            'thermal_noise_level': self.current_temperature * 0.1
        }


# ===== ゲーム設定 =====
class GameConfig:
    """APEX SURVIVOR ゲームルール"""
    CHOICES = {
        1: {'score': 10, 'crash_rate': 0.05},
        2: {'score': 20, 'crash_rate': 0.10},
        3: {'score': 30, 'crash_rate': 0.15},
        4: {'score': 40, 'crash_rate': 0.20},
        5: {'score': 50, 'crash_rate': 0.25},
        6: {'score': 60, 'crash_rate': 0.35},
        7: {'score': 70, 'crash_rate': 0.45},
        8: {'score': 80, 'crash_rate': 0.55},
        9: {'score': 90, 'crash_rate': 0.65},
        10: {'score': 100, 'crash_rate': 0.75}
    }
    
    STARTING_HP = 3
    MAX_HP = 5
    HP_PURCHASE_COST = 20
    
    ROUNDS_PER_SET = 5
    TOTAL_SETS = 5
    
    # セット順位ボーナス
    SET_RANK_BONUS = {
        1: 50,   # 1位: +50pts
        2: 30,   # 2位: +30pts
        3: 15,   # 3位: +15pts
    }


# ===== プレイヤークラス（熱力学版） =====
class ApexPlayerThermal:
    """APEX SURVIVOR プレイヤー（熱力学版）"""
    
    def __init__(self, name: str, personality: str, color: str):
        self.name = name
        self.personality = personality
        self.color = color
        
        # ゲーム状態
        self.hp = GameConfig.STARTING_HP
        self.score = 0
        self.total_score = 0
        self.is_alive = True
        self.choice_history = []
        self.crash_history = []
        
        # 脱落情報
        self.elimination_set = None
        self.elimination_round = None
        
        # 熱力学的HumanAgent
        params = HumanParams()
        self.agent = ThermalHumanAgent(params=params, agent_id=f"Thermal_{self.name}", 
                                      enable_nonlinear_transfer=True)
        self._initialize_personality()
    
    def _initialize_personality(self):
        """性格別κ初期化（熱力学版）"""
        if self.personality == 'cautious':
            # 慎重派: 低体温傾向、死の恐怖が強い
            self.agent.base_temperature = 36.5  # やや低めの基準体温
            self.agent.current_temperature = 36.5
            self.agent.state.kappa[HumanLayer.BASE.value] = 100.0  # 死の恐怖
            self.agent.state.kappa[HumanLayer.CORE.value] = 0.3    # 控えめな勝利欲求
            self.agent.state.kappa[HumanLayer.UPPER.value] = 15.0  # 戦略思考
        elif self.personality == 'aggressive':
            # 攻撃派: 高体温傾向、勝利への執着
            self.agent.base_temperature = 37.5  # やや高めの基準体温
            self.agent.current_temperature = 37.5
            self.agent.state.kappa[HumanLayer.BASE.value] = 150.0  # 死の恐怖（標準）
            self.agent.state.kappa[HumanLayer.CORE.value] = 2.0    # 強い勝利欲求
            self.agent.state.kappa[HumanLayer.UPPER.value] = 12.0  # 戦略思考
        else:  # balanced
            # バランス派: 標準体温、バランス型
            self.agent.base_temperature = 37.0  # 標準体温
            self.agent.current_temperature = 37.0
            self.agent.state.kappa[HumanLayer.BASE.value] = 120.0  # 死の恐怖（中間）
            self.agent.state.kappa[HumanLayer.CORE.value] = 0.5    # 標準勝利欲求
            self.agent.state.kappa[HumanLayer.UPPER.value] = 13.0  # 戦略思考
        
        # 【初期熱設定】体温に応じたE値
        temp_factor = self.agent.current_temperature / 37.0
        if self.personality == 'cautious':
            self.agent.state.E[HumanLayer.BASE.value] = 50.0 * temp_factor
            self.agent.state.E[HumanLayer.CORE.value] = 0.1 * temp_factor
            self.agent.state.E[HumanLayer.UPPER.value] = 3.0 * temp_factor
        elif self.personality == 'aggressive':
            self.agent.state.E[HumanLayer.BASE.value] = 30.0 * temp_factor
            self.agent.state.E[HumanLayer.CORE.value] = 1.0 * temp_factor
            self.agent.state.E[HumanLayer.UPPER.value] = 5.0 * temp_factor
        else:  # balanced
            self.agent.state.E[HumanLayer.BASE.value] = 40.0 * temp_factor
            self.agent.state.E[HumanLayer.CORE.value] = 0.3 * temp_factor
            self.agent.state.E[HumanLayer.UPPER.value] = 4.0 * temp_factor
    
    def make_choice(self, current_rank: int, leader_score: int, round_num: int, 
                    total_rounds: int, alive_count: int, current_set: int, total_sets: int,
                    opponents_info: list = None) -> int:
        """熱力学的選択決定"""
        
        # 【Step 1: 状況認識と体温更新】
        situation_stress = self._assess_situation_stress(current_rank, leader_score, 
                                                        alive_count, current_set, total_sets)
        pressure_intensity = self._calculate_pressure_intensity(current_rank, leader_score, 
                                                               round_num, total_rounds)
        
        # 体温更新（心理状態を体温に反映）
        self.agent.update_temperature(pressure_intensity, situation_stress)
        thermal_state = self.agent.get_thermal_state()
        
        # 【Step 2: 状況を意味圧に変換】
        pressure = self._calculate_layered_pressure(current_rank, leader_score, round_num, 
                                                   total_rounds, alive_count, current_set, 
                                                   total_sets, opponents_info)
        
        # 【Step 3: HumanAgent実行（熱ノイズ込み）】
        updated_state = self.agent.step(pressure)
        
        # 【Step 4: E/κバランスから選択を創発（熱効果込み）】
        raw_choice = self._calculate_choice_from_state(updated_state)
        game_choice = self._convert_to_game_choice(raw_choice, thermal_state)
        
        # 選択履歴に記録
        self.choice_history.append({
            'choice': game_choice,
            'raw_choice': raw_choice,
            'temperature': thermal_state['temperature'],
            'thermal_category': thermal_state['category'],
            'situation_stress': situation_stress,
            'pressure_intensity': pressure_intensity,
            'E_state': self.agent.state.E.copy(),
            'kappa_state': self.agent.state.kappa.copy()
        })
        
        return game_choice
    
    def _assess_situation_stress(self, current_rank: int, leader_score: int, 
                                alive_count: int, current_set: int, total_sets: int) -> float:
        """状況ストレス評価（0-1.0）"""
        stress_factors = []
        
        # 順位によるストレス
        if current_rank == 1:
            stress_factors.append(0.1)  # 1位は余裕
        elif current_rank <= alive_count // 2:
            stress_factors.append(0.3)  # 上位は中程度
        else:
            stress_factors.append(0.8)  # 下位は高ストレス
        
        # HP残量によるストレス
        hp_stress = (GameConfig.STARTING_HP - self.hp) / GameConfig.STARTING_HP
        stress_factors.append(hp_stress * 0.5)
        
        # ゲーム進行によるストレス
        game_progress = (current_set - 1) / total_sets
        stress_factors.append(game_progress * 0.3)
        
        # 生存者数によるストレス
        survival_stress = (4 - alive_count) / 3  # 生存者減少でストレス増
        stress_factors.append(survival_stress * 0.4)
        
        return min(1.0, sum(stress_factors))
    
    def _calculate_pressure_intensity(self, current_rank: int, leader_score: int,
                                     round_num: int, total_rounds: int) -> float:
        """意味圧強度計算（0-1000）"""
        intensity_factors = []
        
        # 順位圧（低順位ほど高圧）
        rank_pressure = (4 - current_rank + 1) * 100  # 200-500
        intensity_factors.append(rank_pressure)
        
        # スコア差圧
        score_gap = max(0, leader_score - self.score)
        score_pressure = min(300, score_gap * 2)  # 最大300
        intensity_factors.append(score_pressure)
        
        # HP危機圧
        if self.hp == 1:
            intensity_factors.append(400)  # 死の危機
        elif self.hp == 2:
            intensity_factors.append(200)  # 危険域
        
        # 時間圧（終盤ほど高圧）
        time_pressure = (round_num / total_rounds) * 150
        intensity_factors.append(time_pressure)
        
        return sum(intensity_factors)
    
    def _calculate_choice_from_state(self, state) -> float:
        """E/κバランスから選択値を計算（v3ロジックを参考）"""
        # E/κ比率を計算（行動指向性）
        E_BASE = state.E[HumanLayer.BASE.value]
        E_CORE = state.E[HumanLayer.CORE.value] 
        E_UPPER = state.E[HumanLayer.UPPER.value]
        
        kappa_BASE = state.kappa[HumanLayer.BASE.value]
        kappa_CORE = state.kappa[HumanLayer.CORE.value]
        kappa_UPPER = state.kappa[HumanLayer.UPPER.value]
        
        # E > κ の層は「行動要求」、E < κ の層は「行動抑制」
        action_BASE = (E_BASE / kappa_BASE) if kappa_BASE > 0 else 0
        action_CORE = (E_CORE / kappa_CORE) if kappa_CORE > 0 else 0
        action_UPPER = (E_UPPER / kappa_UPPER) if kappa_UPPER > 0 else 0
        
        # 性格別の解釈フィルター（v3と同様）
        if self.personality == 'cautious':
            # 慎重派: 生存本能（BASE）が選択を支配
            safety_drive = action_BASE * 2.0 - action_CORE * 0.5
            if action_UPPER > 3.0:
                choice_value = 1.5 + action_UPPER * 0.3  # 戦略主導
            elif safety_drive > 5.0:
                choice_value = 1.0  # 極度に慎重
            else:
                choice_value = 3.0 + action_BASE * 0.8
                
        elif self.personality == 'aggressive':
            # 攻撃派: 勝利欲求（CORE）が選択を牽引
            victory_drive = action_CORE * 3.0 - action_BASE * 0.3
            if victory_drive > 8.0:
                choice_value = 8.0 + action_CORE * 0.5  # 勝利への執着
            elif action_BASE > 5.0:
                choice_value = 4.0 + action_BASE * 0.6  # 生存も考慮
            else:
                choice_value = 6.0 + action_CORE * 0.4
                
        else:  # balanced
            # バランス派: 各層のバランスを取る
            total_action = action_BASE + action_CORE + action_UPPER
            if total_action > 12.0:
                choice_value = 7.0 + (total_action - 12.0) * 0.3
            elif action_BASE > 8.0:
                choice_value = 2.0 + action_BASE * 0.4
            else:
                choice_value = 5.0 + (action_CORE + action_UPPER) * 0.3
        
        return np.clip(choice_value, 1.0, 10.0)
    
    def _calculate_layered_pressure(self, current_rank: int, leader_score: int, round_num: int,
                                   total_rounds: int, alive_count: int, current_set: int,
                                   total_sets: int, opponents_info: list = None) -> HumanPressure:
        """層別意味圧計算（熱力学版）"""
        pressure = HumanPressure()
        
        # BASE層: 生存本能（死の恐怖）
        if self.hp == 1:
            pressure.base += 800  # 即死の恐怖（熱で増幅）
        elif self.hp == 2:
            pressure.base += 400  # 危険域の恐怖
        else:
            pressure.base += 100  # 基本的生存意識
        
        # CORE層: 勝利欲求と競争心
        score_gap = max(0, leader_score - self.score)
        if current_rank == 1:
            pressure.core += 50   # 維持欲求
        else:
            pressure.core += min(300, score_gap)  # 追い上げ欲求
        
        # UPPER層: 戦略的判断
        # 終盤ほど戦略的思考が重要
        strategic_weight = (round_num / total_rounds) * 200
        pressure.upper += strategic_weight
        
        # 生存者数による競争圧（少ないほど激化）
        competition_pressure = (4 - alive_count) * 50
        pressure.core += competition_pressure
        
        return pressure
    
    def _convert_to_game_choice(self, raw_choice: float, thermal_state: dict) -> int:
        """選択値をゲーム選択肢に変換（熱効果込み）"""
        # 熱による選択変動
        temp_delta = thermal_state['delta']  # 基準体温からの差
        thermal_noise = thermal_state['thermal_noise_level']
        
        # 高温時: より極端な選択（リスクテイクまたは極度の慎重）
        # 低温時: より冷静で計算的な選択
        
        if thermal_state['category'] == 'fever':
            # 発熱時: 衝動的、極端な選択
            if raw_choice > 5.0:
                raw_choice += random.uniform(0.5, 2.0)  # リスク増大
            else:
                raw_choice -= random.uniform(0.5, 1.5)  # 極度に慎重
        elif thermal_state['category'] == 'warm':
            # 微熱時: やや衝動的
            raw_choice += random.uniform(-0.5, 1.0)
        elif thermal_state['category'] == 'cool':
            # 低体温時: 冷静で計算的
            raw_choice += random.uniform(-0.3, 0.3)  # 安定した判断
        
        # 熱ノイズによるランダム変動
        thermal_variation = np.random.normal(0, thermal_noise * 0.1)
        raw_choice += thermal_variation
        
        # 1-10の範囲にクリップ
        game_choice = int(np.clip(round(raw_choice), 1, 10))
        
        return game_choice
    
    def take_damage(self):
        """ダメージ処理（熱反応込み）"""
        if self.hp > 0:
            self.hp -= 1
            if self.hp <= 0:
                self.is_alive = False
            else:
                # ダメージによる体温上昇（ストレス反応）
                stress_temp_rise = random.uniform(0.5, 1.5)
                new_temp = min(42.0, self.agent.current_temperature + stress_temp_rise)
                self.agent.current_temperature = new_temp
                self.agent.core_engine.params.temperature_T = new_temp
    
    def get_display_info(self) -> str:
        """表示用情報（熱状態込み）"""
        thermal_state = self.agent.get_thermal_state()
        temp_icon = "🌡️"
        if thermal_state['category'] == 'fever':
            temp_icon = "🔥"
        elif thermal_state['category'] == 'warm':
            temp_icon = "🌡️"
        elif thermal_state['category'] == 'cool':
            temp_icon = "❄️"
        
        return (f"{self.color}{self.name}{temp_icon} "
               f"(HP:{self.hp} Score:{self.score} "
               f"Temp:{thermal_state['temperature']:.1f}°C)")


# ===== ゲーム実行 =====
def run_thermal_apex_survivor():
    """熱力学版APEX SURVIVOR実行"""
    print("🔥🎮" + "="*70)
    print("🔥🎮 APEX SURVIVOR - Thermal Edition")
    print("🔥🎮" + "="*70)
    print("熱力学的SSDシステム:")
    print("• 心理的興奮度 → 体温変化")
    print("• 熱ノイズ → 決断の揺らぎ")
    print("• 高体温 → 衝動的行動")
    print("• 低体温 → 冷静な判断")
    print("="*74)
    
    # プレイヤー作成
    players = [
        ApexPlayerThermal("Alice", "cautious", "🔵"),
        ApexPlayerThermal("Bob", "aggressive", "🔴"),
        ApexPlayerThermal("Charlie", "balanced", "🟢"),
        ApexPlayerThermal("Diana", "aggressive", "🟡")
    ]
    
    # 初期状態表示
    print("\n📊 初期状態:")
    for player in players:
        thermal_state = player.agent.get_thermal_state()
        print(f"{player.get_display_info()} - {player.personality} "
              f"({thermal_state['category']})")
    
    # ゲーム実行
    for set_num in range(1, GameConfig.TOTAL_SETS + 1):
        print(f"\n🎯 === SET {set_num} ===")
        
        alive_players = [p for p in players if p.is_alive]
        if len(alive_players) <= 1:
            break
        
        # ラウンド実行
        for round_num in range(1, GameConfig.ROUNDS_PER_SET + 1):
            print(f"\n--- Round {round_num} ---")
            
            # 各プレイヤーの選択
            round_results = []
            for player in alive_players:
                # 現在の順位とリーダースコア計算
                alive_scores = [(p.name, p.score) for p in alive_players]
                alive_scores.sort(key=lambda x: x[1], reverse=True)
                current_rank = next(i for i, (name, _) in enumerate(alive_scores, 1) if name == player.name)
                leader_score = alive_scores[0][1]
                
                # 相手情報
                opponents_info = [{'name': p.name, 'score': p.score, 'hp': p.hp} 
                                for p in alive_players if p != player]
                
                # 選択実行
                choice = player.make_choice(current_rank, leader_score, round_num, 
                                          GameConfig.ROUNDS_PER_SET, len(alive_players),
                                          set_num, GameConfig.TOTAL_SETS, opponents_info)
                
                # 結果判定
                crash_rate = GameConfig.CHOICES[choice]['crash_rate']
                crashed = random.random() < crash_rate
                score_gain = 0 if crashed else GameConfig.CHOICES[choice]['score']
                
                round_results.append({
                    'player': player,
                    'choice': choice,
                    'crashed': crashed,
                    'score_gain': score_gain,
                    'thermal_state': player.agent.get_thermal_state()
                })
            
            # 結果表示と処理
            for result in round_results:
                player = result['player']
                thermal = result['thermal_state']
                
                print(f"{player.get_display_info()} chose {result['choice']} "
                      f"({thermal['category']} {thermal['temperature']:.1f}°C)")
                
                if result['crashed']:
                    print(f"  💥 CRASHED! HP-1")
                    player.take_damage()
                    player.crash_history.append(round_num)
                    if not player.is_alive:
                        print(f"  ☠️  {player.name} ELIMINATED!")
                        player.elimination_set = set_num
                        player.elimination_round = round_num
                else:
                    player.score += result['score_gain']
                    player.total_score = player.score
                    print(f"  ✅ Success! +{result['score_gain']} points")
            
            # 生存チェック
            alive_players = [p for p in players if p.is_alive]
            if len(alive_players) <= 1:
                break
        
        # セット終了時の順位ボーナス
        if len(alive_players) > 1:
            alive_players.sort(key=lambda p: p.score, reverse=True)
            for rank, player in enumerate(alive_players[:3], 1):
                if rank in GameConfig.SET_RANK_BONUS:
                    bonus = GameConfig.SET_RANK_BONUS[rank]
                    player.score += bonus
                    player.total_score = player.score
                    print(f"🏆 {player.name} Rank {rank}: +{bonus} bonus")
    
    # 最終結果
    print(f"\n🏁 === FINAL RESULTS ===")
    final_ranking = sorted(players, key=lambda p: p.score, reverse=True)
    
    for rank, player in enumerate(final_ranking, 1):
        status = "👑 WINNER" if rank == 1 else "💀 ELIMINATED" if not player.is_alive else "🎯 FINISHED"
        thermal_avg = np.mean(player.agent.temperature_history) if player.agent.temperature_history else player.agent.base_temperature
        
        print(f"{rank}. {player.name} ({player.personality}): {player.score}pts {status}")
        print(f"   💓 Average Temperature: {thermal_avg:.1f}°C")
        print(f"   🎯 Choices: {player.choice_history[-5:] if len(player.choice_history) >= 5 else player.choice_history}")
        
        if player.agent.temperature_history:
            temp_range = f"{min(player.agent.temperature_history):.1f}-{max(player.agent.temperature_history):.1f}°C"
            print(f"   🌡️  Temperature Range: {temp_range}")


if __name__ == "__main__":
    run_thermal_apex_survivor()