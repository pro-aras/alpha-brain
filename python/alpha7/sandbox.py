"""Alpha 7 Interactive Multi-Sensory Sandbox & Embodied Organism Loop.

Pairs the Rust `Alpha7Brain` (1,000,000+ sparse dendritic neurons, BTSP one-shot concept web,
and predictive engine) with `Alpha7Body` (Eyes, Ears, Hands, Smell, Senses).
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from .alpha7_core import Alpha7Brain
from .body import Alpha7Body, SensoryFrame


class Alpha7Organism:
    """High-level embodied organism uniting Alpha7Brain (Rust) and Alpha7Body (5 senses)."""

    def __init__(self, num_neurons: int = 1_000_000, neurons_per_column: int = 64) -> None:
        self.brain = Alpha7Brain(num_neurons, neurons_per_column)
        self.body = Alpha7Body()

    @property
    def neuron_count(self) -> int:
        return self.brain.neuron_count()

    @property
    def memory_footprint_mb(self) -> float:
        return self.brain.memory_footprint_mb()

    def experience_object(
        self,
        concept_name: str,
        frame: SensoryFrame,
        affordance: Optional[Tuple[str, str]] = None,
        partner: str = "user",
    ) -> Dict[str, Any]:
        """Experiences a multi-sensory object/entity (e.g. a cat) once or twice, binding its
        traits, spoken words, and affordances into the Conceptual Knowledge Web via BTSP.
        """
        raw = self.brain.learn_concept(
            concept_name,
            frame.to_neural_traits(),
            frame.spoken_words or [concept_name],
            affordance,
            partner,
        )
        return json.loads(raw)

    def recognize(self, frame: SensoryFrame) -> List[Dict[str, Any]]:
        """Recognizes what concept(s) match a sensory frame using core invariant overlap."""
        raw = self.brain.recognize(frame.to_neural_traits())
        return json.loads(raw)

    def inspect_concept(self, concept_name: str) -> Dict[str, Any]:
        """Returns the learned core invariants, variable surface traits, and familiarity of a concept."""
        return json.loads(self.brain.inspect_concept(concept_name))

    def predict_before_acting(self, frame: SensoryFrame, action: str) -> List[Tuple[str, float]]:
        """Predicts what sensory/state traits will happen next if `action` is taken."""
        return self.brain.predict_next(frame.to_neural_traits(), action)

    def act_and_learn_from_surprise(
        self,
        context_frame: SensoryFrame,
        action: str,
        actual_outcome_traits: List[str],
        partner: str = "sandbox",
    ) -> Dict[str, Any]:
        """Executes `action`, compares predicted outcome vs actual reality, and if something
        predicted fails to happen, analyzes the cause and learns from it in one shot.
        """
        raw = self.brain.act_and_analyze(
            context_frame.to_neural_traits(),
            action,
            actual_outcome_traits,
            partner,
        )
        return json.loads(raw)

    def practice_coding(
        self,
        code_str: str,
        local_inputs: Optional[Dict[str, object]] = None,
        concept_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Alpha 7 looks at a small code snippet with its Eyes, predicts what will happen when
        it runs the code with its Hands, executes the code, and analyzes any surprise or error!
        """
        visual_code_traits = self.body.eyes.inspect_code(code_str)
        context_frame = SensoryFrame(
            eyes=visual_code_traits,
            senses=self.body.internal.read_state(),
        )
        predicted = self.predict_before_acting(context_frame, "run_code")
        actual_outcomes = self.body.hands.execute_small_code(code_str, local_inputs)

        analysis = self.act_and_learn_from_surprise(
            context_frame,
            "run_code",
            actual_outcomes,
            partner="user",
        )
        if concept_label and actual_outcomes:
            self.brain.learn_concept(
                concept_label,
                visual_code_traits,
                [concept_label],
                ("run_code", actual_outcomes[0]),
                "user",
            )
        return {
            "code": code_str,
            "visual_code_traits": visual_code_traits,
            "predicted_before_run": predicted,
            "actual_outcomes": actual_outcomes,
            "analysis": analysis["evaluation"],
        }

    def calculate_goal_scenarios(
        self,
        current_frame: SensoryFrame,
        goal_trait: str,
        max_depth: int = 3,
    ) -> List[Dict[str, Any]]:
        """Directs Alpha 7's predictive engine toward a goal, simulating multi-step possibilities."""
        raw = self.brain.simulate_goal_scenarios(
            current_frame.to_neural_traits(),
            goal_trait,
            max_depth,
        )
        return json.loads(raw)

    def understand_words(self, utterance: str) -> Dict[str, Any]:
        """Grounds spoken/written words into evoked sensory-motor traits, affordances, and user memories."""
        return json.loads(self.brain.think_on_words(utterance))

    def user_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves direct autobiographical memories formed with the user."""
        return json.loads(self.brain.recalled_episodes(limit))


class SandboxWorld:
    """Pre-built multi-sensory scenarios for testing Alpha 7's infant-like 1-2 shot learning,
    prediction-failure analysis, goal-directed scenario simulation, and grounded language.
    """

    @staticmethod
    def cat_exposure_1(body: Alpha7Body) -> SensoryFrame:
        """Interaction 1: User shows an orange cat named 'cat' that purrs and has soft fur."""
        return body.build_frame(
            eyes=["pointy_ears", "whiskers", "slit_pupils", "four_legs", "long_tail", "orange_fur"],
            ears=["purr", "meow"],
            hands=["soft_fur", "warm_body"],
            smell=["feline_scent"],
            utterance="look at this cat kitty",
        )

    @staticmethod
    def cat_exposure_2(body: Alpha7Body) -> SensoryFrame:
        """Interaction 2: User shows a black cat — shares core feline invariants, differs in coat color."""
        return body.build_frame(
            eyes=["pointy_ears", "whiskers", "slit_pupils", "four_legs", "long_tail", "black_fur"],
            ears=["purr"],
            hands=["soft_fur", "warm_body"],
            smell=["feline_scent"],
            utterance="another cat",
        )

    @staticmethod
    def unseen_white_cat(body: Alpha7Body) -> SensoryFrame:
        """Unseen test entity: A white silent cat in the rain (never seen before)."""
        return body.build_frame(
            eyes=["pointy_ears", "whiskers", "slit_pupils", "four_legs", "white_fur"],
            ears=[],
            hands=["soft_fur"],
            smell=["feline_scent", "rain_ozone"],
        )

    @staticmethod
    def unseen_dog(body: Alpha7Body) -> SensoryFrame:
        """Distractor entity: A brown dog with floppy ears and a bark."""
        return body.build_frame(
            eyes=["floppy_ears", "wet_snout", "four_legs", "wagging_tail", "brown_fur"],
            ears=["bark", "panting"],
            hands=["coarse_fur", "warm_body"],
            smell=["canine_scent"],
        )
