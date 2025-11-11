"""
高感度版LEAP実験の詳細分析
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.ssd_core_engine import SSDCoreEngine, SSDCoreParams
from kaiji_debt_hell_roulette_sensitive import create_kaiji_sensitive_params, KaijiSensitivePlayer

def analyze_leap_conditions():
    """LEAP条件を詳細分析"""
    params = create_kaiji_sensitive_params()
    
    print("="*80)
    print("🔬 高感度版LEAP条件分析")
    print("="*80)
    
    print(f"📊 Theta閾値: {params.Theta_values}")
    print(f"🎯 最低LEAP閾値: {min(params.Theta_values)}")
    print(f"⚡ Dynamic Theta感度: {params.theta_sensitivity}")
    print(f"🔋 Gamma値: {params.gamma_values}")
    print(f"📉 Beta値: {params.beta_values}")
    
    # 理論的最大エネルギー計算
    max_gamma = max(params.gamma_values)
    min_beta = min(params.beta_values)
    
    # 最大絶望度3.0での理論値
    max_despair = 3.0
    theoretical_max_energy = max_gamma * max_despair / min_beta
    
    print(f"\n🧮 理論計算:")
    print(f"   最大絶望度: {max_despair}")
    print(f"   最大Gamma: {max_gamma}")
    print(f"   最小Beta: {min_beta}")
    print(f"   理論最大エネルギー: {theoretical_max_energy:.2f}")
    print(f"   最小LEAP閾値: {min(params.Theta_values)}")
    print(f"   LEAP可能性: {'✅ 可能' if theoretical_max_energy > min(params.Theta_values) else '❌ 不可能'}")
    
    # Dynamic Theta効果
    print(f"\n🔄 Dynamic Theta効果:")
    structural_influence = 0.5  # 仮定値
    effective_theta = min(params.Theta_values) * (1 - params.theta_sensitivity * structural_influence)
    print(f"   構造影響度: {structural_influence}")
    print(f"   有効Theta: {effective_theta:.2f}")
    print(f"   Dynamic後LEAP可能性: {'✅ 可能' if theoretical_max_energy > effective_theta else '❌ 不可能'}")
    
    # 実験シミュレーション
    print(f"\n🧪 簡易シミュレーション:")
    
    # 極限状態テスト
    for despair in [1.0, 2.0, 3.0, 5.0, 8.0, 10.0]:
        # 人工的に高エネルギー状態を作成
        energy = max_gamma * despair / min_beta
        
        print(f"   絶望度 {despair}: エネルギー={energy:.2f}, LEAP={'✅' if energy > min(params.Theta_values) else '❌'}")
    
    # Log-Alignment効果の調査
    print(f"\n📈 Log-Alignment効果分析:")
    print(f"   Log版では p̂ = sign(p)·log(1+α_t|p|)/log(b)")
    print(f"   Alpha0値: {params.alpha0}")
    print(f"   Log Base: {params.log_base}")
    
    # 圧力値での実際の抑制効果
    for pressure in [50.0, 100.0, 200.0, 500.0, 1000.0]:
        alpha = params.alpha0
        log_base = params.log_base
        suppressed = np.log(1 + alpha * pressure) / np.log(log_base)
        print(f"   圧力 {pressure} → 抑制後 {suppressed:.2f} (抑制率: {(1-suppressed/pressure)*100:.1f}%)")
        
    print(f"\n💡 結論:")
    print(f"   理論上はLEAP可能だが、Log-Alignmentによる圧力抑制が非常に強力")
    print(f"   実際の心理圧力(~100)が対数関数で大幅に抑制される")
    print(f"   圧力500でも抑制後は約8.7程度に減少")
    print(f"   これがLEAP発生を阻害している主要因と推定")

if __name__ == "__main__":
    analyze_leap_conditions()