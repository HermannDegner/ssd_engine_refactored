"""
SSD Theory Extensions

拡張モジュール - 神経変調・感覚過敏・社会システム

このパッケージには、SSD理論を拡張するためのモジュールが含まれています：
- 神経変調システム（NeuroModulators）
- SS型（感覚過敏）統合システム
- メモリ構造・動的解釈（アーカイブ）

Note: 社会ダイナミクス等の旧実装は一時的に無効化
"""

# 神経変調システム（最新・安定版）
from .ssd_neuro_modulators import (
    NeuroState, NeuroConfig, modulate_params, neuro_preset
)

# SS型（感覚過敏）システム  
from .ssd_ss_sensitivity import (
    SSProfile, SSNeuroConfig, SocialLanguageKPI,
    ss_preset, modulate_with_ss, compute_social_language_kpi
)

__all__ = [
    # Neural Modulation System
    'NeuroState',
    'NeuroConfig', 
    'modulate_params',
    'neuro_preset',
    
    # SS (Sensory Sensitivity) System
    'SSProfile',
    'SSNeuroConfig',
    'SocialLanguageKPI',
    'ss_preset',
    'modulate_with_ss',
    'compute_social_language_kpi',
]

__version__ = '2.0.0'  # Neural + SS Integration
