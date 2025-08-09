"""
Greedy Selector Module

Implements greedy algorithm for exercise selection.
Selects the best exercise for each position without backtracking.
"""

from typing import List, Set, Dict

try:
    from .base_selector import BaseSelector
except ImportError:
    from base_selector import BaseSelector


class GreedySelector(BaseSelector):
    """
    Greedy algorithm selector.

    At each position, selects the exercise with the highest total score
    (static + dynamic) from remaining candidates.

    Time complexity: O(n*m) where n=candidates, m=5 positions
    Space complexity: O(n)
    """

    def _select_exercises_for_day(self, muscle_groups: List[str],
                                  global_selected_ids: Set[int]) -> List[Dict]:
        """
        Select 5 exercises using greedy algorithm.

        Args:
            muscle_groups: Target muscle groups for the day
            global_selected_ids: Exercise IDs already used this week

        Returns:
            List of 5 exercises with scoring information
        """
        # Get candidate exercises with static scores
        candidates = self._get_candidate_exercises(
            muscle_groups, global_selected_ids)

        # Initialize tracking structures
        selected_exercises = []
        selected_ids = set()
        selected_families = set()

        # Greedy selection for each position
        for position in range(self.config['algorithm_params']['exercises_per_day']):
            best_exercise_id = None
            best_score = float('-inf')
            best_dynamic_score = 0

            # Evaluate each remaining candidate
            for exercise_id, data in candidates.items():
                if exercise_id in selected_ids:
                    continue

                # Calculate position-dependent dynamic score
                dynamic_score = self._calculate_dynamic_score(
                    data['exercise'],
                    position,
                    selected_exercises,
                    selected_families,
                    global_selected_ids
                )

                total_score = data['static_score'] + dynamic_score

                # Track best option for this position
                if total_score > best_score:
                    best_score = total_score
                    best_exercise_id = exercise_id
                    best_dynamic_score = dynamic_score

            # Add best exercise if found
            if best_exercise_id:
                selected_exercise = candidates[best_exercise_id]['exercise']

                # Create exercise record with scores
                exercise_with_score = {
                    'pk': selected_exercise['pk'],
                    'name': selected_exercise['name'],
                    'primaryMuscles': selected_exercise['primaryMuscles'],
                    'secondaryMuscles': selected_exercise.get('secondaryMuscles', []),
                    'static_score': round(candidates[best_exercise_id]['static_score'], 2),
                    'dynamic_score': round(best_dynamic_score, 2),
                    'score': round(best_score, 2),
                    'position': position + 1
                }

                selected_exercises.append(exercise_with_score)
                selected_ids.add(best_exercise_id)

                # Update movement family tracking
                family = self._get_exercise_family(best_exercise_id)
                if family:
                    selected_families.add(family)

        return selected_exercises
