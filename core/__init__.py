"""
SSD Theory Core Engine

コアエンジン - SSD理論の統合実装

このパッケージには、SSD理論の完全統合実装が含まれています：
- Log-Alignment対応SSDコアエンジン（正式版）
- 多次元意味圧システム（復活・新コア対応）
- 人間心理特化モジュール（復活・新コア対応）
- 非線形層間転送システム（復活・新コア対応）
- 神経変調システム統合  
- 人体体温基準熱力学システム
- SS型（感覚過敏）対応

旧実装は core/archive/ に保存されています。
"""

from .ssd_core_engine import SSDCoreEngine, SSDCoreState, SSDCoreParams, LeapType
from .ssd_pressure_system import (
    MultidimensionalPressureEngine, PressureDimension, StructuralLayer,
    PressureCalculationResult, create_pressure_engine_for_scenario,
    create_kaiji_pressure_dimensions, create_ss_type_pressure_dimensions
)
from .ssd_human_module import (
    HumanAgent, HumanParams, HumanPressure, HumanLayer
)
from .ssd_nonlinear_transfer import (
    NonlinearInterlayerTransfer, NonlinearTransferFunction,
    create_default_nonlinear_transfer
)

__all__ = [
    # Core Engine (Log-Alignment + Thermal + Neuro Integration)
    'SSDCoreEngine',
    'SSDCoreState', 
    'SSDCoreParams',
    'LeapType',
    
    # Multidimensional Pressure System
    'MultidimensionalPressureEngine',
    'PressureDimension',
    'StructuralLayer', 
    'PressureCalculationResult',
    'create_pressure_engine_for_scenario',
    'create_kaiji_pressure_dimensions',
    'create_ss_type_pressure_dimensions',
    
    # Human Psychology Module
    'HumanAgent',
    'HumanParams',
    'HumanPressure', 
    'HumanLayer',
    
    # Nonlinear Interlayer Transfer System
    'NonlinearInterlayerTransfer',
    'NonlinearTransferFunction',
    'create_default_nonlinear_transfer',
]

__version__ = '2.0.0'  # Log-Alignment + Neuro + SS integration
