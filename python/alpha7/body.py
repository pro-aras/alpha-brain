"""Alpha 7 Embodied 5-Sense Body (Eyes, Ears, Hands, Smell, and Internal Senses).

Translates raw multi-sensory observations, user interactions, and small code executions
into grounded sparse neural trait streams for the Rust Alpha7Brain engine.
"""

from __future__ import annotations

import ast
import io
import contextlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SensoryFrame:
    """A unified multi-modal sensory snapshot captured by Alpha 7's body on a single tick."""

    eyes: List[str] = field(default_factory=list)
    ears: List[str] = field(default_factory=list)
    hands: List[str] = field(default_factory=list)
    smell: List[str] = field(default_factory=list)
    senses: List[str] = field(default_factory=list)
    spoken_words: List[str] = field(default_factory=list)

    def to_neural_traits(self) -> List[str]:
        """Flattens all 5 sensory streams into grounded modality-prefixed neural trait keys."""
        traits: List[str] = []
        for item in self.eyes:
            traits.append(item if item.startswith("eyes:") else f"eyes:{item}")
        for item in self.ears:
            traits.append(item if item.startswith("ears:") else f"ears:{item}")
        for item in self.hands:
            traits.append(item if item.startswith("hands:") else f"hands:{item}")
        for item in self.smell:
            traits.append(item if item.startswith("smell:") else f"smell:{item}")
        for item in self.senses:
            traits.append(item if item.startswith("senses:") else f"senses:{item}")
        return traits


class EyesSensor:
    """Visual processing organ: extracts structural traits from visual scenes and code snippets."""

    def observe_entity(self, visual_features: List[str]) -> List[str]:
        return [f"eyes:{f}" if not f.startswith("eyes:") else f for f in visual_features]

    def inspect_code(self, code_str: str) -> List[str]:
        """Extracts structural visual traits when Alpha 7 looks at a piece of Python code."""
        traits: List[str] = ["eyes:code_block"]
        try:
            tree = ast.parse(code_str)
            traits.append("eyes:valid_syntax")
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    traits.append("eyes:has_function_def")
                    traits.append(f"eyes:func_{node.name}")
                elif isinstance(node, ast.For) or isinstance(node, ast.While):
                    traits.append("eyes:has_loop")
                elif isinstance(node, ast.Add):
                    traits.append("eyes:has_addition")
                elif isinstance(node, ast.Mult):
                    traits.append("eyes:has_multiplication")
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    traits.append(f"eyes:calls_{node.func.id}")
                elif isinstance(node, ast.Return):
                    traits.append("eyes:has_return")
        except SyntaxError:
            traits.append("eyes:syntax_typo")
        return list(dict.fromkeys(traits))


class EarsSensor:
    """Auditory & lexical organ: perceives acoustic signatures and grounded words from the user."""

    def listen(self, sounds: List[str], utterance: Optional[str] = None) -> Tuple[List[str], List[str]]:
        sound_traits = [f"ears:{s}" if not s.startswith("ears:") else s for s in sounds]
        words: List[str] = []
        if utterance:
            for token in utterance.replace(",", " ").replace(".", " ").split():
                clean = token.strip().lower()
                if clean:
                    words.append(clean)
                    sound_traits.append(f"ears:heard_{clean}")
        return sound_traits, words


class HandsEffector:
    """Tactile & motor organ: touches objects, performs actions, and writes/runs small code."""

    def touch(self, tactile_features: List[str]) -> List[str]:
        return [f"hands:{t}" if not t.startswith("hands:") else t for t in tactile_features]

    def execute_small_code(self, code_str: str, local_inputs: Optional[Dict[str, object]] = None) -> List[str]:
        """Executes a small code snippet with Alpha 7's hands and returns the observed visual/tactile outcome traits."""
        stdout_buf = io.StringIO()
        env: Dict[str, object] = {}
        if local_inputs:
            env.update(local_inputs)
        try:
            with contextlib.redirect_stdout(stdout_buf):
                exec(code_str, {"__builtins__": {"print": print, "range": range, "len": len, "sum": sum, "abs": abs, "min": min, "max": max}}, env)
            out_text = stdout_buf.getvalue().strip()
            outcomes = ["eyes:code_ran_cleanly"]
            if out_text:
                outcomes.append(f"eyes:printed_{out_text}")
            if "result" in env:
                outcomes.append(f"eyes:result_{env['result']}")
            return outcomes
        except SyntaxError:
            return ["eyes:syntax_error", "hands:execution_halted"]
        except Exception as exc:
            return [f"eyes:runtime_error_{type(exc).__name__}", "hands:execution_halted"]


class SmellSensor:
    """Olfactory & ambient chemical/context marker sensor."""

    def sniff(self, scents: List[str]) -> List[str]:
        return [f"smell:{s}" if not s.startswith("smell:") else s for s in scents]


class InternalSenses:
    """Proprioception, surprise arousal, energy, and user familiarity sense."""

    def __init__(self) -> None:
        self.user_interactions: int = 0
        self.last_surprise: float = 0.0

    def read_state(self, surprise: float = 0.0) -> List[str]:
        self.last_surprise = surprise
        traits = ["senses:awake"]
        if surprise >= 0.5:
            traits.append("senses:high_surprise_alert")
        else:
            traits.append("senses:calm_predictive_flow")
        if self.user_interactions > 0:
            traits.append("senses:user_bond_active")
        return traits


class Alpha7Body:
    """Complete embodied interface uniting Eyes, Ears, Hands, Smell, and Internal Senses."""

    def __init__(self) -> None:
        self.eyes = EyesSensor()
        self.ears = EarsSensor()
        self.hands = HandsEffector()
        self.smell = SmellSensor()
        self.internal = InternalSenses()

    def build_frame(
        self,
        eyes: Optional[List[str]] = None,
        ears: Optional[List[str]] = None,
        hands: Optional[List[str]] = None,
        smell: Optional[List[str]] = None,
        senses: Optional[List[str]] = None,
        utterance: Optional[str] = None,
    ) -> SensoryFrame:
        ear_traits, words = self.ears.listen(ears or [], utterance)
        if utterance:
            self.internal.user_interactions += 1
        return SensoryFrame(
            eyes=self.eyes.observe_entity(eyes or []),
            ears=ear_traits,
            hands=self.hands.touch(hands or []),
            smell=self.smell.sniff(smell or []),
            senses=senses if senses is not None else self.internal.read_state(self.last_surprise if hasattr(self, "last_surprise") else 0.0),
            spoken_words=words,
        )
