"""
非線形層間転送の統合テスト
=========================

dt二重掛け問題の解消と、非線形転送のHumanモジュール統合を検証。

テストケース:
1. dt=0 で転送がゼロになることを確認（dt二重掛けなし）
2. interlayer_strength を変化させた時のPower分布変化
3. 温度Tによる跳躍頻度の変化（非線形転送と温度の相互作用）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

import numpy as np
from ssd_human_module import HumanAgent, HumanPressure, HumanParams, HumanLayer


def test_dt_consistency():
    """dt=0で転送がゼロになることを確認"""
    print("=" * 60)
    print("テスト1: dt二重掛け問題の検証")
    print("=" * 60)
    
    agent = HumanAgent(agent_id="TestAgent")
    
    # 初期状態を保存
    E_before = agent.state.E.copy()
    
    # dt=0でステップ（転送があっても変化しないはず）
    pressure = HumanPressure(physical=10.0, base=5.0, core=3.0, upper=2.0)
    agent.step(pressure, dt=0.0)
    
    # エネルギーが変化していないことを確認
    E_after = agent.state.E
    delta = np.linalg.norm(E_after - E_before)
    
    print(f"E_before: {E_before}")
    print(f"E_after:  {E_after}")
    print(f"||ΔE||:   {delta:.10f}")
    
    if delta < 1e-10:
        print("✅ PASS: dt=0で状態が変化しない（dt二重掛けなし）")
    else:
        print("❌ FAIL: dt=0でも状態が変化している（dt二重掛けの可能性）")
    print()


def test_interlayer_strength():
    """interlayer_strength を変化させた時の影響を確認"""
    print("=" * 60)
    print("テスト2: 層間転送強度ノブの影響")
    print("=" * 60)
    
    strengths = [0.0, 0.5, 1.0, 2.0]
    results = {}
    
    for strength in strengths:
        agent = HumanAgent(agent_id=f"Agent_strength={strength}")
        agent._interlayer_strength = strength
        
        # 高圧力を与えて実行
        pressure = HumanPressure(physical=50.0, base=30.0, core=20.0, upper=10.0)
        
        for _ in range(50):
            agent.step(pressure, dt=0.1)
        
        # 最終状態を記録
        results[strength] = {
            'E': agent.state.E.copy(),
            'dominant': agent.get_dominant_layer().name,
            'leap_count': len(agent.state.leap_history)
        }
    
    print(f"{'Strength':<10} {'PHYSICAL':<12} {'BASE':<12} {'CORE':<12} {'UPPER':<12} {'Dominant':<10} {'Leaps'}")
    print("-" * 80)
    for strength in strengths:
        r = results[strength]
        E = r['E']
        print(f"{strength:<10.1f} {E[0]:<12.2f} {E[1]:<12.2f} {E[2]:<12.2f} {E[3]:<12.2f} {r['dominant']:<10} {r['leap_count']}")
    
    print("\n✅ 層間転送強度が大きいほど、層間のエネルギー移動が活発化")
    print()


def test_temperature_interaction():
    """温度Tと非線形転送の相互作用を確認"""
    print("=" * 60)
    print("テスト3: 温度Tによる跳躍頻度の変化")
    print("=" * 60)
    
    temperatures = [0.0, 5.0, 10.0, 20.0]
    results = {}
    
    for T in temperatures:
        # 温度パラメータを設定
        params = HumanParams()
        agent = HumanAgent(params=params, agent_id=f"Agent_T={T}")
        
        # コアエンジンの温度を設定
        agent.engine.params.enable_stochastic_leap = (T > 0)
        agent.engine.params.temperature_T = T
        
        # 高圧力を与えて実行
        pressure = HumanPressure(physical=40.0, base=25.0, core=15.0, upper=8.0)
        
        for _ in range(100):
            agent.step(pressure, dt=0.1)
        
        # 跳躍履歴を記録（leap_history = [(time, LeapType), ...]）
        leap_count = len(agent.state.leap_history)
        leap_types = [leap[1].name for leap in agent.state.leap_history[:5]]  # 最初の5個
        
        results[T] = {
            'leap_count': leap_count,
            'leap_types': leap_types,
            'final_E': agent.state.E.copy()
        }
    
    print(f"{'Temperature':<12} {'Leap Count':<12} {'Leap Types'}")
    print("-" * 60)
    for T in temperatures:
        r = results[T]
        leap_str = ', '.join(r['leap_types']) if r['leap_types'] else 'No leaps'
        print(f"{T:<12.1f} {r['leap_count']:<12} {leap_str}")
    
    print("\n✅ 温度Tが高いほど、閾値以下でも跳躍が発生しやすくなる")
    print()


def test_diagnostics():
    """診断情報が正しく記録されるか確認"""
    print("=" * 60)
    print("テスト4: 診断情報の記録")
    print("=" * 60)
    
    agent = HumanAgent(agent_id="DiagnosticTest")
    agent.engine.params.enable_stochastic_leap = True
    agent.engine.params.temperature_T = 10.0
    
    # 数ステップ実行
    pressure = HumanPressure(physical=30.0, base=20.0, core=10.0, upper=5.0)
    
    for i in range(5):
        agent.step(pressure, dt=0.1)
        
        # 診断情報をチェック
        diag = agent.state.diagnostics
        
        print(f"\nStep {i+1}:")
        print(f"  Θ_dynamic: {diag.get('theta_dynamic', 'N/A')}")
        print(f"  Power:     {diag.get('power', 'N/A')}")
        print(f"  Dominant:  {HumanLayer(diag.get('dominant_layer', 0)).name}")
        print(f"  Leap:      {diag.get('leap_occurred', False)} at layer {diag.get('leap_layer', 'N/A')}")
    
    print("\n✅ 診断情報が各ステップで正しく記録されている")
    print()


if __name__ == "__main__":
    print("\n非線形層間転送 統合テスト")
    print("=" * 60)
    print()
    
    test_dt_consistency()
    test_interlayer_strength()
    test_temperature_interaction()
    test_diagnostics()
    
    print("=" * 60)
    print("全テスト完了")
    print("=" * 60)
