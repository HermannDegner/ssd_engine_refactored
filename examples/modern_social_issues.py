"""
現代社会問題分析 - SSD Engine を用いた現実的な社会問題の分析
================================================================

現代社会の具体的な問題をSSD理論でモデル化・分析:

1. SNS上の炎上現象（Online Flame Wars）
   - 批判の連鎖と感情の増幅
   - エコーチェンバー効果

2. 職場のパワーハラスメント（Workplace Power Harassment）
   - 権力勾配と服従の心理
   - 被害者の内面的変化

3. 政治的分断（Political Polarization）
   - 左派vs右派の対立構造
   - メディアの影響と確証バイアス

4. いじめの構造（Bullying Structure）
   - 加害者・被害者・傍観者の三角関係
   - 集団圧力と同調行動
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ssd_human_module import HumanAgent, HumanPressure, HumanLayer
from extensions.ssd_social_dynamics import (
    SocialCouplingParams, RelationshipMatrix, SocialDynamicsEngine
)
import numpy as np
from typing import List, Dict
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 日本語フォント設定
rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
rcParams['axes.unicode_minus'] = False


class SNSFlameWarsAnalysis:
    """SNS炎上分析
    
    SNS上での批判の連鎖と感情の増幅をモデル化
    """
    
    def __init__(self, num_users: int = 30):
        self.num_users = num_users
        self.users: List[HumanAgent] = []
        self.society = None
        self.history = {
            'anger_levels': [],
            'engagement': [],
            'polarization': [],
        }
        
    def setup(self):
        """セットアップ"""
        print("\n" + "="*60)
        print("分析: SNS炎上現象")
        print("="*60)
        print("\n📱 ある発言が物議を醸し、SNSが炎上...")
        
        # ユーザー作成
        # 3つのグループ: 賛成派、反対派、中立派
        group_size = self.num_users // 3
        
        # 賛成派（低BASE E、高UPPER κ）
        for i in range(group_size):
            user = HumanAgent()
            user.state.kappa[HumanLayer.UPPER.value] = 2.5  # 強い信念
            user.state.E[HumanLayer.BASE.value] = 1.0
            self.users.append(user)
        
        # 反対派（低BASE E、高UPPER κ、逆の方向）
        for i in range(group_size, 2 * group_size):
            user = HumanAgent()
            user.state.kappa[HumanLayer.UPPER.value] = 2.5  # 強い（逆の）信念
            user.state.E[HumanLayer.BASE.value] = 1.0
            self.users.append(user)
        
        # 中立派（低UPPER κ）
        for i in range(2 * group_size, self.num_users):
            user = HumanAgent()
            user.state.kappa[HumanLayer.UPPER.value] = 0.8
            user.state.E[HumanLayer.BASE.value] = 0.5
            self.users.append(user)
        
        # 関係性: グループ内協力、グループ間対立
        relation_matrix = np.zeros((self.num_users, self.num_users))
        for i in range(self.num_users):
            for j in range(self.num_users):
                if i == j:
                    continue
                # 同じグループ
                if (i < group_size and j < group_size) or \
                   (group_size <= i < 2*group_size and group_size <= j < 2*group_size) or \
                   (i >= 2*group_size and j >= 2*group_size):
                    relation_matrix[i, j] = 0.7
                # 賛成 vs 反対
                elif (i < group_size and group_size <= j < 2*group_size) or \
                     (group_size <= i < 2*group_size and j < group_size):
                    relation_matrix[i, j] = -0.8
                # 中立との関係
                else:
                    relation_matrix[i, j] = 0.0
        
        relationships = RelationshipMatrix(matrix=relation_matrix)
        
        # エネルギー伝播を強化（SNSの拡散効果）
        coupling_params = SocialCouplingParams()
        coupling_params.zeta_base = 0.20  # 怒りが伝染しやすい
        coupling_params.omega_base = -0.10  # 競合で怒りが増幅
        
        self.society = SocialDynamicsEngine(
            agents=self.users,
            relationships=relationships,
            params=coupling_params
        )
        
        print(f"  賛成派: User 1-{group_size}")
        print(f"  反対派: User {group_size+1}-{2*group_size}")
        print(f"  中立派: User {2*group_size+1}-{self.num_users}")
        
    def run(self, num_steps: int = 100):
        """実行"""
        print(f"\nシミュレーション開始（{num_steps}ステップ）...")
        
        group_size = self.num_users // 3
        
        for step in range(num_steps):
            # 記録
            anger_levels = [u.state.E[HumanLayer.BASE.value] for u in self.users]
            self.history['anger_levels'].append(anger_levels)
            
            # エンゲージメント（エネルギー総量）
            total_engagement = sum([u.state.E[HumanLayer.UPPER.value] for u in self.users])
            self.history['engagement'].append(total_engagement)
            
            # 分極化（グループ間の差）
            group1_avg = np.mean([u.state.kappa[HumanLayer.UPPER.value] for u in self.users[:group_size]])
            group2_avg = np.mean([u.state.kappa[HumanLayer.UPPER.value] for u in self.users[group_size:2*group_size]])
            polarization = abs(group1_avg - group2_avg)
            self.history['polarization'].append(polarization)
            
            # 圧力適用
            if step < 20:
                # 初期: 小さな刺激
                pressure = HumanPressure()
                pressure.upper = np.random.uniform(0.5, 1.0)
                
            elif step < 50:
                # 炎上開始
                if step == 20:
                    print(f"\nStep {step}: 🔥 炎上開始！")
                    # 対立する投稿
                    self.users[0].state.E[HumanLayer.UPPER.value] = 8.0
                    self.users[group_size].state.E[HumanLayer.UPPER.value] = 8.0
                
                pressure = HumanPressure()
                pressure.base = np.random.uniform(1.0, 2.0)  # 怒り
                pressure.upper = np.random.uniform(1.0, 3.0)  # 主張
                
            elif step < 80:
                # 炎上ピーク
                if step == 50:
                    print(f"Step {step}: 💥 炎上ピーク！")
                pressure = HumanPressure()
                pressure.base = np.random.uniform(2.0, 4.0)
                pressure.upper = np.random.uniform(2.0, 4.0)
                
            else:
                # 鎮静化
                if step == 80:
                    print(f"Step {step}: 🌊 炎上の鎮静化...")
                pressure = HumanPressure()
                pressure.base = np.random.uniform(0.5, 1.0)
                pressure.upper = np.random.uniform(0.5, 1.0)
            
            for user in self.users:
                user.step(pressure)
            
            self.society.step()
            
            if (step + 1) % 20 == 0:
                avg_anger = np.mean(anger_levels)
                print(f"  Step {step+1}: 平均怒りレベル = {avg_anger:.2f}")
        
        print("\n✅ シミュレーション完了")
        
    def visualize(self):
        """可視化"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('SNS炎上分析', fontsize=16, fontweight='bold')
        
        steps = range(len(self.history['anger_levels']))
        group_size = self.num_users // 3
        
        # 怒りレベルの推移
        ax1 = axes[0, 0]
        anger_array = np.array(self.history['anger_levels'])
        ax1.plot(steps, np.mean(anger_array, axis=1), 'r-', linewidth=2, label='平均怒り')
        ax1.fill_between(steps, 
                         np.mean(anger_array, axis=1) - np.std(anger_array, axis=1),
                         np.mean(anger_array, axis=1) + np.std(anger_array, axis=1),
                         alpha=0.3, color='red')
        ax1.set_title('怒りレベルの推移')
        ax1.set_xlabel('ステップ')
        ax1.set_ylabel('怒り (E_BASE)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # グループ別の怒り
        ax2 = axes[0, 1]
        group1_anger = [np.mean([step[i] for i in range(group_size)]) for step in self.history['anger_levels']]
        group2_anger = [np.mean([step[i] for i in range(group_size, 2*group_size)]) for step in self.history['anger_levels']]
        group3_anger = [np.mean([step[i] for i in range(2*group_size, self.num_users)]) for step in self.history['anger_levels']]
        
        ax2.plot(steps, group1_anger, label='賛成派', linewidth=2)
        ax2.plot(steps, group2_anger, label='反対派', linewidth=2)
        ax2.plot(steps, group3_anger, label='中立派', linewidth=2)
        ax2.set_title('グループ別怒りレベル')
        ax2.set_xlabel('ステップ')
        ax2.set_ylabel('怒り')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # エンゲージメント
        ax3 = axes[1, 0]
        ax3.plot(steps, self.history['engagement'], 'purple', linewidth=2)
        ax3.fill_between(steps, 0, self.history['engagement'], alpha=0.3, color='purple')
        ax3.set_title('総エンゲージメント')
        ax3.set_xlabel('ステップ')
        ax3.set_ylabel('エンゲージメント')
        ax3.grid(True, alpha=0.3)
        
        # 分極化
        ax4 = axes[1, 1]
        ax4.plot(steps, self.history['polarization'], 'orange', linewidth=2)
        ax4.fill_between(steps, 0, self.history['polarization'], alpha=0.3, color='orange')
        ax4.set_title('意見の分極化')
        ax4.set_xlabel('ステップ')
        ax4.set_ylabel('分極化度')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('sns_flame_wars_analysis.png', dpi=150)
        print("\n📊 可視化結果を保存: sns_flame_wars_analysis.png")
        plt.show()


class WorkplaceHarassmentAnalysis:
    """職場パワハラ分析
    
    権力勾配のある職場でのハラスメント構造をモデル化
    """
    
    def __init__(self):
        self.boss = None
        self.victim = None
        self.colleagues: List[HumanAgent] = []
        self.all_agents = []
        self.history = {
            'victim_stress': [],
            'victim_core_kappa': [],
            'boss_anger': [],
            'colleagues_fear': [],
        }
        
    def setup(self):
        """セットアップ"""
        print("\n" + "="*60)
        print("分析: 職場パワーハラスメント")
        print("="*60)
        print("\n💼 権力勾配のある職場でのハラスメント...")
        
        # 上司（高いUPPER κ、権威主義的）
        self.boss = HumanAgent()
        self.boss.state.kappa[HumanLayer.UPPER.value] = 3.5  # 強い権威意識
        self.boss.state.kappa[HumanLayer.CORE.value] = 2.0
        self.boss.state.E[HumanLayer.BASE.value] = 2.0  # イライラ
        
        # 被害者（低い抵抗力）
        self.victim = HumanAgent()
        self.victim.state.kappa[HumanLayer.CORE.value] = 1.5  # 中程度の規範意識
        self.victim.state.kappa[HumanLayer.BASE.value] = 1.0
        
        # 同僚たち（傍観者）
        num_colleagues = 5
        for i in range(num_colleagues):
            colleague = HumanAgent()
            colleague.state.kappa[HumanLayer.CORE.value] = np.random.uniform(1.2, 1.8)
            self.colleagues.append(colleague)
        
        self.all_agents = [self.boss, self.victim] + self.colleagues
        
        # 関係性マトリクス
        # 上司→被害者: 強い負の影響
        # 被害者→上司: 弱い影響（服従）
        # 同僚→被害者: 同情（弱い協力）
        num_agents = len(self.all_agents)
        relation_matrix = np.zeros((num_agents, num_agents))
        
        # 上司→被害者
        relation_matrix[1, 0] = 0.9  # 被害者は上司に強く影響される
        relation_matrix[0, 1] = 0.1  # 上司は被害者にあまり影響されない
        
        # 同僚→被害者（同情）
        for i in range(2, num_agents):
            relation_matrix[1, i] = 0.3
            relation_matrix[i, 1] = 0.4
        
        # 同僚→上司（恐怖）
        for i in range(2, num_agents):
            relation_matrix[i, 0] = 0.6
            relation_matrix[0, i] = 0.2
        
        relationships = RelationshipMatrix(matrix=relation_matrix)
        coupling_params = SocialCouplingParams()
        coupling_params.zeta_base = 0.12  # 恐怖の伝染
        
        self.society = SocialDynamicsEngine(
            agents=self.all_agents,
            relationships=relationships,
            params=coupling_params
        )
        
        print("  上司: 権威主義的、高圧的")
        print("  被害者: 標的にされた社員")
        print(f"  同僚: {num_colleagues}人の傍観者")
        
    def run(self, num_steps: int = 150):
        """実行"""
        print(f"\nシミュレーション開始（{num_steps}ステップ）...")
        
        for step in range(num_steps):
            # 記録
            self.history['victim_stress'].append(self.victim.state.E[HumanLayer.BASE.value])
            self.history['victim_core_kappa'].append(self.victim.state.kappa[HumanLayer.CORE.value])
            self.history['boss_anger'].append(self.boss.state.E[HumanLayer.BASE.value])
            
            colleague_fear = np.mean([c.state.E[HumanLayer.BASE.value] for c in self.colleagues])
            self.history['colleagues_fear'].append(colleague_fear)
            
            # 上司の圧力
            boss_pressure = HumanPressure()
            boss_pressure.upper = np.random.uniform(1.0, 2.0)  # 権威維持
            boss_pressure.base = np.random.uniform(1.5, 3.0)  # イライラ
            self.boss.step(boss_pressure)
            
            # 被害者への直接的なハラスメント
            victim_pressure = HumanPressure()
            
            if step < 30:
                # 初期: まだ穏やか
                victim_pressure.base = np.random.uniform(1.0, 2.0)
                victim_pressure.core = np.random.uniform(0.5, 1.0)
                
            elif step < 80:
                # ハラスメント開始
                if step == 30:
                    print(f"\nStep {step}: ⚠️ ハラスメント開始...")
                victim_pressure.base = np.random.uniform(3.0, 6.0)  # 強いストレス
                victim_pressure.core = np.random.uniform(2.0, 4.0)  # 規範との葛藤
                
            else:
                # 慢性化
                if step == 80:
                    print(f"Step {step}: 😞 ハラスメントの慢性化...")
                victim_pressure.base = np.random.uniform(4.0, 7.0)
                victim_pressure.core = np.random.uniform(2.0, 5.0)
            
            self.victim.step(victim_pressure)
            
            # 同僚たち
            colleague_pressure = HumanPressure()
            colleague_pressure.base = np.random.uniform(0.5, 1.5)  # 目撃による不快感
            colleague_pressure.core = np.random.uniform(1.0, 2.0)  # 何もできない葛藤
            
            for colleague in self.colleagues:
                colleague.step(colleague_pressure)
            
            # 社会的相互作用
            self.society.step()
            
            if (step + 1) % 30 == 0:
                print(f"  Step {step+1}: 被害者ストレス = {self.history['victim_stress'][-1]:.2f}")
        
        print("\n✅ シミュレーション完了")
        
    def visualize(self):
        """可視化"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('職場パワーハラスメント分析', fontsize=16, fontweight='bold')
        
        steps = range(len(self.history['victim_stress']))
        
        # 被害者のストレス
        ax1 = axes[0, 0]
        ax1.plot(steps, self.history['victim_stress'], 'r-', linewidth=2)
        ax1.fill_between(steps, 0, self.history['victim_stress'], alpha=0.3, color='red')
        ax1.set_title('被害者のストレスレベル')
        ax1.set_xlabel('ステップ')
        ax1.set_ylabel('ストレス (E_BASE)')
        ax1.grid(True, alpha=0.3)
        
        # 被害者の規範意識の変化
        ax2 = axes[0, 1]
        ax2.plot(steps, self.history['victim_core_kappa'], 'blue', linewidth=2)
        ax2.set_title('被害者の規範意識（自尊心）')
        ax2.set_xlabel('ステップ')
        ax2.set_ylabel('κ_CORE')
        ax2.grid(True, alpha=0.3)
        
        # 上司の怒り
        ax3 = axes[1, 0]
        ax3.plot(steps, self.history['boss_anger'], 'orange', linewidth=2)
        ax3.set_title('上司の怒りレベル')
        ax3.set_xlabel('ステップ')
        ax3.set_ylabel('怒り (E_BASE)')
        ax3.grid(True, alpha=0.3)
        
        # 同僚の恐怖
        ax4 = axes[1, 1]
        ax4.plot(steps, self.history['colleagues_fear'], 'purple', linewidth=2)
        ax4.set_title('同僚の恐怖レベル')
        ax4.set_xlabel('ステップ')
        ax4.set_ylabel('恐怖 (E_BASE)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('workplace_harassment_analysis.png', dpi=150)
        print("\n📊 可視化結果を保存: workplace_harassment_analysis.png")
        plt.show()


def main():
    """メイン実行"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║          現代社会問題分析 with SSD Engine                      ║
║          Modern Social Issues Analysis                         ║
╚════════════════════════════════════════════════════════════════╝

現実の社会問題をSSD理論で分析:

1. SNS炎上現象
   - 批判の連鎖と感情の増幅

2. 職場パワーハラスメント
   - 権力勾配と被害者の心理変化
    """)
    
    print("\n実行する分析を選択してください:")
    print("1: SNS炎上現象")
    print("2: 職場パワーハラスメント")
    print("3: 両方実行")
    
    choice = input("\n選択 (1-3): ").strip()
    
    if choice == '1' or choice == '3':
        sns_analysis = SNSFlameWarsAnalysis()
        sns_analysis.setup()
        sns_analysis.run()
        sns_analysis.visualize()
        
        if choice == '3':
            print("\n" + "="*60)
            input("次の分析に進むにはEnterキーを押してください...")
    
    if choice == '2' or choice == '3':
        harassment_analysis = WorkplaceHarassmentAnalysis()
        harassment_analysis.setup()
        harassment_analysis.run()
        harassment_analysis.visualize()
    
    print("\n✅ すべての分析が完了しました！")


if __name__ == "__main__":
    main()
