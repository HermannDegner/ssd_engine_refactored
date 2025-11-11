# -*- coding: utf-8 -*-
"""
SS型（感覚過敏）統合デモ - 論考から実装への橋渡し
==================================================

HSP/SS型の理論的洞察をSSDシステムで実装・検証。

機能:
1. SS型二経路モデル（経路A: 場依存型、経路B: 脅威感受型）
2. ストレス転換ダイナミクス（A→B遷移）
3. 社会・言語KPI計測（CAR, LP, CCL, XAL）
4. カイジ×SS型シミュレーション

理論ベース:
- 感覚過敏 = 微細不整合の検知力↑
- 場依存整合 = 文脈で残差を処理
- ストレス下でのモード切替
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from dataclasses import replace
from core.ssd_core_engine import SSDCoreEngine, SSDCoreParams, SSDCoreState
from extensions.ssd_ss_sensitivity import (
    SSProfile, SSNeuroConfig, SocialLanguageKPI,
    ss_preset, modulate_with_ss, compute_social_language_kpi
)

class SSDSSEngine(SSDCoreEngine):
    """SS型統合SSDエンジン"""
    
    def __init__(self, params: SSDCoreParams, 
                 ss_profile: SSProfile,
                 ss_config: SSNeuroConfig = None):
        super().__init__(params)
        self.base_params = params
        self.ss_profile = ss_profile
        self.ss_config = ss_config or SSNeuroConfig()
        
        # KPI追跡
        self.kpi_history = []
        self.current_stress = 0.0
        
    def step(self, state: SSDCoreState, pressure, dt: float = 0.1) -> SSDCoreState:
        """SS型変調を適用したステップ実行"""
        
        # pressureをndarrayに変換
        if np.isscalar(pressure):
            pressure_array = np.full(self.base_params.num_layers, pressure)
        else:
            pressure_array = np.array(pressure)
            
        # 現在ストレス計算（簡易版：エネルギー蓄積度）
        energy_stress = np.mean(state.E) / np.mean(self.base_params.Theta_values)
        pressure_stress = np.mean(np.abs(pressure_array)) / 100.0  # 正規化
        self.current_stress = min(1.0, (energy_stress + pressure_stress) / 2.0)
        
        # SS型変調適用
        modulated_params, neuro_state, kpi = modulate_with_ss(
            self.base_params, self.ss_profile, self.current_stress,
            ss_config=self.ss_config
        )
        
        # KPI計算（シミュレーション）
        kpi = self._simulate_social_kpi(pressure_array, state)
        self.kpi_history.append(kpi)
        
        # パラメータ置換してステップ実行
        original_params = self.params
        self.params = modulated_params
        result = super().step(state, pressure_array, dt)
        self.params = original_params
        
        return result
    
    def _simulate_social_kpi(self, pressure_array, state) -> SocialLanguageKPI:
        """社会・言語KPIのシミュレーション計算"""
        
        # 情報量推定
        pressure_magnitude = np.linalg.norm(pressure_array)
        explicit_info = pressure_magnitude * (1.0 - self.ss_profile.context_dependency)
        implicit_info = pressure_magnitude * self.ss_profile.context_dependency
        
        # 文脈解決推定
        context_skill = self.ss_profile.ss_level * self.ss_profile.context_dependency
        context_resolved = implicit_info * context_skill
        
        # 総残差推定
        total_residual = np.linalg.norm(state.E) + pressure_magnitude * 0.1
        
        # 推論ステップ推定（文脈依存度に応じて増加）
        inference_steps = int(5 + self.ss_profile.context_dependency * 10)
        
        return compute_social_language_kpi(
            explicit_info, implicit_info, context_resolved, 
            total_residual, inference_steps
        )


def demo_ss_basic_comparison():
    """基本SS型比較デモ"""
    
    print("=" * 80)
    print("🧠✨ SS型（感覚過敏）基本比較デモ")
    print("=" * 80)
    
    # 基本パラメータ
    params = SSDCoreParams(
        temperature_T=37.0,
        enable_stochastic_leap=True,
        G0=0.001, g=0.01,
        Theta_values=[100.0, 80.0, 60.0, 40.0],
        alpha0=1.0
    )
    
    # SS型プロファイル比較
    profiles = {
        "標準型": SSProfile(ss_level=0.0),
        "強感受性": ss_preset("high_ss"),
        "バランス": ss_preset("balanced_ss"),
        "ストレス反応": ss_preset("stress_reactive")
    }
    
    pressure = 50.0  # 中程度圧力
    
    print("\n🔬 SS型別パラメータ変調効果:")
    print("-" * 60)
    
    for name, profile in profiles.items():
        print(f"\n🎯 {name} (SS={profile.ss_level:.1f}):")
        
        # 平常時 (低ストレス)
        modulated, neuro, kpi = modulate_with_ss(params, profile, current_stress=0.1)
        print(f"  平常時:")
        print(f"    感覚ゲイン α0: {params.alpha0:.2f} → {modulated.alpha0:.2f}")
        print(f"    LEAP閾値 Θ[0]: {params.Theta_values[0]:.1f} → {modulated.Theta_values[0]:.1f}")
        print(f"    神経状態: D1={neuro.D1:.2f}, 5HT={neuro._5HT:.2f}, NE={neuro.NE:.2f}")
        
        # 高ストレス時
        modulated, neuro, kpi = modulate_with_ss(params, profile, current_stress=0.8)
        print(f"  高ストレス:")
        print(f"    感覚ゲイン α0: {params.alpha0:.2f} → {modulated.alpha0:.2f}")
        print(f"    LEAP閾値 Θ[0]: {params.Theta_values[0]:.1f} → {modulated.Theta_values[0]:.1f}")
        print(f"    神経状態: D1={neuro.D1:.2f}, 5HT={neuro._5HT:.2f}, NE={neuro.NE:.2f}")


def demo_ss_social_kpi():
    """SS型社会・言語KPI計測デモ"""
    
    print("\n" + "=" * 80)
    print("📊🌍 SS型社会・言語KPI計測デモ")
    print("=" * 80)
    
    params = SSDCoreParams(temperature_T=37.0, alpha0=1.0, G0=0.001, g=0.01)
    
    # SS社会 vs LL社会シミュレーション
    ss_society = ss_preset("high_ss")    # 高コンテクスト・場依存
    ll_society = SSProfile(              # 低コンテクスト・明示的
        ss_level=0.2,
        context_dependency=0.2,
        pathway_balance=0.3
    )
    
    print("\n🌏 社会タイプ別KPI比較:")
    print("-" * 50)
    
    for society_name, profile in [("SS社会（日本型）", ss_society), 
                                  ("LL社会（欧米型）", ll_society)]:
        
        engine = SSDSSEngine(params, profile)
        state = SSDCoreState(E=np.zeros(4), kappa=np.ones(4))
        
        # 複数ステップ実行
        for step in range(5):
            pressure = 40.0 + step * 10.0  # 徐々に圧力増加
            state = engine.step(state, pressure, dt=0.1)
        
        # 最新KPI表示
        kpi = engine.kpi_history[-1] if engine.kpi_history else SocialLanguageKPI()
        
        print(f"\n🎯 {society_name}:")
        print(f"  CAR（場依存整合率）: {kpi.CAR:.3f}")
        print(f"  LP（言語圧力）: {kpi.LP:.3f}") 
        print(f"  CCL（空気コスト）: {kpi.CCL:.1f}")
        print(f"  XAL（異整合変換損失）: {kpi.XAL:.3f}")
        print(f"  現在ストレス水準: {engine.current_stress:.3f}")


def demo_kaiji_ss_progression():
    """カイジ×SS型進行シミュレーション"""
    
    print("\n" + "=" * 80)
    print("🎰🧠 カイジ×SS型借金地獄シミュレーション")
    print("=" * 80)
    
    params = SSDCoreParams(
        temperature_T=37.0, enable_stochastic_leap=True,
        G0=0.001, g=0.01, Theta_values=[80.0, 60.0, 40.0, 30.0]
    )
    
    # カイジのSS型設定（感受性高・ストレス反応強）
    kaiji_ss = SSProfile(
        ss_level=0.7,           # 高感受性
        pathway_balance=0.6,    # ストレス時B経路優位
        context_dependency=0.8, # 場の空気に敏感
        stress_threshold=0.2,   # 低ストレス閾値
        threat_sensitivity=1.8  # 高脅威感受性
    )
    
    engine = SSDSSEngine(params, kaiji_ss)
    state = SSDCoreState(E=np.zeros(4), kappa=np.ones(4))
    
    # 借金地獄進行段階
    stages = [
        ("冷静な計算", 30.0),
        ("初回ベット", 45.0), 
        ("連敗の焦り", 65.0),
        ("絶望的状況", 85.0),
        ("最後の賭け", 95.0)
    ]
    
    print("\n📈 カイジSS型の心理・社会状況変化:")
    print("-" * 60)
    
    for i, (stage_name, pressure) in enumerate(stages):
        print(f"\n🎯 Stage {i+1}: {stage_name} (圧力: {pressure:.1f})")
        
        # 複数ステップ実行
        leap_occurred = False
        for step in range(3):
            state = engine.step(state, pressure, dt=0.1)
            
            if any(E >= T for E, T in zip(state.E, engine.params.Theta_values)):
                print(f"  Step {step+1}: 🚀「ざわ...ざわ...」SS-LEAP! E={state.E[0]:.1f}")
                leap_occurred = True
                break
            else:
                print(f"  Step {step+1}: E={state.E[0]:.1f} (ストレス: {engine.current_stress:.2f})")
        
        # KPI表示
        if engine.kpi_history:
            kpi = engine.kpi_history[-1]
            print(f"  社会KPI: CAR={kpi.CAR:.2f}, CCL={kpi.CCL:.1f}, ストレス={engine.current_stress:.2f}")
        
        if not leap_occurred:
            print(f"  → {stage_name}: SS型感受性による緊張蓄積中...")
        else:
            print(f"  → {stage_name}: SS型特有の感覚過敏が閾値突破！")


def demo_ss_pathway_transition():
    """SS型経路転換デモ"""
    
    print("\n" + "=" * 80)
    print("🔄⚡ SS型経路転換（A→B遷移）デモ")
    print("=" * 80)
    
    params = SSDCoreParams(temperature_T=37.0, alpha0=1.0)
    
    # 経路転換しやすいSS型
    transition_prone = SSProfile(
        ss_level=0.8,
        pathway_balance=0.2,    # 平常時A優位
        stress_threshold=0.3,   # 中程度で転換
        context_dependency=0.9
    )
    
    print("\n🧠 ストレス水準による経路転換パターン:")
    print("-" * 50)
    
    stress_levels = [0.1, 0.2, 0.4, 0.6, 0.8]
    
    for stress in stress_levels:
        modulated, neuro, kpi = modulate_with_ss(params, transition_prone, stress)
        
        # 経路判定
        if stress <= transition_prone.stress_threshold:
            pathway = "経路A（場依存・高感度）"
        else:
            pathway = "経路B（脅威感受・跳躍）"
        
        print(f"\n💫 ストレス {stress:.1f}: {pathway}")
        print(f"  神経状態: D1={neuro.D1:.2f}, D2={neuro.D2:.2f}, NE={neuro.NE:.2f}, 5HT={neuro._5HT:.2f}")
        print(f"  変調効果: α0={modulated.alpha0:.2f}, Θ[0]={modulated.Theta_values[0]:.1f}")


if __name__ == "__main__":
    print("🧠✨ SS型（感覚過敏）統合システムデモ")
    
    # 基本比較
    demo_ss_basic_comparison()
    
    # 社会KPI計測
    demo_ss_social_kpi()
    
    # カイジ×SS型
    demo_kaiji_ss_progression()
    
    # 経路転換
    demo_ss_pathway_transition()
    
    print("\n" + "=" * 80)
    print("✅ SS型システム完全統合完了！")
    print("🔗 理論（HSP/感覚過敏）→ 数理フック → 実装完了")
    print("📊 社会・言語KPI（CAR/LP/CCL/XAL）計測機能実装")
    print("⚡ 二経路モデル（A: 場依存、B: 脅威感受）動作確認")
    print("🎯 ストレス転換ダイナミクス（A→B遷移）実現")
    print("=" * 80)