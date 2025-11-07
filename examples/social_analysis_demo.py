"""
社会分析デモ - SSD Engine を用いた社会的ダイナミクスの分析
============================================================

このデモでは、構造主観力学（SSD）理論を用いて、
現実的な社会現象をシミュレートし、分析します。

分析テーマ:
1. 組織内の意見対立と合意形成
2. ソーシャルプレッシャーの伝播
3. リーダーシップの創発
4. 集団分極化（グループシンク）
5. 規範の形成と崩壊

理論基盤:
- E/κダイナミクス: 意思決定の内部力学
- 主観的社会システム: 他者観測と主観的解釈
- 社会的カップリング: エネルギーとκの伝播
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ssd_human_module import HumanAgent, HumanPressure, HumanLayer, HumanParams
from extensions.ssd_social_dynamics import (
    SocialCouplingParams, RelationshipMatrix, SocialDynamicsEngine
)
from extensions.ssd_subjective_society import (
    SubjectiveSociety, AgentState, SignalGenerator, ObservableSignal
)
from extensions.ssd_subjective_social_pressure import ObservationContext
import numpy as np
from typing import List, Dict
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 日本語フォント設定
rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
rcParams['axes.unicode_minus'] = False


class SocialAnalysisScenario:
    """社会分析シナリオの基底クラス"""
    
    def __init__(self, num_agents: int, scenario_name: str):
        self.num_agents = num_agents
        self.scenario_name = scenario_name
        self.agents: List[HumanAgent] = []
        self.society = None
        self.history = {
            'E_base': [],
            'E_core': [],
            'E_upper': [],
            'kappa_core': [],
            'kappa_upper': [],
            'signals': [],
        }
        
    def setup_agents(self):
        """エージェントのセットアップ（サブクラスで実装）"""
        raise NotImplementedError
        
    def run_simulation(self, num_steps: int = 100):
        """シミュレーション実行"""
        print(f"\n{'='*60}")
        print(f"シナリオ: {self.scenario_name}")
        print(f"エージェント数: {self.num_agents}")
        print(f"ステップ数: {num_steps}")
        print(f"{'='*60}\n")
        
        for step in range(num_steps):
            # 各エージェントの状態を観測
            self._record_state(step)
            
            # 社会的相互作用
            self._step_interaction()
            
            # 進捗表示
            if (step + 1) % 20 == 0:
                print(f"Step {step + 1}/{num_steps} 完了")
        
        print("\nシミュレーション完了！")
        
    def _record_state(self, step: int):
        """状態の記録"""
        E_base = [agent.state.E[HumanLayer.BASE.value] for agent in self.agents]
        E_core = [agent.state.E[HumanLayer.CORE.value] for agent in self.agents]
        E_upper = [agent.state.E[HumanLayer.UPPER.value] for agent in self.agents]
        kappa_core = [agent.state.kappa[HumanLayer.CORE.value] for agent in self.agents]
        kappa_upper = [agent.state.kappa[HumanLayer.UPPER.value] for agent in self.agents]
        
        self.history['E_base'].append(E_base)
        self.history['E_core'].append(E_core)
        self.history['E_upper'].append(E_upper)
        self.history['kappa_core'].append(kappa_core)
        self.history['kappa_upper'].append(kappa_upper)
        
    def _step_interaction(self):
        """1ステップの相互作用（サブクラスで実装）"""
        raise NotImplementedError
        
    def visualize_results(self):
        """結果の可視化"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'社会分析: {self.scenario_name}', fontsize=16, fontweight='bold')
        
        # BASE層エネルギー（感情）
        ax1 = axes[0, 0]
        for i in range(self.num_agents):
            E_base_i = [step[i] for step in self.history['E_base']]
            ax1.plot(E_base_i, label=f'Agent {i+1}', alpha=0.7)
        ax1.set_title('BASE層エネルギー（感情・本能）')
        ax1.set_xlabel('ステップ')
        ax1.set_ylabel('E_BASE')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # CORE層エネルギー（規範葛藤）
        ax2 = axes[0, 1]
        for i in range(self.num_agents):
            E_core_i = [step[i] for step in self.history['E_core']]
            ax2.plot(E_core_i, label=f'Agent {i+1}', alpha=0.7)
        ax2.set_title('CORE層エネルギー（規範葛藤）')
        ax2.set_xlabel('ステップ')
        ax2.set_ylabel('E_CORE')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # CORE層κ（規範の定着）
        ax3 = axes[1, 0]
        for i in range(self.num_agents):
            kappa_core_i = [step[i] for step in self.history['kappa_core']]
            ax3.plot(kappa_core_i, label=f'Agent {i+1}', alpha=0.7)
        ax3.set_title('CORE層κ（規範の定着度）')
        ax3.set_xlabel('ステップ')
        ax3.set_ylabel('κ_CORE')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # UPPER層κ（イデオロギーの定着）
        ax4 = axes[1, 1]
        for i in range(self.num_agents):
            kappa_upper_i = [step[i] for step in self.history['kappa_upper']]
            ax4.plot(kappa_upper_i, label=f'Agent {i+1}', alpha=0.7)
        ax4.set_title('UPPER層κ（イデオロギーの定着度）')
        ax4.set_xlabel('ステップ')
        ax4.set_ylabel('κ_UPPER')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'social_analysis_{self.scenario_name.replace(" ", "_")}.png', dpi=150)
        print(f"\n可視化結果を保存: social_analysis_{self.scenario_name.replace(' ', '_')}.png")
        plt.show()
        
    def analyze_results(self):
        """結果の分析"""
        print(f"\n{'='*60}")
        print(f"分析結果: {self.scenario_name}")
        print(f"{'='*60}\n")
        
        # 最終状態の分析
        final_E_base = self.history['E_base'][-1]
        final_E_core = self.history['E_core'][-1]
        final_kappa_core = self.history['kappa_core'][-1]
        final_kappa_upper = self.history['kappa_upper'][-1]
        
        print("📊 最終状態:")
        print(f"  BASE層エネルギー平均: {np.mean(final_E_base):.2f} (SD: {np.std(final_E_base):.2f})")
        print(f"  CORE層エネルギー平均: {np.mean(final_E_core):.2f} (SD: {np.std(final_E_core):.2f})")
        print(f"  CORE層κ平均: {np.mean(final_kappa_core):.2f} (SD: {np.std(final_kappa_core):.2f})")
        print(f"  UPPER層κ平均: {np.mean(final_kappa_upper):.2f} (SD: {np.std(final_kappa_upper):.2f})")
        
        # 収束性の分析
        E_base_variance = [np.var(step) for step in self.history['E_base']]
        kappa_core_variance = [np.var(step) for step in self.history['kappa_core']]
        
        print(f"\n📈 ダイナミクス:")
        print(f"  感情の分散（初期→最終）: {E_base_variance[0]:.2f} → {E_base_variance[-1]:.2f}")
        print(f"  規範の分散（初期→最終）: {kappa_core_variance[0]:.2f} → {kappa_core_variance[-1]:.2f}")
        
        if E_base_variance[-1] < E_base_variance[0]:
            print("  ✓ 感情の収束（集団の安定化）")
        else:
            print("  ✗ 感情の発散（集団の不安定化）")
            
        if kappa_core_variance[-1] < kappa_core_variance[0]:
            print("  ✓ 規範の収束（価値観の統一）")
        else:
            print("  ✗ 規範の発散（価値観の多様化）")


class OpinionPolarizationScenario(SocialAnalysisScenario):
    """意見分極化シナリオ
    
    2つのグループが異なる意見を持ち、
    グループ内では協力、グループ間では競争する状況をシミュレート。
    """
    
    def __init__(self, num_agents: int = 6):
        super().__init__(num_agents, "意見分極化（Opinion Polarization）")
        
    def setup_agents(self):
        """エージェントのセットアップ"""
        print("エージェントをセットアップ中...")
        
        # 2グループに分割
        group_size = self.num_agents // 2
        
        # グループA: 保守的（CORE層κが高い）
        for i in range(group_size):
            agent = HumanAgent()
            agent.state.kappa[HumanLayer.CORE.value] = 2.5  # 高い規範意識
            agent.state.kappa[HumanLayer.UPPER.value] = 1.8  # 保守的イデオロギー
            self.agents.append(agent)
            
        # グループB: 革新的（UPPER層κが高い）
        for i in range(group_size, self.num_agents):
            agent = HumanAgent()
            agent.state.kappa[HumanLayer.CORE.value] = 1.2  # 低い規範意識
            agent.state.kappa[HumanLayer.UPPER.value] = 2.5  # 革新的イデオロギー
            self.agents.append(agent)
        
        # 関係性マトリクス: グループ内協力、グループ間競争
        relation_matrix = np.zeros((self.num_agents, self.num_agents))
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i == j:
                    continue
                # 同じグループなら協力
                if (i < group_size and j < group_size) or (i >= group_size and j >= group_size):
                    relation_matrix[i, j] = 0.8
                # 異なるグループなら競争
                else:
                    relation_matrix[i, j] = -0.6
        
        # 社会システム構築
        relationships = RelationshipMatrix(matrix=relation_matrix)
        coupling_params = SocialCouplingParams()
        self.society = SocialDynamicsEngine(
            agents=self.agents,
            relationships=relationships,
            params=coupling_params
        )
        
        print(f"  グループA (保守派): Agent 1-{group_size}")
        print(f"  グループB (革新派): Agent {group_size+1}-{self.num_agents}")
        
    def _step_interaction(self):
        """1ステップの相互作用"""
        # 外部圧力: 議論のトピック（UPPER層に圧力）
        debate_pressure = HumanPressure()
        debate_pressure.upper = np.random.uniform(0.5, 1.5)
        
        # 各エージェントに圧力を適用
        for agent in self.agents:
            agent.step(debate_pressure)
        
        # 社会的カップリング
        self.society.step()


class LeadershipEmergenceScenario(SocialAnalysisScenario):
    """リーダーシップ創発シナリオ
    
    初期状態では全員が同等だが、
    状況への対応力の違いからリーダーが創発的に現れる。
    """
    
    def __init__(self, num_agents: int = 5):
        super().__init__(num_agents, "リーダーシップの創発")
        
    def setup_agents(self):
        """エージェントのセットアップ"""
        print("エージェントをセットアップ中...")
        
        # 全員をほぼ同じ初期状態で作成
        for i in range(self.num_agents):
            agent = HumanAgent()
            # わずかなランダム性を加える
            agent.state.kappa[HumanLayer.UPPER.value] = 1.0 + np.random.uniform(-0.2, 0.2)
            agent.state.kappa[HumanLayer.CORE.value] = 1.0 + np.random.uniform(-0.2, 0.2)
            self.agents.append(agent)
        
        # 1人だけ少し高いUPPER κを持つ（潜在的リーダー）
        self.agents[0].state.kappa[HumanLayer.UPPER.value] = 2.0
        
        # 協力的な関係性
        relationships = RelationshipMatrix.create_cooperative(self.num_agents)
        coupling_params = SocialCouplingParams()
        self.society = SocialDynamicsEngine(
            agents=self.agents,
            relationships=relationships,
            params=coupling_params
        )
        
        print(f"  全エージェント: ほぼ同等の初期状態")
        print(f"  Agent 1: わずかに高いイデオロギー慣性（潜在的リーダー）")
        
    def _step_interaction(self):
        """1ステップの相互作用"""
        # 危機的状況: BASE層に高い圧力
        crisis_pressure = HumanPressure()
        crisis_pressure.base = np.random.uniform(2.0, 4.0)
        crisis_pressure.upper = np.random.uniform(0.5, 1.0)
        
        # 各エージェントに圧力を適用
        for agent in self.agents:
            agent.step(crisis_pressure)
        
        # 社会的カップリング
        self.society.step()


class NormFormationScenario(SocialAnalysisScenario):
    """規範形成シナリオ
    
    初期状態では規範が未確立だが、
    社会的相互作用を通じて集団規範が形成される。
    """
    
    def __init__(self, num_agents: int = 8):
        super().__init__(num_agents, "規範の形成")
        
    def setup_agents(self):
        """エージェントのセットアップ"""
        print("エージェントをセットアップ中...")
        
        # 全員、低いCORE κでスタート（規範未確立）
        for i in range(self.num_agents):
            agent = HumanAgent()
            agent.state.kappa[HumanLayer.CORE.value] = 0.8  # 低い規範慣性
            agent.state.kappa[HumanLayer.BASE.value] = 1.5  # 本能的
            self.agents.append(agent)
        
        # 2人だけ高いCORE κ（規範の種）
        self.agents[0].state.kappa[HumanLayer.CORE.value] = 2.5
        self.agents[1].state.kappa[HumanLayer.CORE.value] = 2.5
        
        # 協力的な関係性（規範が伝播しやすい）
        relationships = RelationshipMatrix.create_cooperative(self.num_agents)
        coupling_params = SocialCouplingParams()
        # κ伝播を強化
        coupling_params.xi_core = 0.12  # デフォルト0.06の2倍
        self.society = SocialDynamicsEngine(
            agents=self.agents,
            relationships=relationships,
            params=coupling_params
        )
        
        print(f"  大多数: 規範未確立（低CORE κ）")
        print(f"  Agent 1-2: 規範の種（高CORE κ）")
        
    def _step_interaction(self):
        """1ステップの相互作用"""
        # 規範違反の誘惑（BASE層圧力）と規範遵守の圧力（CORE層）
        temptation_pressure = HumanPressure()
        temptation_pressure.base = np.random.uniform(1.0, 2.0)
        temptation_pressure.core = np.random.uniform(0.5, 1.0)
        
        # 各エージェントに圧力を適用
        for agent in self.agents:
            agent.step(temptation_pressure)
        
        # 社会的カップリング（規範の伝播）
        self.society.step()


def main():
    """メイン実行"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║          SSDエンジン 社会分析デモ                              ║
║      Structural Subjectivity Dynamics - Social Analysis        ║
╚════════════════════════════════════════════════════════════════╝

このデモでは、以下の社会現象を分析します:

1. 意見分極化（Opinion Polarization）
   - 2つのグループ間の対立と分極化

2. リーダーシップの創発
   - 危機的状況下でのリーダーの自然発生

3. 規範の形成
   - 社会規範が集団内で伝播・定着するプロセス
    """)
    
    # シナリオ選択
    print("\n実行するシナリオを選択してください:")
    print("1: 意見分極化")
    print("2: リーダーシップの創発")
    print("3: 規範の形成")
    print("4: すべて実行")
    
    choice = input("\n選択 (1-4): ").strip()
    
    scenarios = []
    
    if choice == '1':
        scenarios.append(OpinionPolarizationScenario())
    elif choice == '2':
        scenarios.append(LeadershipEmergenceScenario())
    elif choice == '3':
        scenarios.append(NormFormationScenario())
    elif choice == '4':
        scenarios.append(OpinionPolarizationScenario())
        scenarios.append(LeadershipEmergenceScenario())
        scenarios.append(NormFormationScenario())
    else:
        print("無効な選択です。デフォルトで意見分極化を実行します。")
        scenarios.append(OpinionPolarizationScenario())
    
    # 各シナリオを実行
    for scenario in scenarios:
        scenario.setup_agents()
        scenario.run_simulation(num_steps=100)
        scenario.analyze_results()
        scenario.visualize_results()
        
        print("\n" + "="*60)
        input("次のシナリオに進むにはEnterキーを押してください...")
    
    print("\n✅ すべてのシナリオが完了しました！")


if __name__ == "__main__":
    main()
