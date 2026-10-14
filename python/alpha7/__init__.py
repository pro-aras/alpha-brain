"""Alpha 7: Embodied Sparse Dendritic AI with 1-2 Shot Concept Web & Predictive World Model."""

from .alpha7_core import Alpha7Brain
from .body import Alpha7Body, SensoryFrame
from .sandbox import Alpha7Organism, SandboxWorld

__all__ = [
    "Alpha7Brain",
    "Alpha7Body",
    "SensoryFrame",
    "Alpha7Organism",
    "SandboxWorld",
]
