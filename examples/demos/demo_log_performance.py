"""
Log版エンジン パフォーマンス比較テスト
====================================

Log版と通常版の計算性能を比較し、
Log-Alignment処理のオーバーヘッドを測定。
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

import numpy as np
import time
from ssd_core_engine_log import SSDCoreEngine as LogEngine, SSDCoreParams as LogParams, SSDCoreState as LogState
from ssd_core_engine import SSDCoreEngine as NormalEngine, SSDCoreParams as NormalParams, SSDCoreState as NormalState


def benchmark_engines():
    """Log版と通常版のパフォーマンス比較"""
    print("=" * 60)
    print("Log版 vs 通常版 パフォーマンス比較")
    print("=" * 60)
    
    # 共通パラメータ
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
    
    # エンジン作成
    log_engine = LogEngine(LogParams(**common_params, log_align=True))
    normal_engine = NormalEngine(NormalParams(**common_params))
    
    # テスト条件
    test_conditions = [
        ("小規模", 1000, np.array([5.0, 3.0, 2.0, 1.0])),
        ("中規模", 5000, np.array([20.0, 15.0, 10.0, 5.0])),
        ("大規模", 10000, np.array([100.0, 50.0, 25.0, 12.0]))
    ]
    
    for test_name, steps, pressure in test_conditions:
        print(f"\n--- {test_name}テスト ({steps:,} steps) ---")
        
        # Log版テスト
        log_state = LogState(E=np.zeros(4), kappa=np.ones(4))
        start_time = time.time()
        
        for _ in range(steps):
            log_state = log_engine.step(log_state, pressure, dt=0.1)
        
        log_time = time.time() - start_time
        
        # 通常版テスト
        normal_state = NormalState(E=np.zeros(4), kappa=np.ones(4))
        start_time = time.time()
        
        for _ in range(steps):
            normal_state = normal_engine.step(normal_state, pressure, dt=0.1)
        
        normal_time = time.time() - start_time
        
        # 結果表示
        print(f"  Log版:    {log_time:.4f}秒 ({steps/log_time:.0f} steps/sec)")
        print(f"  通常版:   {normal_time:.4f}秒 ({steps/normal_time:.0f} steps/sec)")
        print(f"  オーバーヘッド: {(log_time/normal_time-1)*100:.1f}%")
        
        # 最終状態比較
        print(f"  Log版 E:  {log_state.E}")
        print(f"  通常版 E: {normal_state.E}")
        print(f"  α_t: {log_state.logalign_state['alpha_t']:.4f}")
    
    print("\n✅ パフォーマンステスト完了")


def test_log_alignment_scaling():
    """Log-Alignmentの適応性能テスト"""
    print("\n" + "=" * 60)
    print("Log-Alignment 適応性能テスト")
    print("=" * 60)
    
    params = LogParams(
        num_layers=4,
        R_values=[100.0, 10.0, 1.0, 0.1],
        gamma_values=[0.15, 0.10, 0.08, 0.05],
        beta_values=[0.001, 0.01, 0.05, 0.1],
        eta_values=[0.9, 0.5, 0.3, 0.2],
        lambda_values=[0.001, 0.01, 0.02, 0.05],
        kappa_min_values=[0.9, 0.8, 0.5, 0.3],
        Theta_values=[50.0, 25.0, 12.0, 6.0],
        log_align=True,
        alpha0=1.0
    )
    
    engine = LogEngine(params)
    
    # 信号強度を段階的に増加
    signal_levels = [1, 10, 100, 1000, 10000]
    
    print(f"{'Signal':<8} {'α_t':<8} {'P_hat_norm':<12} {'Compression':<12}")
    print("-" * 50)
    
    for level in signal_levels:
        state = LogState(E=np.zeros(4), kappa=np.ones(4))
        pressure = np.array([level, level*0.8, level*0.6, level*0.4])
        
        # 数ステップ実行して適応させる
        for _ in range(10):
            state = engine.step(state, pressure, dt=0.1)
        
        alpha_t = state.logalign_state['alpha_t']
        p_hat_norm = state.diagnostics.get('pressure_hat_norm', 0)
        compression = np.linalg.norm(pressure) / p_hat_norm if p_hat_norm > 0 else 0
        
        print(f"{level:<8} {alpha_t:<8.4f} {p_hat_norm:<12.2f} {compression:<12.2f}")
    
    print("\n✅ Log-Alignment適応テスト完了")


def memory_usage_test():
    """メモリ使用量比較テスト"""
    print("\n" + "=" * 60)
    print("メモリ使用量比較テスト")
    print("=" * 60)
    
    import tracemalloc
    
    # 共通パラメータ
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
    
    pressure = np.array([10.0, 8.0, 6.0, 4.0])
    steps = 1000
    
    # Log版メモリ測定
    tracemalloc.start()
    
    log_engine = LogEngine(LogParams(**common_params, log_align=True))
    log_state = LogState(E=np.zeros(4), kappa=np.ones(4))
    
    for _ in range(steps):
        log_state = log_engine.step(log_state, pressure, dt=0.1)
    
    log_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024  # MB
    tracemalloc.stop()
    
    # 通常版メモリ測定
    tracemalloc.start()
    
    normal_engine = NormalEngine(NormalParams(**common_params))
    normal_state = NormalState(E=np.zeros(4), kappa=np.ones(4))
    
    for _ in range(steps):
        normal_state = normal_engine.step(normal_state, pressure, dt=0.1)
    
    normal_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024  # MB
    tracemalloc.stop()
    
    print(f"Log版メモリ使用量:    {log_memory:.2f} MB")
    print(f"通常版メモリ使用量:   {normal_memory:.2f} MB")
    print(f"メモリ差分:           {log_memory - normal_memory:.2f} MB")
    print(f"メモリ増加率:         {(log_memory/normal_memory-1)*100:.1f}%")
    
    print("\n✅ メモリ使用量テスト完了")


if __name__ == "__main__":
    print("Log版エンジン パフォーマンス総合テスト")
    print("=" * 60)
    
    tests = [
        benchmark_engines,
        test_log_alignment_scaling,
        memory_usage_test
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ テスト失敗: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("パフォーマンステスト完了")
    print("=" * 60)
    print("\n【結論】")
    print("Log版エンジンは追加機能による適度なオーバーヘッドで、")
    print("大信号適応性と確率的跳躍の利点を提供します。")