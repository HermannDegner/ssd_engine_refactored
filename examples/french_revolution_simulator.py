"""
フランス革命シミュレーター - SSD Engine による歴史的社会変革の分析
====================================================================

1789年のフランス革命を構造主観力学（SSD）理論でモデル化。
社会階層間の対立、革命の勃発、恐怖政治への移行を再現。

シミュレーション内容:
1. 革命前夜（1788-1789）: 三部会と特権階級への不満
2. 革命の勃発（1789）: バスティーユ襲撃、封建制廃止
3. 急進化（1792-1793）: 王政廃止、恐怖政治
4. テルミドールの反動（1794）: ロベスピエール失脚

社会階層:
- 貴族（Nobility）: 特権階級、変化への抵抗
- 聖職者（Clergy）: 宗教的権威、保守的
- ブルジョワジー（Bourgeoisie）: 啓蒙思想、改革派
- サンキュロット（Sans-culottes）: 都市労働者、急進派
- 農民（Peasants）: 圧倒的多数、経済的困窮
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ssd_human_module import HumanAgent, HumanPressure, HumanLayer
from extensions.ssd_social_dynamics import (
    SocialCouplingParams, RelationshipMatrix, SocialDynamicsEngine
)
import numpy as np
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from matplotlib import rcParams
from enum import Enum

# 日本語フォント設定
rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
rcParams['axes.unicode_minus'] = False


class SocialClass(Enum):
    """社会階層"""
    NOBILITY = 0      # 貴族
    CLERGY = 1        # 聖職者
    BOURGEOISIE = 2   # ブルジョワジー
    SANS_CULOTTES = 3 # サンキュロット
    PEASANTS = 4      # 農民


class RevolutionaryAgent(HumanAgent):
    """革命期のエージェント（拡張版）"""
    
    def __init__(self, social_class: SocialClass, agent_id: int):
        super().__init__()
        self.social_class = social_class
        self.agent_id = agent_id
        self.is_alive = True
        self.revolutionary_fervor = 0.0  # 革命熱
        self.fear_of_terror = 0.0        # 恐怖政治への恐れ
        
    def __str__(self):
        return f"{self.social_class.name}_{self.agent_id}"


class FrenchRevolutionSimulator:
    """フランス革命シミュレーター"""
    
    def __init__(self):
        self.agents: List[RevolutionaryAgent] = []
        self.society = None
        self.current_phase = "革命前夜"
        self.step_count = 0
        
        # 階層別エージェント数
        self.class_sizes = {
            SocialClass.NOBILITY: 3,
            SocialClass.CLERGY: 3,
            SocialClass.BOURGEOISIE: 5,
            SocialClass.SANS_CULOTTES: 8,
            SocialClass.PEASANTS: 12,
        }
        
        # 歴史記録
        self.history = {
            'phase': [],
            'nobility_power': [],
            'revolutionary_fervor': [],
            'social_tension': [],
            'terror_level': [],
            'executed_count': [],
            'class_energies': {cls: [] for cls in SocialClass},
            'class_kappas': {cls: [] for cls in SocialClass},
        }
        
        # 重要イベント記録
        self.events = []
        
    def setup(self):
        """シミュレーションのセットアップ"""
        print("\n" + "="*70)
        print("🇫🇷 フランス革命シミュレーター - 1789-1794 🇫🇷")
        print("="*70)
        print("\n歴史的背景:")
        print("  1788年: 財政危機、飢饉による食糧不足")
        print("  1789年: 三部会召集、バスティーユ襲撃")
        print("  1792年: 王政廃止、共和制樹立")
        print("  1793年: 恐怖政治の開始")
        print("  1794年: テルミドールの反動")
        print("\n" + "="*70)
        
        # エージェント作成
        agent_id = 0
        
        # 1. 貴族（Nobility）
        print("\n👑 貴族階級の生成...")
        for i in range(self.class_sizes[SocialClass.NOBILITY]):
            agent = RevolutionaryAgent(SocialClass.NOBILITY, agent_id)
            # 高い特権意識、変化への強い抵抗
            agent.state.kappa[HumanLayer.UPPER.value] = 4.0  # 王権神授説への信念
            agent.state.kappa[HumanLayer.CORE.value] = 3.5   # 貴族の名誉
            agent.state.kappa[HumanLayer.BASE.value] = 2.0
            agent.state.E[HumanLayer.BASE.value] = 1.0       # 比較的安定
            self.agents.append(agent)
            agent_id += 1
        
        # 2. 聖職者（Clergy）
        print("⛪ 聖職者階級の生成...")
        for i in range(self.class_sizes[SocialClass.CLERGY]):
            agent = RevolutionaryAgent(SocialClass.CLERGY, agent_id)
            agent.state.kappa[HumanLayer.UPPER.value] = 3.5  # 宗教的信念
            agent.state.kappa[HumanLayer.CORE.value] = 3.0   # 教会の権威
            agent.state.kappa[HumanLayer.BASE.value] = 1.5
            agent.state.E[HumanLayer.BASE.value] = 1.5
            self.agents.append(agent)
            agent_id += 1
        
        # 3. ブルジョワジー（Bourgeoisie）
        print("💼 ブルジョワジー階級の生成...")
        for i in range(self.class_sizes[SocialClass.BOURGEOISIE]):
            agent = RevolutionaryAgent(SocialClass.BOURGEOISIE, agent_id)
            # 啓蒙思想、立憲君主制志向
            agent.state.kappa[HumanLayer.UPPER.value] = 2.5  # 自由主義思想
            agent.state.kappa[HumanLayer.CORE.value] = 2.0   # 法の支配
            agent.state.kappa[HumanLayer.BASE.value] = 1.2
            agent.state.E[HumanLayer.UPPER.value] = 2.0      # 政治的野心
            agent.state.E[HumanLayer.BASE.value] = 2.0       # 不満
            self.agents.append(agent)
            agent_id += 1
        
        # 4. サンキュロット（Sans-culottes）
        print("🔥 サンキュロット（都市労働者）の生成...")
        for i in range(self.class_sizes[SocialClass.SANS_CULOTTES]):
            agent = RevolutionaryAgent(SocialClass.SANS_CULOTTES, agent_id)
            # 急進的、直接行動志向
            agent.state.kappa[HumanLayer.UPPER.value] = 1.5  # 急進共和主義
            agent.state.kappa[HumanLayer.CORE.value] = 1.0   # 規範意識低い
            agent.state.kappa[HumanLayer.BASE.value] = 0.8
            agent.state.E[HumanLayer.BASE.value] = 4.0       # 高い怒りと飢え
            agent.state.E[HumanLayer.UPPER.value] = 3.0      # 革命的情熱
            self.agents.append(agent)
            agent_id += 1
        
        # 5. 農民（Peasants）
        print("🌾 農民階級の生成...")
        for i in range(self.class_sizes[SocialClass.PEASANTS]):
            agent = RevolutionaryAgent(SocialClass.PEASANTS, agent_id)
            # 保守的だが経済的圧力が高い
            agent.state.kappa[HumanLayer.UPPER.value] = 0.8
            agent.state.kappa[HumanLayer.CORE.value] = 1.5   # 伝統的価値観
            agent.state.kappa[HumanLayer.BASE.value] = 1.0
            agent.state.E[HumanLayer.BASE.value] = 5.0       # 飢餓と重税
            agent.state.E[HumanLayer.PHYSICAL.value] = 3.0   # 肉体的疲労
            self.agents.append(agent)
            agent_id += 1
        
        print(f"\n総エージェント数: {len(self.agents)}")
        
        # 階層間関係性マトリクス
        self._setup_class_relations()
        
        print("\n✅ セットアップ完了")
        
    def _setup_class_relations(self):
        """階層間の関係性を設定"""
        n = len(self.agents)
        relation_matrix = np.zeros((n, n))
        
        for i, agent_i in enumerate(self.agents):
            for j, agent_j in enumerate(self.agents):
                if i == j:
                    continue
                
                class_i = agent_i.social_class
                class_j = agent_j.social_class
                
                # 同じ階級内: 強い協力
                if class_i == class_j:
                    relation_matrix[i, j] = 0.8
                
                # 貴族 vs 平民
                elif (class_i == SocialClass.NOBILITY and 
                      class_j in [SocialClass.SANS_CULOTTES, SocialClass.PEASANTS]):
                    relation_matrix[i, j] = -0.9  # 強い対立
                    
                elif (class_j == SocialClass.NOBILITY and 
                      class_i in [SocialClass.SANS_CULOTTES, SocialClass.PEASANTS]):
                    relation_matrix[i, j] = -0.9
                
                # ブルジョワジー vs 貴族
                elif ((class_i == SocialClass.BOURGEOISIE and class_j == SocialClass.NOBILITY) or
                      (class_j == SocialClass.BOURGEOISIE and class_i == SocialClass.NOBILITY)):
                    relation_matrix[i, j] = -0.6  # 中程度の対立
                
                # ブルジョワジー vs サンキュロット（初期は協力）
                elif ((class_i == SocialClass.BOURGEOISIE and class_j == SocialClass.SANS_CULOTTES) or
                      (class_j == SocialClass.BOURGEOISIE and class_i == SocialClass.SANS_CULOTTES)):
                    relation_matrix[i, j] = 0.4  # 穏やかな協力
                
                # その他: 中立
                else:
                    relation_matrix[i, j] = 0.0
        
        relationships = RelationshipMatrix(matrix=relation_matrix)
        
        # 社会的カップリング（革命期は感情が伝播しやすい）
        coupling_params = SocialCouplingParams()
        coupling_params.zeta_base = 0.18   # BASE層エネルギー伝播強化
        coupling_params.zeta_upper = 0.08  # 思想の伝播
        coupling_params.xi_upper = 0.10    # イデオロギーκ伝播
        coupling_params.omega_base = -0.12 # 対立での増幅
        
        self.society = SocialDynamicsEngine(
            agents=self.agents,
            relationships=relationships,
            params=coupling_params
        )
        
    def run(self, total_steps: int = 300):
        """シミュレーション実行"""
        print(f"\n{'='*70}")
        print(f"シミュレーション開始: {total_steps}ステップ")
        print(f"{'='*70}\n")
        
        for step in range(total_steps):
            self.step_count = step
            
            # フェーズ判定と遷移
            self._update_phase(step)
            
            # 記録
            self._record_state()
            
            # フェーズ別の圧力適用
            self._apply_phase_pressure(step)
            
            # 社会的相互作用
            self.society.step()
            
            # 重要イベントの検出
            self._detect_events(step)
            
            # 進捗表示
            if (step + 1) % 30 == 0:
                self._print_status(step)
        
        print(f"\n{'='*70}")
        print("✅ シミュレーション完了")
        print(f"{'='*70}")
        
    def _update_phase(self, step: int):
        """フェーズの更新"""
        old_phase = self.current_phase
        
        if step < 60:
            self.current_phase = "革命前夜"
        elif step < 120:
            self.current_phase = "革命の勃発"
        elif step < 220:
            self.current_phase = "急進化・恐怖政治"
        else:
            self.current_phase = "テルミドール反動"
        
        if old_phase != self.current_phase:
            print(f"\n{'='*70}")
            print(f"📅 フェーズ遷移: {old_phase} → {self.current_phase}")
            print(f"{'='*70}\n")
            self.events.append((step, f"フェーズ遷移: {self.current_phase}"))
            
    def _apply_phase_pressure(self, step: int):
        """フェーズ別の圧力適用"""
        
        if self.current_phase == "革命前夜":
            # 財政危機、食糧不足
            for agent in self.agents:
                pressure = HumanPressure()
                
                if agent.social_class == SocialClass.NOBILITY:
                    pressure.base = np.random.uniform(0.5, 1.5)
                    pressure.core = np.random.uniform(0.5, 1.0)  # 特権への不安
                    
                elif agent.social_class == SocialClass.BOURGEOISIE:
                    pressure.upper = np.random.uniform(1.0, 2.0)  # 政治的野心
                    pressure.core = np.random.uniform(1.0, 2.0)   # 不平等への憤り
                    
                elif agent.social_class == SocialClass.SANS_CULOTTES:
                    pressure.base = np.random.uniform(3.0, 5.0)   # 飢えと怒り
                    pressure.upper = np.random.uniform(1.5, 2.5)  # 革命思想
                    
                elif agent.social_class == SocialClass.PEASANTS:
                    pressure.base = np.random.uniform(4.0, 6.0)   # 飢餓
                    pressure.physical = np.random.uniform(2.0, 3.0)
                    
                elif agent.social_class == SocialClass.CLERGY:
                    pressure.core = np.random.uniform(1.0, 2.0)   # 世俗化への危機感
                
                agent.step(pressure)
        
        elif self.current_phase == "革命の勃発":
            # バスティーユ襲撃、封建制廃止
            for agent in self.agents:
                pressure = HumanPressure()
                
                if agent.social_class == SocialClass.NOBILITY:
                    pressure.base = np.random.uniform(4.0, 7.0)   # 恐怖
                    pressure.core = np.random.uniform(3.0, 5.0)   # 特権の崩壊
                    pressure.upper = np.random.uniform(2.0, 4.0)  # 王権の危機
                    
                elif agent.social_class == SocialClass.BOURGEOISIE:
                    pressure.upper = np.random.uniform(2.0, 4.0)  # 立憲君主制への希望
                    pressure.base = np.random.uniform(2.0, 3.0)   # 興奮と不安
                    
                elif agent.social_class == SocialClass.SANS_CULOTTES:
                    pressure.base = np.random.uniform(2.0, 4.0)   # 革命の興奮
                    pressure.upper = np.random.uniform(3.0, 5.0)  # 共和主義
                    agent.revolutionary_fervor += 0.1
                    
                elif agent.social_class == SocialClass.PEASANTS:
                    pressure.base = np.random.uniform(2.0, 4.0)   # 希望と混乱
                    pressure.core = np.random.uniform(1.0, 2.0)
                
                agent.step(pressure)
        
        elif self.current_phase == "急進化・恐怖政治":
            # ジャコバン独裁、大量処刑
            terror_intensity = min((step - 120) / 100.0, 1.0) * 5.0
            
            for agent in self.agents:
                if not agent.is_alive:
                    continue
                    
                pressure = HumanPressure()
                
                if agent.social_class == SocialClass.NOBILITY:
                    # 多くが亡命または処刑
                    if np.random.random() < 0.01:  # 処刑リスク
                        agent.is_alive = False
                        self.events.append((step, f"処刑: {agent}"))
                        continue
                    pressure.base = np.random.uniform(6.0, 10.0)  # 極度の恐怖
                    
                elif agent.social_class == SocialClass.BOURGEOISIE:
                    # ジロンド派弾圧
                    if np.random.random() < 0.005:
                        agent.is_alive = False
                        self.events.append((step, f"処刑: {agent}"))
                        continue
                    pressure.base = np.random.uniform(4.0, 7.0)   # 恐怖
                    pressure.core = np.random.uniform(3.0, 5.0)   # 良心との葛藤
                    
                elif agent.social_class == SocialClass.SANS_CULOTTES:
                    pressure.upper = np.random.uniform(4.0, 6.0)  # 急進主義
                    pressure.base = np.random.uniform(2.0, 4.0)   # 革命防衛の使命感
                    agent.revolutionary_fervor += 0.15
                    
                elif agent.social_class == SocialClass.PEASANTS:
                    pressure.base = np.random.uniform(3.0, 5.0)   # 混乱と恐怖
                    pressure.core = np.random.uniform(2.0, 4.0)
                
                agent.fear_of_terror = terror_intensity
                agent.step(pressure)
        
        else:  # テルミドール反動
            # ロベスピエール失脚、恐怖政治の終焉
            for agent in self.agents:
                if not agent.is_alive:
                    continue
                    
                pressure = HumanPressure()
                
                if agent.social_class == SocialClass.SANS_CULOTTES:
                    # 急進派の失脚
                    pressure.base = np.random.uniform(3.0, 5.0)   # 失望
                    pressure.upper = np.random.uniform(1.0, 2.0)  # 理想の崩壊
                    agent.revolutionary_fervor -= 0.1
                    
                elif agent.social_class == SocialClass.BOURGEOISIE:
                    pressure.base = np.random.uniform(1.0, 2.0)   # 安堵
                    pressure.upper = np.random.uniform(2.0, 3.0)  # 新秩序の構築
                    
                else:
                    pressure.base = np.random.uniform(1.0, 3.0)
                    pressure.core = np.random.uniform(1.0, 2.0)
                
                agent.step(pressure)
    
    def _detect_events(self, step: int):
        """重要イベントの検出"""
        # バスティーユ襲撃
        if step == 60:
            avg_sans_culottes_E = np.mean([
                a.state.E[HumanLayer.BASE.value] 
                for a in self.agents 
                if a.social_class == SocialClass.SANS_CULOTTES and a.is_alive
            ])
            self.events.append((step, f"🏰 バスティーユ襲撃！民衆の怒り: {avg_sans_culottes_E:.2f}"))
        
        # 王政廃止
        if step == 120:
            self.events.append((step, "👑 王政廃止宣言！"))
        
        # 恐怖政治開始
        if step == 150:
            self.events.append((step, "⚔️ 恐怖政治開始"))
        
        # ロベスピエール失脚
        if step == 220:
            self.events.append((step, "🔻 テルミドール9日のクーデター"))
    
    def _record_state(self):
        """状態の記録"""
        self.history['phase'].append(self.current_phase)
        
        # 貴族の権力（UPPER κの平均）
        nobility_power = np.mean([
            a.state.kappa[HumanLayer.UPPER.value] 
            for a in self.agents 
            if a.social_class == SocialClass.NOBILITY and a.is_alive
        ])
        self.history['nobility_power'].append(nobility_power)
        
        # 革命熱（サンキュロットのUPPER Eの平均）
        if any(a.social_class == SocialClass.SANS_CULOTTES and a.is_alive for a in self.agents):
            rev_fervor = np.mean([
                a.state.E[HumanLayer.UPPER.value] 
                for a in self.agents 
                if a.social_class == SocialClass.SANS_CULOTTES and a.is_alive
            ])
        else:
            rev_fervor = 0
        self.history['revolutionary_fervor'].append(rev_fervor)
        
        # 社会的緊張（全体のBASE Eの平均）
        alive_agents = [a for a in self.agents if a.is_alive]
        if alive_agents:
            social_tension = np.mean([a.state.E[HumanLayer.BASE.value] for a in alive_agents])
        else:
            social_tension = 0
        self.history['social_tension'].append(social_tension)
        
        # 恐怖レベル
        terror = np.mean([a.fear_of_terror for a in alive_agents]) if alive_agents else 0
        self.history['terror_level'].append(terror)
        
        # 処刑者数
        executed = sum(1 for a in self.agents if not a.is_alive)
        self.history['executed_count'].append(executed)
        
        # 階級別エネルギーとκ
        for social_class in SocialClass:
            class_agents = [a for a in self.agents if a.social_class == social_class and a.is_alive]
            if class_agents:
                avg_E = np.mean([a.state.E[HumanLayer.BASE.value] for a in class_agents])
                avg_kappa = np.mean([a.state.kappa[HumanLayer.UPPER.value] for a in class_agents])
            else:
                avg_E = 0
                avg_kappa = 0
            self.history['class_energies'][social_class].append(avg_E)
            self.history['class_kappas'][social_class].append(avg_kappa)
    
    def _print_status(self, step: int):
        """ステータス表示"""
        alive = sum(1 for a in self.agents if a.is_alive)
        executed = sum(1 for a in self.agents if not a.is_alive)
        
        print(f"Step {step+1}/{len(self.history['phase'])}: "
              f"Phase={self.current_phase}, "
              f"Alive={alive}, Executed={executed}, "
              f"Terror={self.history['terror_level'][-1]:.2f}")
    
    def visualize(self):
        """結果の可視化"""
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        fig.suptitle('🇫🇷 フランス革命シミュレーション結果 (1789-1794) 🇫🇷', 
                     fontsize=18, fontweight='bold')
        
        steps = range(len(self.history['phase']))
        
        # 1. 貴族の権力の衰退
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(steps, self.history['nobility_power'], 'purple', linewidth=2.5, label='貴族の権力')
        ax1.fill_between(steps, 0, self.history['nobility_power'], alpha=0.3, color='purple')
        ax1.set_title('貴族の権力衰退', fontsize=14, fontweight='bold')
        ax1.set_xlabel('時間経過')
        ax1.set_ylabel('権力 (κ_UPPER)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 2. 革命熱の推移
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(steps, self.history['revolutionary_fervor'], 'red', linewidth=2.5, label='革命熱')
        ax2.fill_between(steps, 0, self.history['revolutionary_fervor'], alpha=0.3, color='red')
        ax2.set_title('革命熱の高揚', fontsize=14, fontweight='bold')
        ax2.set_xlabel('時間経過')
        ax2.set_ylabel('革命熱 (E_UPPER)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 3. 社会的緊張
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.plot(steps, self.history['social_tension'], 'orange', linewidth=2.5, label='社会的緊張')
        ax3.fill_between(steps, 0, self.history['social_tension'], alpha=0.3, color='orange')
        ax3.set_title('社会的緊張', fontsize=14, fontweight='bold')
        ax3.set_xlabel('時間経過')
        ax3.set_ylabel('緊張 (E_BASE)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # 4. 恐怖政治レベル
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.plot(steps, self.history['terror_level'], 'darkred', linewidth=2.5, label='恐怖政治')
        ax4.fill_between(steps, 0, self.history['terror_level'], alpha=0.3, color='darkred')
        ax4.set_title('恐怖政治の強度', fontsize=14, fontweight='bold')
        ax4.set_xlabel('時間経過')
        ax4.set_ylabel('恐怖レベル')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        # 5. 処刑者数
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.plot(steps, self.history['executed_count'], 'black', linewidth=2.5, label='処刑者数')
        ax5.fill_between(steps, 0, self.history['executed_count'], alpha=0.3, color='gray')
        ax5.set_title('処刑者数の推移', fontsize=14, fontweight='bold')
        ax5.set_xlabel('時間経過')
        ax5.set_ylabel('処刑者数')
        ax5.grid(True, alpha=0.3)
        ax5.legend()
        
        # 6. 階級別エネルギー
        ax6 = fig.add_subplot(gs[1, 2])
        colors = {'NOBILITY': 'purple', 'CLERGY': 'blue', 'BOURGEOISIE': 'green',
                  'SANS_CULOTTES': 'red', 'PEASANTS': 'brown'}
        for social_class in SocialClass:
            ax6.plot(steps, self.history['class_energies'][social_class], 
                    color=colors[social_class.name], linewidth=2, 
                    label=social_class.name, alpha=0.7)
        ax6.set_title('階級別ストレスレベル', fontsize=14, fontweight='bold')
        ax6.set_xlabel('時間経過')
        ax6.set_ylabel('ストレス (E_BASE)')
        ax6.grid(True, alpha=0.3)
        ax6.legend(fontsize=8)
        
        # 7. 階級別イデオロギー強度
        ax7 = fig.add_subplot(gs[2, 0])
        for social_class in SocialClass:
            ax7.plot(steps, self.history['class_kappas'][social_class], 
                    color=colors[social_class.name], linewidth=2, 
                    label=social_class.name, alpha=0.7)
        ax7.set_title('階級別イデオロギー強度', fontsize=14, fontweight='bold')
        ax7.set_xlabel('時間経過')
        ax7.set_ylabel('イデオロギー (κ_UPPER)')
        ax7.grid(True, alpha=0.3)
        ax7.legend(fontsize=8)
        
        # 8. フェーズタイムライン
        ax8 = fig.add_subplot(gs[2, 1:])
        phase_colors = {
            '革命前夜': 'lightblue',
            '革命の勃発': 'yellow',
            '急進化・恐怖政治': 'red',
            'テルミドール反動': 'lightgreen'
        }
        
        current_phase = self.history['phase'][0]
        start_step = 0
        
        for i, phase in enumerate(self.history['phase']):
            if phase != current_phase or i == len(self.history['phase']) - 1:
                ax8.axvspan(start_step, i, alpha=0.3, 
                           color=phase_colors.get(current_phase, 'gray'),
                           label=current_phase if start_step == 0 or current_phase not in [self.history['phase'][j] for j in range(start_step)] else "")
                if i < len(self.history['phase']) - 1:
                    current_phase = phase
                    start_step = i
        
        # イベント表示
        for step, event in self.events:
            if step < len(steps):
                ax8.axvline(x=step, color='red', linestyle='--', alpha=0.5, linewidth=1)
                ax8.text(step, 0.5, event.split(':')[0] if ':' in event else event, 
                        rotation=90, fontsize=8, va='bottom')
        
        ax8.set_title('歴史的タイムライン', fontsize=14, fontweight='bold')
        ax8.set_xlabel('時間経過')
        ax8.set_ylim(0, 1)
        ax8.set_yticks([])
        ax8.legend(loc='upper left', fontsize=9)
        ax8.grid(True, alpha=0.3, axis='x')
        
        plt.savefig('french_revolution_simulation.png', dpi=150, bbox_inches='tight')
        print("\n📊 可視化結果を保存: french_revolution_simulation.png")
        plt.show()
    
    def print_summary(self):
        """シミュレーション結果のサマリー"""
        print(f"\n{'='*70}")
        print("📜 フランス革命シミュレーション結果サマリー")
        print(f"{'='*70}\n")
        
        print("🎭 最終状態:")
        alive_by_class = {}
        for social_class in SocialClass:
            alive = sum(1 for a in self.agents if a.social_class == social_class and a.is_alive)
            total = self.class_sizes[social_class]
            alive_by_class[social_class] = (alive, total)
            print(f"  {social_class.name:20s}: {alive}/{total} 生存")
        
        print(f"\n⚰️  総処刑者数: {self.history['executed_count'][-1]}")
        
        print("\n📊 主要指標:")
        print(f"  貴族の権力 (初期→最終): {self.history['nobility_power'][0]:.2f} → {self.history['nobility_power'][-1]:.2f}")
        print(f"  最大革命熱: {max(self.history['revolutionary_fervor']):.2f}")
        print(f"  最大恐怖レベル: {max(self.history['terror_level']):.2f}")
        print(f"  最大社会的緊張: {max(self.history['social_tension']):.2f}")
        
        print("\n📅 主要イベント:")
        for step, event in self.events[:10]:  # 最初の10イベント
            print(f"  Step {step:3d}: {event}")
        
        print(f"\n{'='*70}\n")


def main():
    """メイン実行"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                  🇫🇷 フランス革命シミュレーター 🇫🇷                  ║
║           Structural Subjectivity Dynamics Analysis                ║
╚════════════════════════════════════════════════════════════════════╝

1789年から1794年までのフランス革命をSSD理論でシミュレート。

社会階層:
  👑 貴族（Nobility）        - 特権階級、王政支持
  ⛪ 聖職者（Clergy）         - 宗教的権威、保守的
  💼 ブルジョワジー（Bourgeoisie）- 啓蒙思想、改革派
  🔥 サンキュロット（Sans-culottes）- 急進的都市労働者
  🌾 農民（Peasants）        - 経済的困窮、保守的

歴史的フェーズ:
  1. 革命前夜（1788-1789）
  2. 革命の勃発（1789-1792）
  3. 急進化・恐怖政治（1792-1794）
  4. テルミドール反動（1794）
    """)
    
    input("Enterキーを押してシミュレーションを開始...")
    
    # シミュレーション実行
    simulator = FrenchRevolutionSimulator()
    simulator.setup()
    simulator.run(total_steps=300)
    simulator.print_summary()
    simulator.visualize()
    
    print("\n✅ シミュレーション完了！歴史の再解釈をお楽しみください。")


if __name__ == "__main__":
    main()
