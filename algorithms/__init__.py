"""
Exercise Selection Algorithms Package

This package provides different algorithms for workout plan generation.
"""

from .base_selector import BaseSelector
from .greedy_selector import GreedySelector
from .hybrid_selector import HybridSelector

__version__ = '1.0.0'
__all__ = ['BaseSelector', 'GreedySelector', 'HybridSelector']
