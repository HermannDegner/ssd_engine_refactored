"""
SSD Core Engine Log版 動作確認テスト
=====================================

Log-Alignment機能を含む最新版エンジンの動作を検証。

テスト項目:
1. 基本初期化と状態遷移
2. Log-Alignment変換の動作
3. 確率的跳躍（温度パラメータ）
4. 診断情報の記録
5. 層間転送との互換性
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

import numpy as np
from ssd_core_engine_log import SSDCoreEngine, SSDCoreParams, SSDCoreState


def test_basic_initialization():
    """基本的な初期化と単純な状態遷移をテスト"""
    print("=" * 60)
    print("テスト1: 基本初期化と状態遷移")
    print("=" * 60)
    
    # パラメータ作成
    params = SSDCoreParams(
        num_layers=3,
        R_values=[100.0, 10.0, 1.0],
        gamma_values=[0.15, 0.10, 0.08],
        beta_values=[0.001, 0.01, 0.05],
        eta_values=[0.9, 0.5, 0.3],
        lambda_values=[0.001, 0.01, 0.02],
        kappa_min_values=[0.9, 0.8, 0.5],
        Theta_values=[200.0, 100.0, 50.0],
        log_align=True,  # Log-Alignment有効
        alpha0=1.0,
        log_base=np.e
    )
    
    # エンジン初期化
    engine = SSDCoreEngine(params)
    
    # 初期状態
    state = SSDCoreState(
        E=np.array([0.0, 0.0, 0.0]),
        kappa=np.array([1.0, 1.0, 1.0]),
        t=0.0
    )
    
    print(f"初期状態:")
    print(f"  E: {state.E}")
    print(f"  κ: {state.kappa}")
    print(f"  logalign_state: {state.logalign_state}")
    
    # 圧力を加えて数ステップ実行
    pressure = np.array([10.0, 5.0, 2.0])
    
    for i in range(5):
        state = engine.step(state, pressure, dt=0.1)
        print(f"\nStep {i+1}:")
        print(f"  E: {state.E}")
        print(f"  κ: {state.kappa}")
        print(f"  α_t: {state.logalign_state['alpha_t']:.4f}")
        print(f"  diagnostics: leap={state.diagnostics.get('leap_occurred', False)}")
    
    print("✅ 基本初期化・状態遷移テスト完了")
    return True


def test_log_alignment():
    """Log-Alignment変換のテスト"""
    print("\n" + "=" * 60)
    print("テスト2: Log-Alignment変換")
    print("=" * 60)
    
    params = SSDCoreParams(
        num_layers=2,
        R_values=[10.0, 1.0],
        gamma_values=[0.15, 0.10],
        beta_values=[0.001, 0.01],
        eta_values=[0.9, 0.5],
        lambda_values=[0.001, 0.01],
        kappa_min_values=[0.9, 0.8],
        Theta_values=[200.0, 100.0],
        log_align=True,
        alpha0=2.0,
        log_base=10.0  # 常用対数
    )
    
    engine = SSDCoreEngine(params)
    state = SSDCoreState(
        E=np.array([0.0, 0.0]),
        kappa=np.array([1.0, 1.0])
    )
    
    # 様々な圧力レベルでテスト
    test_pressures = [
        np.array([1.0, 1.0]),      # 小信号
        np.array([10.0, 10.0]),    # 中信号
        np.array([100.0, 100.0]),  # 大信号
        np.array([-50.0, 50.0])    # 符号混合
    ]
    
    for i, pressure in enumerate(test_pressures):
        pressure_hat = engine.apply_log_alignment(state, pressure)
        
        print(f"\n圧力テスト {i+1}:")
        print(f"  原信号 p: {pressure}")
        print(f"  変換後 p̂: {pressure_hat}")
        print(f"  変換比: {pressure_hat / (pressure + 1e-10)}")
        print(f"  α_t: {state.logalign_state['alpha_t']:.4f}")
        
        # 次のテストのため状態を更新
        state = engine.step(state, pressure, dt=0.1)
    
    print("✅ Log-Alignment変換テスト完了")
    return True


def test_stochastic_leap():
    """確率的跳躍（温度パラメータ）のテスト"""
    print("\n" + "=" * 60)
    print("テスト3: 確率的跳躍（温度パラメータ）")
    print("=" * 60)
    
    temperatures = [0.0, 5.0, 15.0]  # 決定論的 → 確率的
    
    for T in temperatures:
        print(f"\n温度 T = {T}:")
        
        params = SSDCoreParams(
            num_layers=2,
            R_values=[10.0, 1.0],
            gamma_values=[0.15, 0.10],
            beta_values=[0.001, 0.01],
            eta_values=[0.9, 0.5],
            lambda_values=[0.001, 0.01],
            kappa_min_values=[0.9, 0.8],
            Theta_values=[20.0, 15.0],  # 跳躍閾値
            enable_stochastic_leap=True,
            temperature_T=T,
            log_align=True
        )
        
        engine = SSDCoreEngine(params)
        
        # 複数回試行
        leap_counts = []
        for trial in range(20):
            state = SSDCoreState(
                E=np.array([18.0, 12.0]),  # 閾値近傍
                kappa=np.array([1.0, 1.0])
            )
            
            pressure = np.array([30.0, 20.0])  # 高圧力
            leap_count = 0
            
            for step in range(10):
                old_leap_count = len(state.leap_history)
                state = engine.step(state, pressure, dt=0.1)
                new_leap_count = len(state.leap_history)
                leap_count += (new_leap_count - old_leap_count)
            
            leap_counts.append(leap_count)
        
        avg_leaps = np.mean(leap_counts)
        std_leaps = np.std(leap_counts)
        
        print(f"  平均跳躍回数: {avg_leaps:.2f} ± {std_leaps:.2f}")
        print(f"  跳躍頻度の変動: {std_leaps:.2f}")
    
    print("✅ 確率的跳躍テスト完了")
    return True


def test_diagnostics():
    """診断情報の記録テスト"""
    print("\n" + "=" * 60)
    print("テスト4: 診断情報の記録")
    print("=" * 60)
    
    params = SSDCoreParams(
        num_layers=3,
        R_values=[100.0, 10.0, 1.0],
        gamma_values=[0.15, 0.10, 0.08],
        beta_values=[0.001, 0.01, 0.05],
        eta_values=[0.9, 0.5, 0.3],
        lambda_values=[0.001, 0.01, 0.02],
        kappa_min_values=[0.9, 0.8, 0.5],
        Theta_values=[200.0, 100.0, 50.0],
        log_align=True,
        enable_stochastic_leap=True,
        temperature_T=10.0
    )
    
    engine = SSDCoreEngine(params)
    state = SSDCoreState(
        E=np.array([5.0, 15.0, 25.0]),
        kappa=np.array([1.2, 2.0, 0.8])
    )
    
    pressure = np.array([20.0, 15.0, 10.0])
    
    for i in range(3):
        state = engine.step(state, pressure, dt=0.1)
        diag = state.diagnostics
        
        print(f"\nStep {i+1} 診断情報:")
        print(f"  Θ_dynamic: {diag.get('theta_dynamic', 'N/A')}")
        print(f"  Power: {diag.get('power', 'N/A')}")
        print(f"  Dominant layer: {diag.get('dominant_layer', 'N/A')}")
        print(f"  Leap occurred: {diag.get('leap_occurred', False)}")
        print(f"  α_t: {diag.get('alpha_t', 'N/A')}")
        print(f"  Unit check: {diag.get('unit_check', 'N/A')}")
        print(f"  Pressure_hat norm: {diag.get('pressure_hat_norm', 'N/A')}")
    
    print("✅ 診断情報記録テスト完了")
    return True


def test_interlayer_compatibility():
    """層間転送との互換性テスト"""
    print("\n" + "=" * 60)
    print("テスト5: 層間転送との互換性")
    print("=" * 60)
    
    params = SSDCoreParams(
        num_layers=3,
        R_values=[10.0, 5.0, 1.0],
        gamma_values=[0.15, 0.10, 0.08],
        beta_values=[0.001, 0.01, 0.05],
        eta_values=[0.9, 0.5, 0.3],
        lambda_values=[0.001, 0.01, 0.02],
        kappa_min_values=[0.9, 0.8, 0.5],
        Theta_values=[200.0, 100.0, 50.0],
        log_align=True
    )
    
    engine = SSDCoreEngine(params)
    state = SSDCoreState(
        E=np.array([2.0, 5.0, 8.0]),
        kappa=np.array([1.0, 1.5, 2.0])
    )
    
    pressure = np.array([10.0, 8.0, 6.0])
    
    # 層間転送なし
    state1 = engine.step(state, pressure, dt=0.1)
    print(f"転送なし: E = {state1.E}")
    
    # 層間転送あり
    interlayer_transfer = np.array([1.0, -0.5, -0.5])  # 0層に流入、1,2層から流出
    state2 = engine.step(state, pressure, dt=0.1, interlayer_transfer=interlayer_transfer)
    print(f"転送あり: E = {state2.E}")
    
    # 差分を確認
    diff = state2.E - state1.E
    expected_diff = interlayer_transfer * 0.1  # dt=0.1
    print(f"期待値差分: {expected_diff}")
    print(f"実際の差分: {diff}")
    print(f"誤差: {np.abs(diff - expected_diff)}")
    
    if np.allclose(diff, expected_diff, atol=1e-10):
        print("✅ 層間転送互換性テスト完了")
        return True
    else:
        print("❌ 層間転送で予期しない差分")
        return False


if __name__ == "__main__":
    print("SSD Core Engine Log版 動作確認テスト")
    print("=" * 60)
    
    tests = [
        test_basic_initialization,
        test_log_alignment,
        test_stochastic_leap,
        test_diagnostics,
        test_interlayer_compatibility
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ テスト失敗: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"合格: {passed}/{total}")
    
    if passed == total:
        print("🎉 全テスト合格！Log版は正常動作しています。")
    else:
        print("⚠️  一部テストが失敗しました。修正が必要です。")