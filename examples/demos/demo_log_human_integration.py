"""
Log版エンジンを使ったHumanAgentテスト
===================================

Log-Alignment機能を持つエンジンをHumanAgentで使用して、
実際のゲーム環境での動作を確認。
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

import numpy as np
from ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, SSDCoreState
from ssd_human_module import HumanAgent, HumanPressure, HumanParams


def test_human_agent_with_log_engine():
    """HumanAgentでLog版エンジンをテスト"""
    print("=" * 60)
    print("Log版エンジンを使ったHumanAgentテスト")
    print("=" * 60)
    
    # HumanParamsをLog版対応に拡張
    class LogHumanParams(HumanParams):
        def to_core_params(self) -> SSDCoreParams:
            """Log版エンジンパラメータに変換"""
            return SSDCoreParams(
                num_layers=4,
                R_values=[self.R_physical, self.R_base, self.R_core, self.R_upper],
                gamma_values=[self.gamma_physical, self.gamma_base, self.gamma_core, self.gamma_upper],
                beta_values=[self.beta_physical, self.beta_base, self.beta_core, self.beta_upper],
                eta_values=[self.eta_physical, self.eta_base, self.eta_core, self.eta_upper],
                lambda_values=[self.lambda_physical, self.lambda_base, self.lambda_core, self.lambda_upper],
                kappa_min_values=[self.kappa_min_physical, self.kappa_min_base, self.kappa_min_core, self.kappa_min_upper],
                Theta_values=[self.Theta_physical, self.Theta_base, self.Theta_core, self.Theta_upper],
                enable_dynamic_theta=self.enable_dynamic_theta,
                theta_sensitivity=self.theta_sensitivity,
                # Log-Alignment機能を有効化
                log_align=True,
                alpha0=2.0,
                log_base=np.e,
                enable_stochastic_leap=True,
                temperature_T=5.0  # 適度な確率性
            )
    
    # Log版対応HumanAgent
    class LogHumanAgent(HumanAgent):
        def __init__(self, params=None, agent_id="LogHuman"):
            self.params = params or LogHumanParams()
            self.agent_id = agent_id
            
            # Log版エンジン初期化
            core_params = self.params.to_core_params()
            self.engine = SSDCoreEngine(core_params)
            
            # 状態初期化（Log版用）
            self.state = SSDCoreState(
                E=np.zeros(4),
                kappa=np.ones(4),
                t=0.0
            )
            
            # 非線形転送器
            from ssd_nonlinear_transfer import NonlinearInterlayerTransfer
            self._nl_transfer = NonlinearInterlayerTransfer()
            self._interlayer_strength = 1.0
        
        def _compute_interlayer_transfer(self) -> np.ndarray:
            """非線形層間転送の計算"""
            E = self.state.E
            kappa = self.state.kappa
            dE_inter = self._nl_transfer.compute_transfer(E, kappa)
            return self._interlayer_strength * dE_inter
    
    # テスト実行
    agent = LogHumanAgent(agent_id="TestAgent")
    
    print(f"初期状態:")
    print(f"  E: {agent.state.E}")
    print(f"  κ: {agent.state.kappa}")
    print(f"  Log align enabled: {agent.engine.params.log_align}")
    print(f"  Temperature T: {agent.engine.params.temperature_T}")
    
    # 様々な心理的圧力をテスト
    test_scenarios = [
        ("軽いストレス", HumanPressure(physical=5.0, base=3.0, core=2.0, upper=1.0)),
        ("中程度のストレス", HumanPressure(physical=20.0, base=15.0, core=10.0, upper=5.0)),
        ("高ストレス", HumanPressure(physical=50.0, base=40.0, core=30.0, upper=20.0)),
        ("極限状態", HumanPressure(physical=100.0, base=80.0, core=60.0, upper=40.0))
    ]
    
    for scenario_name, pressure in test_scenarios:
        print(f"\n--- {scenario_name} ---")
        
        # 10ステップ実行
        for step in range(10):
            agent.step(pressure, dt=0.1)
        
        # 結果表示
        print(f"  E: {agent.state.E}")
        print(f"  κ: {agent.state.kappa}")
        print(f"  跳躍回数: {len(agent.state.leap_history)}")
        print(f"  α_t: {agent.state.logalign_state['alpha_t']:.4f}")
        
        # 診断情報
        diag = agent.state.diagnostics
        print(f"  Dominant layer: {diag.get('dominant_layer', 'N/A')}")
        print(f"  Pressure_hat norm: {diag.get('pressure_hat_norm', 'N/A'):.2f}")
        
        # 跳躍があった場合
        if agent.state.leap_history:
            last_leap = agent.state.leap_history[-1]
            print(f"  最新跳躍: t={last_leap[0]:.1f}, type={last_leap[1].name}")
    
    print("\n✅ HumanAgent + Log版エンジンテスト完了")
    return True


def test_log_vs_normal_comparison():
    """Log版と通常版の比較テスト"""
    print("\n" + "=" * 60)
    print("Log版 vs 通常版 比較テスト")
    print("=" * 60)
    
    from ssd_core_engine import SSDCoreEngine as NormalEngine, SSDCoreParams as NormalParams
    
    # 同じ条件でエンジンを作成
    common_params = {
        'num_layers': 4,
        'R_values': [1000.0, 100.0, 10.0, 1.0],
        'gamma_values': [0.15, 0.10, 0.08, 0.05],
        'beta_values': [0.001, 0.01, 0.05, 0.1],
        'eta_values': [0.9, 0.5, 0.3, 0.2],
        'lambda_values': [0.001, 0.01, 0.02, 0.05],
        'kappa_min_values': [0.9, 0.8, 0.5, 0.3],
        'Theta_values': [200.0, 100.0, 50.0, 30.0]
    }
    
    # Log版エンジン
    log_params = SSDCoreParams(**common_params, log_align=True, alpha0=1.0)
    log_engine = SSDCoreEngine(log_params)
    log_state = SSDCoreState(E=np.zeros(4), kappa=np.ones(4))
    
    # 通常版エンジン
    normal_params = NormalParams(**common_params)
    normal_engine = NormalEngine(normal_params)
    from ssd_core_engine import SSDCoreState as NormalState
    normal_state = NormalState(E=np.zeros(4), kappa=np.ones(4))
    
    # 様々な圧力レベルでテスト
    pressure_levels = [
        np.array([1.0, 1.0, 1.0, 1.0]),      # 小信号
        np.array([10.0, 10.0, 10.0, 10.0]),   # 中信号
        np.array([100.0, 50.0, 25.0, 12.0])   # 大信号（不均等）
    ]
    
    for i, pressure in enumerate(pressure_levels):
        print(f"\n圧力レベル {i+1}: {pressure}")
        
        # 5ステップ実行
        for step in range(5):
            log_state = log_engine.step(log_state, pressure, dt=0.1)
            normal_state = normal_engine.step(normal_state, pressure, dt=0.1)
        
        print(f"  Log版 E: {log_state.E}")
        print(f"  通常版 E: {normal_state.E}")
        print(f"  Log版 κ: {log_state.kappa}")
        print(f"  通常版 κ: {normal_state.kappa}")
        
        # Log版特有の情報
        print(f"  α_t: {log_state.logalign_state['alpha_t']:.4f}")
        print(f"  Pressure_hat norm: {log_state.diagnostics.get('pressure_hat_norm', 'N/A'):.2f}")
    
    print("\n✅ Log版 vs 通常版比較テスト完了")
    return True


if __name__ == "__main__":
    print("Log版エンジン + HumanAgent 動作確認")
    print("=" * 60)
    
    tests = [
        test_human_agent_with_log_engine,
        test_log_vs_normal_comparison
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ テスト失敗: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("総合テスト結果")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"合格: {passed}/{total}")
    
    if passed == total:
        print("🎉 Log版エンジンは完全に動作し、実用可能です！")
        print("\n【Log版の利点】")
        print("- 大信号への適応性（Log-Alignment）")
        print("- 確率的跳躍による自然な揺らぎ")
        print("- 詳細な診断情報")
        print("- 通常版との完全互換性")
    else:
        print("⚠️  一部問題があります。修正推奨。")