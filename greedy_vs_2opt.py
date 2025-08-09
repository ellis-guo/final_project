"""
Greedy vs Greedy+2-opt Algorithm Performance Test

This module compares the performance of pure greedy algorithm against
greedy with 2-opt local search optimization using the actual exercise database.
"""

import time
from typing import List, Dict, Set, Tuple
from algorithms.greedy_selector import GreedySelector
from algorithms.hybrid_selector import HybridSelector


class GreedyVs2OptTester:
    """Test greedy vs greedy+2-opt performance on real data"""

    def __init__(self):
        self.greedy_selector = GreedySelector()
        self.hybrid_selector = HybridSelector()

    def run_test(self):
        """Execute the comparison test"""
        print("="*80)
        print("ALGORITHM PERFORMANCE TEST")
        print("Greedy vs. Greedy + 2-opt Optimization")
        print("="*80)

        # Display configuration
        print("\nTest Configuration:")
        print(f"  Training Days: {self.greedy_selector.TRAINING_DAYS}")
        print(f"  Exercises per Day: 5")
        print(f"  Total Exercise Database: 340 exercises")
        print(
            f"  Muscle Preferences: {self.greedy_selector.MUSCLE_PREFERENCES}")
        print(
            f"  Excluded Exercises: {len(self.greedy_selector.EXCLUDED_EXERCISES)} exercises")

        # Run greedy algorithm
        print("\n" + "-"*80)
        print("Running Pure Greedy Algorithm...")
        start_time = time.perf_counter()
        greedy_plan = self.greedy_selector.generate_weekly_plan()
        greedy_time = time.perf_counter() - start_time
        greedy_scores = self._extract_scores(greedy_plan)
        print(f"Completed in {greedy_time:.4f} seconds")

        # Run greedy + 2-opt using hybrid selector
        print("\nRunning Greedy + 2-opt Optimization...")
        start_time = time.perf_counter()
        optimized_plan, optimization_details = self._run_greedy_with_2opt()
        optimized_time = time.perf_counter() - start_time
        optimized_scores = self._extract_scores(optimized_plan)
        print(f"Completed in {optimized_time:.4f} seconds")

        # Generate report
        self._print_report(
            greedy_plan, greedy_time, greedy_scores,
            optimized_plan, optimized_time, optimized_scores,
            optimization_details
        )

    def _run_greedy_with_2opt(self) -> Tuple[Dict, List[Dict]]:
        """
        Run greedy algorithm followed by 2-opt optimization
        Returns both the plan and optimization details
        """
        optimization_details = []
        weekly_plan = {}

        # Get training template
        template = self.hybrid_selector.training_templates[
            str(self.hybrid_selector.TRAINING_DAYS)]
        global_selected_ids = set()

        for day_num, muscle_groups in enumerate(template, 1):
            day_key = f"Day {day_num}"

            # Get candidates
            candidates = self.hybrid_selector._get_candidate_exercises(
                muscle_groups, global_selected_ids)

            # Run greedy first
            greedy_result = self.hybrid_selector._greedy_search(
                candidates, global_selected_ids)
            greedy_score = sum(ex['score'] for ex in greedy_result)

            # Apply 2-opt optimization
            optimized_result, iterations, improvements = self._two_opt_with_tracking(
                greedy_result, candidates, global_selected_ids)
            optimized_score = sum(ex['score'] for ex in optimized_result)

            # Record optimization details
            optimization_details.append({
                'day': day_key,
                'initial_score': greedy_score,
                'final_score': optimized_score,
                'improvement': optimized_score - greedy_score,
                'iterations': iterations,
                'improvements_made': improvements
            })

            # Update global selected IDs
            for exercise in optimized_result:
                global_selected_ids.add(exercise['pk'])

            # Build day plan
            weekly_plan[day_key] = {
                'type': ' & '.join([mg.title() for mg in muscle_groups]),
                'muscle_groups': muscle_groups,
                'exercises': optimized_result,
                'total_score': round(optimized_score, 2)
            }

        return weekly_plan, optimization_details

    def _two_opt_with_tracking(self, initial_solution: List[Dict],
                               candidates: Dict[int, Dict],
                               global_selected_ids: Set[int]) -> Tuple[List[Dict], int, int]:
        """
        2-opt optimization with detailed tracking
        Returns: (optimized_solution, total_iterations, improvements_made)
        """
        current_solution = initial_solution.copy()
        current_score = sum(ex['score'] for ex in current_solution)

        iterations = 0
        improvements_made = 0
        max_iterations = self.hybrid_selector.config['algorithm_params'].get(
            'max_2opt_iterations', 100)

        improved = True
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
                    new_solution = self.hybrid_selector._build_solution(
                        tuple(exercise_ids), candidates, global_selected_ids)
                    new_score = sum(ex['score'] for ex in new_solution)

                    # Accept improvement
                    if new_score > current_score:
                        current_solution = new_solution
                        current_score = new_score
                        improved = True
                        improvements_made += 1
                        break

                if improved:
                    break

        return current_solution, iterations, improvements_made

    def _extract_scores(self, plan: Dict) -> Dict:
        """Extract scores from weekly plan"""
        scores = {
            'daily': {},
            'total': 0
        }

        for day, data in plan.items():
            if 'exercises' in data and data['exercises']:
                day_score = sum(ex['score'] for ex in data['exercises'])
                scores['daily'][day] = round(day_score, 2)
                scores['total'] += day_score
            else:
                scores['daily'][day] = 0

        scores['total'] = round(scores['total'], 2)
        return scores

    def _print_report(self, greedy_plan: Dict, greedy_time: float, greedy_scores: Dict,
                      optimized_plan: Dict, optimized_time: float, optimized_scores: Dict,
                      optimization_details: List[Dict]):
        """Print comprehensive comparison report"""

        print("\n" + "="*80)
        print("PERFORMANCE COMPARISON REPORT")
        print("="*80)

        # Table 1: Overall Performance
        print("\nTable 1: Overall Performance Metrics")
        print("-"*80)
        print(
            f"{'Metric':<25} {'Pure Greedy':<20} {'Greedy + 2-opt':<20} {'Difference':<20}")
        print("-"*80)

        # Execution time
        time_diff = optimized_time - greedy_time
        time_ratio = optimized_time / greedy_time if greedy_time > 0 else 0
        print(f"{'Execution Time (s)':<25} {greedy_time:<20.4f} {optimized_time:<20.4f} {f'+{time_diff:.4f} ({time_ratio:.1f}x)':<20}")

        # Total score
        score_diff = optimized_scores['total'] - greedy_scores['total']
        score_improvement = (
            score_diff / greedy_scores['total']) * 100 if greedy_scores['total'] > 0 else 0
        print(
            f"{'Total Weekly Score':<25} {greedy_scores['total']:<20.2f} {optimized_scores['total']:<20.2f} {f'+{score_diff:.2f} ({score_improvement:.1f}%)':<20}")

        print("-"*80)

        # Table 2: Daily Score Comparison
        print("\nTable 2: Daily Score Breakdown")
        print("-"*80)
        print(f"{'Day':<15} {'Pure Greedy':<15} {'Greedy + 2-opt':<15} {'Improvement':<15} {'Change %':<15}")
        print("-"*80)

        for day in greedy_scores['daily'].keys():
            g_score = greedy_scores['daily'][day]
            o_score = optimized_scores['daily'][day]
            diff = o_score - g_score
            pct = (diff / g_score) * 100 if g_score > 0 else 0
            print(
                f"{day:<15} {g_score:<15.2f} {o_score:<15.2f} {diff:<15.2f} {pct:<14.1f}%")

        print("-"*80)

        # Table 3: 2-opt Optimization Details
        print("\nTable 3: 2-opt Optimization Process")
        print("-"*80)
        print(f"{'Day':<10} {'Initial':<12} {'Final':<12} {'Improvement':<12} {'Iterations':<12} {'Swaps Made':<12}")
        print(f"{'':10} {'Score':<12} {'Score':<12} {'':12} {'':12} {'':12}")
        print("-"*80)

        total_iterations = 0
        total_swaps = 0

        for detail in optimization_details:
            print(f"{detail['day']:<10} {detail['initial_score']:<12.2f} {detail['final_score']:<12.2f} "
                  f"{detail['improvement']:<12.2f} {detail['iterations']:<12} {detail['improvements_made']:<12}")
            total_iterations += detail['iterations']
            total_swaps += detail['improvements_made']

        print("-"*80)
        print(f"{'Total':<10} {'':12} {'':12} {score_diff:<12.2f} {total_iterations:<12} {total_swaps:<12}")
        print("-"*80)

        # Summary Statistics
        print("\nSummary Statistics:")
        print("-"*40)
        print(
            f"Average iterations per day: {total_iterations / len(optimization_details):.1f}")
        print(
            f"Average swaps per day: {total_swaps / len(optimization_details):.1f}")
        print(
            f"Days with improvements: {sum(1 for d in optimization_details if d['improvements_made'] > 0)}/{len(optimization_details)}")
        print(f"Overall score improvement: {score_improvement:.2f}%")
        print(f"Time overhead for 2-opt: {(time_ratio - 1) * 100:.1f}%")

        print("\n" + "="*80)
        print("End of Report")
        print("="*80)


def main():
    """Main execution function"""
    tester = GreedyVs2OptTester()
    tester.run_test()


if __name__ == "__main__":
    main()
