"""
SSD Theory Extensions

拡張モジュール - 社会的相互作用と高度な機能

このパッケージには、SSD理論を社会システムや複雑な相互作用に
拡張するためのモジュールが含まれています。
"""

from .ssd_social_dynamics import (
    Society, SocialDynamicsEngine, SocialCouplingParams, 
    RelationshipMatrix, RelationType
)

__all__ = [
    # Social Dynamics
    'Society',
    'SocialDynamicsEngine',
    'SocialCouplingParams',
    'RelationshipMatrix',
    'RelationType',
]

__version__ = '1.0.0'
