"""
Base Selector Module for Exercise Selection System

This module provides the abstract base class for all exercise selection algorithms.
Handles data loading, scoring calculations, and common utilities.
"""

import json
import os
import sys
from typing import Dict, List, Set
from abc import ABC, abstractmethod

# Force UTF-8 encoding for console output
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Windows console UTF-8 configuration
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul 2>&1')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class BaseSelector(ABC):
    """
    Abstract base class for exercise selection algorithms.

    Subclasses must implement:
    - _select_exercises_for_day(): Core algorithm for selecting 5 exercises
    """

    # ========== USER CONFIGURATION ==========
    # Training days per week (1-7)
    TRAINING_DAYS = 5

    # Muscle group preference coefficients (0.1-10.0, default: 1.0)
    MUSCLE_PREFERENCES = {
        "chest": 1.5,
        "back": 0.6,
        "shoulder": 0.6,
        "arm": 0.6,
        "leg": 0.6,
        "core": 0.6
    }

    # Excluded exercise IDs
    EXCLUDED_EXERCISES = set()
    # ========== END CONFIGURATION ==========

    def __init__(self):
        """Initialize selector with all necessary data files."""
        # Get project root directory
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)

        # Load core data files
        self.exercises = self._load_json(
            os.path.join(project_root, 'strength.json'))
        self.config = self._load_json(
            os.path.join(project_root, 'config.json'))

        # Load classification files
        classification_dir = os.path.join(project_root, 'classification')

        self.category_mapping = self._load_json(
            os.path.join(classification_dir, 'categoryMapping.json'))
        self.preference_mapping = self._load_json(
            os.path.join(classification_dir, 'preferenceMapping.json'))
        self.training_templates = self._load_json(
            os.path.join(classification_dir, 'trainingTemplates.json'))

        # Load six classification dimensions
        self.classifications = {
            'major': self._load_json(os.path.join(classification_dir, 'type1_isMajor.json')),
            'compound': self._load_json(os.path.join(classification_dir, 'type2_isCompound.json')),
            'single': self._load_json(os.path.join(classification_dir, 'type3_isSingle.json')),
            'machine': self._load_json(os.path.join(classification_dir, 'type4_isMachine.json')),
            'common': self._load_json(os.path.join(classification_dir, 'type5_isCommon.json')),
            'family': self._load_json(os.path.join(classification_dir, 'type6_movementFamily.json'))
        }

    def _load_json(self, filepath: str) -> Dict:
        """Load JSON file with UTF-8 encoding."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_weekly_plan(self) -> Dict:
        """
        Generate a complete weekly workout plan.

        Returns:
            Dictionary containing daily workout plans
        """
        template = self.training_templates[str(self.TRAINING_DAYS)]
        weekly_plan = {}
        global_selected_ids = set()  # Track weekly selections to avoid repetition

        for day_index, muscle_groups in enumerate(template):
            day_name = f"Day {day_index + 1}"

            # Handle rest days
            if not muscle_groups:
                weekly_plan[day_name] = {
                    "type": "Rest Day",
                    "exercises": [],
                    "total_score": 0
                }
                continue

            # Select exercises for this day
            exercises_with_scores = self._select_exercises_for_day(
                muscle_groups, global_selected_ids
            )

            # Update global tracking
            for ex in exercises_with_scores:
                global_selected_ids.add(ex['pk'])

            # Calculate daily total score
            total_day_score = sum(ex['score'] for ex in exercises_with_scores)

            weekly_plan[day_name] = {
                "type": self._generate_day_type(muscle_groups),
                "muscle_groups": muscle_groups,
                "exercises": exercises_with_scores,
                "total_score": round(total_day_score, 2)
            }

        return weekly_plan

    @abstractmethod
    def _select_exercises_for_day(self, muscle_groups: List[str],
                                  global_selected_ids: Set[int]) -> List[Dict]:
        """
        Select 5 exercises for a specific training day.
        Must be implemented by subclasses.
        """
        pass

    def _get_candidate_exercises(self, muscle_groups: List[str],
                                 global_selected_ids: Set[int]) -> Dict[int, Dict]:
        """Get candidate exercises and calculate static scores."""
        # Get exercise IDs for target muscle groups
        exercise_ids = set()
        for muscle_group in muscle_groups:
            if muscle_group in self.category_mapping:
                exercise_ids.update(self.category_mapping[muscle_group])

        # Handle full body training
        if not exercise_ids or muscle_groups == ["all"]:
            exercise_ids = {ex['pk'] for ex in self.exercises}

        # Calculate static score for each valid exercise
        candidates = {}
        for exercise_id in exercise_ids:
            exercise = self._get_exercise_by_id(exercise_id)
            if exercise and exercise['pk'] not in self.EXCLUDED_EXERCISES:
                static_score = self._calculate_static_score(exercise)
                candidates[exercise_id] = {
                    'exercise': exercise,
                    'static_score': static_score
                }

        return candidates

    def _calculate_static_score(self, exercise: Dict) -> float:
        """
        Calculate position-independent static score.
        Uses sharing mechanism to prevent multi-muscle exercises from dominating.
        """
        score = 0
        weights = self.config['scoring_weights']

        # Primary muscle score with sharing mechanism
        primary_muscles = exercise.get('primaryMuscles', [])
        if primary_muscles:
            score_per_muscle = weights['primary_muscle']['base_score'] / \
                len(primary_muscles)
            for muscle in primary_muscles:
                preference = self._get_muscle_preference(muscle)
                score += score_per_muscle * preference

        # Secondary muscle score with sharing mechanism
        secondary_muscles = exercise.get('secondaryMuscles', [])
        if secondary_muscles:
            score_per_muscle = weights['secondary_muscle']['base_score'] / \
                len(secondary_muscles)
            for muscle in secondary_muscles:
                preference = self._get_muscle_preference(muscle)
                score += score_per_muscle * preference

        # Common exercise bonus
        if exercise['pk'] in self.classifications['common']['Common']:
            score += weights['common_exercise_bonus']['score']

        return score

    def _calculate_dynamic_score(self, exercise: Dict, position: int,
                                 selected_exercises: List[Dict],
                                 selected_families: Set[str],
                                 global_selected_ids: Set[int]) -> float:
        """
        Calculate position-dependent dynamic score.
        Includes position bonuses, diversity penalties, and repetition penalties.
        """
        score = 0
        exercise_id = exercise['pk']
        position_scores = self.config['position_scores']

        # Layer 1: Position-based scoring
        if exercise_id in self.classifications['major']['Major']:
            score += position_scores['major_muscle']['scores'][position]
        elif exercise_id in self.classifications['major']['Minor']:
            score += position_scores['minor_muscle']['scores'][position]

        if exercise_id in self.classifications['compound']['compound']:
            score += position_scores['compound']['scores'][position]
        elif exercise_id in self.classifications['compound']['isolation']:
            score += position_scores['isolation']['scores'][position]

        if exercise_id in self.classifications['machine']['free']:
            score += position_scores['free_weight']['scores'][position]
        elif exercise_id in self.classifications['machine']['equipment']:
            score += position_scores['equipment']['scores'][position]

        # Layer 2: Diversity balance
        bilateral_count = 0
        compound_count = 0
        machine_count = 0
        selected_muscle_groups = set()

        for ex in selected_exercises:
            ex_id = ex['pk']
            # Track muscle groups
            for muscle_group, exercise_ids in self.category_mapping.items():
                if ex_id in exercise_ids:
                    selected_muscle_groups.add(muscle_group)

            # Count characteristics
            if ex_id in self.classifications['single']['bilateral']:
                bilateral_count += 1
            if ex_id in self.classifications['compound']['compound']:
                compound_count += 1
            if ex_id in self.classifications['machine']['equipment']:
                machine_count += 1

        # Apply diversity penalties
        diversity = self.config['diversity_rules']
        threshold = diversity['balance_threshold']
        penalty = diversity['balance_penalty']

        if exercise_id in self.classifications['single']['bilateral'] and bilateral_count >= threshold:
            score += penalty
        elif exercise_id in self.classifications['single']['single_sided'] and (len(selected_exercises) - bilateral_count) >= threshold:
            score += penalty

        if exercise_id in self.classifications['compound']['compound'] and compound_count >= threshold:
            score += penalty
        elif exercise_id in self.classifications['compound']['isolation'] and (len(selected_exercises) - compound_count) >= threshold:
            score += penalty

        if exercise_id in self.classifications['machine']['equipment'] and machine_count >= threshold:
            score += penalty
        elif exercise_id in self.classifications['machine']['free'] and (len(selected_exercises) - machine_count) >= threshold:
            score += penalty

        # Apply repetition penalties
        penalties = diversity['penalties']

        # Same movement family penalty
        family = self._get_exercise_family(exercise_id)
        if family and family in selected_families:
            score += penalties['same_family']

        # Weekly repetition penalty
        if exercise_id in global_selected_ids:
            score += penalties['weekly_repeat']

        # Muscle group overlap penalty
        muscle_group_overlap = sum(1 for muscle_group, exercise_ids in self.category_mapping.items()
                                   if exercise_id in exercise_ids and muscle_group in selected_muscle_groups)
        if muscle_group_overlap > 0:
            score += penalties['same_muscle_group'] * muscle_group_overlap

        return score

    def _get_exercise_by_id(self, exercise_id: int) -> Dict:
        """Retrieve exercise data by ID."""
        for exercise in self.exercises:
            if exercise['pk'] == exercise_id:
                return exercise
        return None

    def _get_exercise_family(self, exercise_id: int) -> str:
        """Get movement family for an exercise."""
        for family_name, exercise_ids in self.classifications['family'].items():
            if exercise_id in exercise_ids:
                return family_name
        return None

    def _get_muscle_preference(self, muscle: str) -> float:
        """Get preference coefficient for a specific muscle."""
        for category, muscles in self.preference_mapping.items():
            if muscle in muscles:
                return self.MUSCLE_PREFERENCES.get(category, 1.0)
        return 1.0

    def _generate_day_type(self, muscle_groups: List[str]) -> str:
        """Generate human-readable training day type."""
        muscle_names = {
            "chest": "Chest", "back": "Back", "shoulder": "Shoulders",
            "tricep": "Triceps", "bicep": "Biceps", "legs": "Legs",
            "arm": "Arms", "core": "Core"
        }
        names = [muscle_names.get(mg, mg.title()) for mg in muscle_groups]

        if len(names) == 1:
            return names[0]
        elif len(names) == 2:
            return f"{names[0]} & {names[1]}"
        else:
            return f"{', '.join(names[:-1])} & {names[-1]}"

    def print_detailed_plan(self, weekly_plan: Dict) -> None:
        """Print formatted weekly workout plan."""
        print("\n" + "="*80)
        print(f"Weekly Workout Plan (Generated by {self.__class__.__name__})")
        print("="*80)

        # Display configuration
        template_names = {
            1: "Full Body", 2: "Upper/Lower Split", 3: "Push/Pull/Legs",
            4: "Push/Pull x2", 5: "Bro Split", 6: "Push/Pull/Legs x2",
            7: "Push/Pull/Legs x2 + Rest"
        }
        print(
            f"\nTraining Days: {self.TRAINING_DAYS} ({template_names[self.TRAINING_DAYS]})")

        # Display muscle preferences if customized
        non_default = {k: v for k,
                       v in self.MUSCLE_PREFERENCES.items() if v != 1.0}
        if non_default:
            print("\nMuscle Preferences:")
            for muscle, coef in sorted(non_default.items()):
                print(f"  {muscle}: {coef}")

        # Display excluded exercises
        if self.EXCLUDED_EXERCISES:
            print("\nExcluded Exercises:")
            for excluded_id in self.EXCLUDED_EXERCISES:
                ex = self._get_exercise_by_id(excluded_id)
                if ex:
                    print(f"  - [{excluded_id}] {ex['name']}")

        # Print daily plans
        for day, plan in weekly_plan.items():
            print(f"\n{day}: {plan['type']}")
            if 'muscle_groups' in plan and plan['muscle_groups']:
                print(f"Target Muscles: {', '.join(plan['muscle_groups'])}")
            print(f"Daily Total Score: {plan['total_score']}")
            print("-" * 60)

            if plan['exercises']:
                for exercise in plan['exercises']:
                    print(
                        f"\nPosition {exercise['position']}. [{exercise['pk']}] {exercise['name']}")
                    print(
                        f"   Static: {exercise['static_score']} | Dynamic: {exercise['dynamic_score']} | Total: {exercise['score']}")
                    print(
                        f"   Primary: {', '.join(exercise['primaryMuscles'])}")
                    if exercise['secondaryMuscles']:
                        print(
                            f"   Secondary: {', '.join(exercise['secondaryMuscles'])}")
            else:
                print("   Rest and Recovery!")
