"""
Hybrid Selector Module

Implements adaptive algorithm selection based on problem size.
Uses exhaustive search for small problems and greedy with optimization for large ones.
"""

from typing import List, Set, Dict
from itertools import combinations, permutations
from math import comb, factorial

try:
    from .base_selector import BaseSelector
except ImportError:
    from base_selector import BaseSelector


class HybridSelector(BaseSelector):
    """
    Hybrid algorithm selector with adaptive strategy.

    Algorithm selection:
    - n ≤ threshold: Complete exhaustive search (all combinations & permutations)
    - n > threshold: Greedy algorithm + 2-opt local optimization

    Threshold is configurable via config.json (default: 10)
    """

    def _select_exercises_for_day(self, muscle_groups: List[str],
                                  global_selected_ids: Set[int]) -> List[Dict]:
        """
        Select 5 exercises using adaptive strategy based on problem size.

        Args:
            muscle_groups: Target muscle groups for the day
            global_selected_ids: Exercise IDs already used this week

        Returns:
            List of 5 exercises with scoring information
        """
        # Get candidate exercises
        candidates = self._get_candidate_exercises(
            muscle_groups, global_selected_ids)
        num_candidates = len(candidates)

        # Get threshold from config
        threshold = self.config['algorithm_params'].get(
            'exhaustive_threshold', 10)

        # Choose algorithm based on problem size
        if num_candidates <= threshold:
            return self._exhaustive_search(candidates, global_selected_ids)
        else:
            greedy_result = self._greedy_search(
                candidates, global_selected_ids)
            return self._two_opt_improvement(greedy_result, candidates, global_selected_ids)

    def _exhaustive_search(self, candidates: Dict[int, Dict],
                           global_selected_ids: Set[int]) -> List[Dict]:
        """
        Complete exhaustive search: test all C(n,5) × 5! possibilities.

        Time complexity: O(C(n,5) × 120)
        Guarantees global optimum but computationally expensive.

        Args:
            candidates: Available exercises with static scores
            global_selected_ids: Weekly selected exercise IDs

        Returns:
            Globally optimal selection of 5 exercises
        """
        candidate_ids = list(candidates.keys())

        # Handle insufficient candidates
        if len(candidate_ids) < 5:
            return self._greedy_search(candidates, global_selected_ids)

        best_result = None
        best_total_score = float('-inf')

        # Calculate total evaluations for large problems
        if len(candidate_ids) > 15:
            expected_combos = comb(len(candidate_ids), 5)
            expected_perms = expected_combos * factorial(5)
            print(f"    Evaluating {expected_perms:,} permutations...")

        # Test all combinations
        for combo in combinations(candidate_ids, 5):
            # Test all permutations of each combination
            for perm in permutations(combo):
                # Build and evaluate this permutation
                perm_result = self._build_solution(
                    perm, candidates, global_selected_ids)
                perm_score = sum(ex['score'] for ex in perm_result)

                # Update best if improved
                if perm_score > best_total_score:
                    best_total_score = perm_score
                    best_result = perm_result

        return best_result

    def _greedy_search(self, candidates: Dict[int, Dict],
                       global_selected_ids: Set[int]) -> List[Dict]:
        """
        Greedy algorithm: select best exercise for each position.

        Time complexity: O(n × 5)
        Fast but may not find global optimum.

        Args:
            candidates: Available exercises with static scores
            global_selected_ids: Weekly selected exercise IDs

        Returns:
            Locally optimal selection of 5 exercises
        """
        selected_exercises = []
        selected_ids = set()
        selected_families = set()

        for position in range(self.config['algorithm_params']['exercises_per_day']):
            best_exercise_id = None
            best_score = float('-inf')
            best_dynamic_score = 0

            # Find best exercise for current position
            for exercise_id, data in candidates.items():
                if exercise_id in selected_ids:
                    continue

                dynamic_score = self._calculate_dynamic_score(
                    data['exercise'],
                    position,
                    selected_exercises,
                    selected_families,
                    global_selected_ids
                )

                total_score = data['static_score'] + dynamic_score

                if total_score > best_score:
                    best_score = total_score
                    best_exercise_id = exercise_id
                    best_dynamic_score = dynamic_score

            # Add best exercise
            if best_exercise_id:
                selected_exercise = candidates[best_exercise_id]['exercise']

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

                family = self._get_exercise_family(best_exercise_id)
                if family:
                    selected_families.add(family)

        return selected_exercises

    def _two_opt_improvement(self, initial_solution: List[Dict],
                             candidates: Dict[int, Dict],
                             global_selected_ids: Set[int]) -> List[Dict]:
        """
        2-opt local search: improve solution by swapping positions.

        Iteratively swaps pairs of exercises to find better arrangements.
        Continues until no improvement found or max iterations reached.

        Args:
            initial_solution: Starting solution from greedy algorithm
            candidates: Available exercises with static scores
            global_selected_ids: Weekly selected exercise IDs

        Returns:
            Locally optimized solution
        """
        current_solution = initial_solution.copy()
        current_score = sum(ex['score'] for ex in current_solution)

        improved = True
        iterations = 0
        max_iterations = self.config['algorithm_params'].get(
            'max_2opt_iterations', 100)

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1

            # Try swapping each pair of positions
            for i in range(5):
                for j in range(i + 1, 5):
                    # Create new solution with swapped positions
                    exercise_ids = [ex['pk'] for ex in current_solution]
                    exercise_ids[i], exercise_ids[j] = exercise_ids[j], exercise_ids[i]

                    # Rebuild and evaluate
                    new_solution = self._build_solution(
                        tuple(exercise_ids), candidates, global_selected_ids)
                    new_score = sum(ex['score'] for ex in new_solution)

                    # Accept improvement
                    if new_score > current_score:
                        current_solution = new_solution
                        current_score = new_score
                        improved = True
                        break

                if improved:
                    break

        return current_solution

    def _build_solution(self, exercise_ids: tuple, candidates: Dict[int, Dict],
                        global_selected_ids: Set[int]) -> List[Dict]:
        """
        Build complete solution from ordered exercise IDs.

        Calculates dynamic scores based on position and already selected exercises.

        Args:
            exercise_ids: Ordered tuple of exercise IDs
            candidates: Available exercises with static scores
            global_selected_ids: Weekly selected exercise IDs

        Returns:
            Complete solution with all scoring information
        """
        selected_exercises = []
        selected_ids = set()
        selected_families = set()

        for position, exercise_id in enumerate(exercise_ids):
            # Calculate dynamic score for this position
            dynamic_score = self._calculate_dynamic_score(
                candidates[exercise_id]['exercise'],
                position,
                selected_exercises,
                selected_families,
                global_selected_ids
            )

            # Build exercise record
            selected_exercise = candidates[exercise_id]['exercise']
            static_score = candidates[exercise_id]['static_score']
            total_score = static_score + dynamic_score

            exercise_with_score = {
                'pk': selected_exercise['pk'],
                'name': selected_exercise['name'],
                'primaryMuscles': selected_exercise['primaryMuscles'],
                'secondaryMuscles': selected_exercise.get('secondaryMuscles', []),
                'static_score': round(static_score, 2),
                'dynamic_score': round(dynamic_score, 2),
                'score': round(total_score, 2),
                'position': position + 1
            }

            selected_exercises.append(exercise_with_score)
            selected_ids.add(exercise_id)

            # Track movement family
            family = self._get_exercise_family(exercise_id)
            if family:
                selected_families.add(family)

        return selected_exercises
