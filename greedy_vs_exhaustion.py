"""
Greedy vs Exhaustive Algorithm Performance Test

This module tests the performance difference between greedy and exhaustive search
algorithms on small sample sizes to determine the optimal threshold for algorithm selection.
"""

import time
import sys
import os
from typing import List, Dict
from itertools import combinations, permutations
from math import comb, factorial

# Direct import since we're in the root directory now
from algorithms.hybrid_selector import HybridSelector


class SmallSampleExhaustiveTester:
    """Test exhaustive search performance on small sample sizes"""

    def __init__(self):
        self.selector = HybridSelector()
        self.training_days = 1
        self.preferences = {
            "chest": 0.9,
            "back": 0.9,
            "shoulder": 0.9,
            "arm": 0.9,
            "leg": 0.9,
            "core": 0.9
        }

    def run_test(self):
        """Execute small sample exhaustive test"""
        print("="*80)
        print("ALGORITHM PERFORMANCE TEST")
        print("Greedy vs. Exhaustive Search Comparison")
        print("="*80)

        sample_sizes = [5, 10, 15, 20]
        results = []

        # Save original settings
        original_days = self.selector.TRAINING_DAYS
        original_prefs = self.selector.MUSCLE_PREFERENCES.copy()

        try:
            # Set test parameters
            self.selector.TRAINING_DAYS = self.training_days
            self.selector.MUSCLE_PREFERENCES = self.preferences.copy()

            for size in sample_sizes:
                print(f"\nTesting with {size} candidates")
                print("-"*40)

                # Calculate expected evaluations
                if size == 5:
                    expected_evals = factorial(5)
                else:
                    expected_evals = comb(size, 5) * factorial(5)

                print(f"Total evaluations required: {expected_evals:,}")

                result = self._test_sample_size(size)
                results.append(result)

                # Print immediate results
                print(f"\nTest Results:")
                print(
                    f"  Greedy algorithm time: {result['greedy_time']:.6f} seconds")
                print(
                    f"  Exhaustive algorithm time: {result['exhaustive_time']:.6f} seconds")

                if result['greedy_time'] > 0:
                    time_ratio = result['exhaustive_time'] / \
                        result['greedy_time']
                    print(f"  Time ratio: {time_ratio:.1f}x")

                print(f"  Greedy score: {result['greedy_score']:.2f}")
                print(f"  Exhaustive score: {result['exhaustive_score']:.2f}")
                print(
                    f"  Score difference: {result['exhaustive_score'] - result['greedy_score']:.2f}")

        finally:
            # Restore original settings
            self.selector.TRAINING_DAYS = original_days
            self.selector.MUSCLE_PREFERENCES = original_prefs

        # Print summary report
        self._print_summary(results)

    def _test_sample_size(self, sample_size: int) -> dict:
        """Test algorithms with fixed sample size"""
        # Get muscle groups for 1-day training (full body)
        template = self.selector.training_templates[str(self.training_days)]
        muscle_groups = template[0]

        # Get candidates and select first N
        full_candidates = self.selector._get_candidate_exercises(
            muscle_groups, set())
        candidate_ids = sorted(full_candidates.keys())[:sample_size]
        fixed_candidates = {k: full_candidates[k] for k in candidate_ids}

        print(f"Selected candidates: {candidate_ids}")

        # Test greedy algorithm
        print("\nRunning greedy algorithm...")
        start_time = time.perf_counter()
        greedy_result = self._run_greedy_algorithm(fixed_candidates)
        greedy_time = time.perf_counter() - start_time
        greedy_score = sum(ex['score'] for ex in greedy_result)
        print(f"Greedy complete in {greedy_time:.6f}s")

        # Test exhaustive algorithm
        print("\nRunning exhaustive algorithm (all permutations)...")
        start_time = time.perf_counter()
        exhaustive_result = self._run_exhaustive_algorithm(fixed_candidates)
        exhaustive_time = time.perf_counter() - start_time
        exhaustive_score = sum(ex['score'] for ex in exhaustive_result)
        print(f"Exhaustive complete in {exhaustive_time:.6f}s")

        return {
            'sample_size': sample_size,
            'greedy_time': greedy_time,
            'greedy_score': greedy_score,
            'exhaustive_time': exhaustive_time,
            'exhaustive_score': exhaustive_score,
            'greedy_result': greedy_result,
            'exhaustive_result': exhaustive_result
        }

    def _run_greedy_algorithm(self, candidates: Dict) -> List[Dict]:
        """Execute greedy selection algorithm"""
        selected = []
        used_ids = set()
        families = set()

        for position in range(5):
            best_id = None
            best_score = float('-inf')

            # Evaluate each remaining candidate
            for ex_id, data in candidates.items():
                if ex_id in used_ids:
                    continue

                # Calculate dynamic score for this position
                dynamic = self.selector._calculate_dynamic_score(
                    data['exercise'], position, selected, families, set()
                )
                total = data['static_score'] + dynamic

                if total > best_score:
                    best_score = total
                    best_id = ex_id

            # Add best exercise to selection
            if best_id:
                exercise = candidates[best_id]['exercise']
                selected.append({
                    'pk': exercise['pk'],
                    'name': exercise['name'],
                    'primaryMuscles': exercise['primaryMuscles'],
                    'secondaryMuscles': exercise.get('secondaryMuscles', []),
                    'score': round(best_score, 2),
                    'position': position + 1
                })
                used_ids.add(best_id)

                # Track movement family
                family = self.selector._get_exercise_family(best_id)
                if family:
                    families.add(family)

        return selected

    def _run_exhaustive_algorithm(self, candidates: Dict) -> List[Dict]:
        """Execute COMPLETE exhaustive search algorithm"""
        candidate_ids = list(candidates.keys())

        if len(candidate_ids) < 5:
            return self._run_greedy_algorithm(candidates)

        best_order = None
        best_score = float('-inf')
        evaluations_done = 0

        if len(candidate_ids) == 5:
            # Test all permutations directly
            total_evaluations = factorial(5)
            print(f"  Testing all {total_evaluations} permutations...")

            for perm in permutations(candidate_ids):
                evaluations_done += 1
                score = self._evaluate_permutation(perm, candidates)
                if score > best_score:
                    best_score = score
                    best_order = perm

                # Progress update
                if evaluations_done % 20 == 0:
                    progress = evaluations_done * 100 // total_evaluations
                    print(
                        f"    Progress: {evaluations_done}/{total_evaluations} ({progress}%)")
        else:
            # Test all combinations and their permutations
            total_combos = comb(len(candidate_ids), 5)
            total_evaluations = total_combos * factorial(5)
            print(
                f"  Testing {total_combos} combinations x 120 permutations = {total_evaluations:,} total")

            combo_count = 0
            for combo in combinations(candidate_ids, 5):
                combo_count += 1
                # Test all permutations of this combination
                for perm in permutations(combo):
                    evaluations_done += 1
                    score = self._evaluate_permutation(perm, candidates)
                    if score > best_score:
                        best_score = score
                        best_order = perm

                # Adaptive progress update frequency
                num_candidates = len(candidate_ids)
                if num_candidates <= 10:
                    update_freq = 10
                elif num_candidates <= 15:
                    update_freq = 50
                else:
                    update_freq = 500

                if combo_count % update_freq == 0 or combo_count == total_combos:
                    progress_pct = (evaluations_done *
                                    100) // total_evaluations
                    print(
                        f"    Combinations: {combo_count}/{total_combos} | Evaluations: {evaluations_done:,}/{total_evaluations:,} ({progress_pct}%)")

        print(
            f"  Complete: {evaluations_done:,} evaluations, best score: {best_score:.2f}")
        return self._build_final_result(best_order, candidates)

    def _evaluate_permutation(self, order: tuple, candidates: Dict) -> float:
        """Calculate total score for a specific exercise ordering"""
        total_score = 0
        families = set()
        selected = []

        for position, ex_id in enumerate(order):
            exercise = candidates[ex_id]['exercise']
            static = candidates[ex_id]['static_score']

            # Calculate dynamic score based on position and current selection
            dynamic = self.selector._calculate_dynamic_score(
                exercise, position, selected, families, set()
            )

            total_score += static + dynamic

            # Update selection state for next position
            selected.append({
                'pk': exercise['pk'],
                'name': exercise['name'],
                'primaryMuscles': exercise['primaryMuscles'],
                'secondaryMuscles': exercise.get('secondaryMuscles', [])
            })

            # Track movement family
            family = self.selector._get_exercise_family(ex_id)
            if family:
                families.add(family)

        return total_score

    def _build_final_result(self, order: tuple, candidates: Dict) -> List[Dict]:
        """Build final result with complete exercise information"""
        result = []
        families = set()

        for position, ex_id in enumerate(order):
            exercise = candidates[ex_id]['exercise']
            static = candidates[ex_id]['static_score']

            # Calculate dynamic score for this position
            dynamic = self.selector._calculate_dynamic_score(
                exercise, position, result, families, set()
            )

            # Build exercise record with score
            exercise_with_score = {
                'pk': exercise['pk'],
                'name': exercise['name'],
                'primaryMuscles': exercise['primaryMuscles'],
                'secondaryMuscles': exercise.get('secondaryMuscles', []),
                'score': round(static + dynamic, 2),
                'position': position + 1
            }
            result.append(exercise_with_score)

            # Track movement family
            family = self.selector._get_exercise_family(ex_id)
            if family:
                families.add(family)

        return result

    def _print_summary(self, results: List[dict]):
        """Print comprehensive summary of results"""
        print("\n" + "="*80)
        print("ALGORITHM PERFORMANCE COMPARISON REPORT")
        print("Greedy vs. Exhaustive Search")
        print("="*80)

        # Table 1: Performance Metrics
        print("\nTable 1: Performance Metrics")
        print("-" * 80)
        print(f"{'Sample':<8} {'Total':<15} {'Greedy':<12} {'Exhaustive':<12} {'Time':<10} {'Score':<12} {'Score':<12}")
        print(f"{'Size':<8} {'Evaluations':<15} {'Time (s)':<12} {'Time (s)':<12} {'Ratio':<10} {'Gap':<12} {'Improvement':<12}")
        print("-" * 80)

        for result in results:
            size = result['sample_size']

            # Calculate total evaluations
            if size == 5:
                evals = factorial(5)
            else:
                evals = comb(size, 5) * factorial(5)

            g_time = result['greedy_time']
            e_time = result['exhaustive_time']

            # Calculate time ratio
            if g_time > 0:
                ratio = e_time / g_time
                ratio_str = f"{ratio:.1f}x"
            else:
                ratio_str = "N/A"

            # Calculate score improvement
            gap = result['exhaustive_score'] - result['greedy_score']
            improvement = (gap / result['greedy_score']) * \
                100 if result['greedy_score'] > 0 else 0

            print(
                f"{size:<8} {evals:<15,} {g_time:<12.6f} {e_time:<12.6f} {ratio_str:<10} {gap:<12.2f} {improvement:<11.2f}%")

        print("-" * 80)

        # Table 2: Execution Time Categories
        print("\nTable 2: Execution Time Categories")
        print("-" * 80)
        print(f"{'Sample Size':<15} {'Exhaustive Time':<20} {'Category':<20}")
        print("-" * 80)

        for result in results:
            size = result['sample_size']
            e_time = result['exhaustive_time']

            # Categorize execution time
            if e_time < 0.1:
                category = "Instant"
            elif e_time < 1:
                category = "Fast"
            elif e_time < 3:
                category = "Moderate"
            elif e_time < 10:
                category = "Slow"
            else:
                category = "Very Slow"

            print(f"{size:<15} {e_time:<20.4f} {category:<20}")

        print("-" * 80)

        # Table 3: Solution Quality Comparison
        print("\nTable 3: Solution Quality Comparison")
        print("-" * 80)
        print(f"{'Sample Size':<15} {'Greedy Score':<15} {'Exhaustive Score':<18} {'Difference':<12} {'Improvement %':<15}")
        print("-" * 80)

        for result in results:
            size = result['sample_size']
            g_score = result['greedy_score']
            e_score = result['exhaustive_score']
            diff = e_score - g_score
            imp = (diff / g_score) * 100 if g_score > 0 else 0

            print(
                f"{size:<15} {g_score:<15.2f} {e_score:<18.2f} {diff:<12.2f} {imp:<14.2f}%")

        print("-" * 80)
        print("\nEnd of Report")
        print("="*80)


def main():
    """Main execution function"""
    tester = SmallSampleExhaustiveTester()
    tester.run_test()


if __name__ == "__main__":
    main()
