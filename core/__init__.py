"""
SSD Theory Core Modules

コアモジュール - SSD理論の基本要素

このパッケージには、SSD理論の最も基本的な構成要素が含まれています。
すべてのSSD実装はこれらのコアモジュールの上に構築されます。
"""

from .ssd_core_engine import SSDCoreEngine, SSDCoreState, SSDCoreParams, LeapType
from .ssd_human_module import HumanAgent, HumanLayer, HumanPressure

__all__ = [
    # Core Engine
    'SSDCoreEngine',
    'SSDCoreState',
    'SSDCoreParams',
    'LeapType',
    
    # Human Module
    'HumanAgent',
    'HumanLayer',
    'HumanPressure',
]

__version__ = '1.0.0'
