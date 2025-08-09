"""
Greedy vs Hybrid Algorithm Performance Test

This module compares the performance of pure greedy algorithm against
the hybrid algorithm (adaptive exhaustive/greedy+2-opt) using the actual exercise database.
"""

import time
from typing import Dict, List
from algorithms.greedy_selector import GreedySelector
from algorithms.hybrid_selector import HybridSelector


class GreedyVsHybridTester:
    """Test greedy vs hybrid algorithm performance on real data"""

    def __init__(self):
        self.greedy_selector = GreedySelector()
        self.hybrid_selector = HybridSelector()

    def run_test(self):
        """Execute the comparison test"""
        print("="*80)
        print("ALGORITHM PERFORMANCE TEST")
        print("Greedy vs. Hybrid (Adaptive) Algorithm")
        print("="*80)

        # Display configuration
        print("\nTest Configuration:")
        print(f"  Training Days: {self.greedy_selector.TRAINING_DAYS}")
        print(f"  Exercises per Day: 5")
        print(f"  Total Exercise Database: 340 exercises")
        print(
            f"  Exhaustive Search Threshold: {self.hybrid_selector.config['algorithm_params'].get('exhaustive_threshold', 10)} candidates")
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
        greedy_stats = self._collect_algorithm_stats(
            self.greedy_selector, greedy_plan)
        print(f"Completed in {greedy_time:.4f} seconds")

        # Run hybrid algorithm
        print("\nRunning Hybrid Algorithm (Adaptive)...")
        start_time = time.perf_counter()
        hybrid_plan = self.hybrid_selector.generate_weekly_plan()
        hybrid_time = time.perf_counter() - start_time
        hybrid_scores = self._extract_scores(hybrid_plan)
        hybrid_stats = self._collect_algorithm_stats(
            self.hybrid_selector, hybrid_plan)
        print(f"Completed in {hybrid_time:.4f} seconds")

        # Generate comprehensive report
        self._print_report(
            greedy_plan, greedy_time, greedy_scores, greedy_stats,
            hybrid_plan, hybrid_time, hybrid_scores, hybrid_stats
        )

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

    def _collect_algorithm_stats(self, selector, plan: Dict) -> Dict:
        """Collect statistics about algorithm execution"""
        stats = {
            'days_processed': 0,
            'total_exercises': 0,
            'unique_muscle_groups': set(),
            'exercise_types': {'major': 0, 'compound': 0, 'machine': 0},
            'avg_candidates_per_day': []
        }

        for day, data in plan.items():
            if 'exercises' in data and data['exercises']:
                stats['days_processed'] += 1
                stats['total_exercises'] += len(data['exercises'])

                # Track muscle groups
                if 'muscle_groups' in data:
                    stats['unique_muscle_groups'].update(data['muscle_groups'])

                # Count exercise types
                for ex in data['exercises']:
                    ex_id = ex['pk']
                    if ex_id in selector.classifications['major']:
                        stats['exercise_types']['major'] += 1
                    if ex_id in selector.classifications['compound']:
                        stats['exercise_types']['compound'] += 1
                    if ex_id in selector.classifications['machine']:
                        stats['exercise_types']['machine'] += 1

        return stats

    def _print_report(self, greedy_plan: Dict, greedy_time: float, greedy_scores: Dict, greedy_stats: Dict,
                      hybrid_plan: Dict, hybrid_time: float, hybrid_scores: Dict, hybrid_stats: Dict):
        """Print comprehensive comparison report"""

        print("\n" + "="*80)
        print("PERFORMANCE COMPARISON REPORT")
        print("="*80)

        # Table 1: Overall Performance
        print("\nTable 1: Overall Performance Metrics")
        print("-"*80)
        print(
            f"{'Metric':<30} {'Pure Greedy':<20} {'Hybrid Algorithm':<20} {'Difference':<20}")
        print("-"*80)

        # Execution time
        time_diff = hybrid_time - greedy_time
        time_ratio = hybrid_time / greedy_time if greedy_time > 0 else 0
        print(f"{'Execution Time (s)':<30} {greedy_time:<20.4f} {hybrid_time:<20.4f} {f'+{time_diff:.4f} ({time_ratio:.1f}x)':<20}")

        # Total score
        score_diff = hybrid_scores['total'] - greedy_scores['total']
        score_improvement = (
            score_diff / greedy_scores['total']) * 100 if greedy_scores['total'] > 0 else 0
        print(
            f"{'Total Weekly Score':<30} {greedy_scores['total']:<20.2f} {hybrid_scores['total']:<20.2f} {f'+{score_diff:.2f} ({score_improvement:.1f}%)':<20}")

        # Average daily score
        avg_greedy = greedy_scores['total'] / greedy_stats['days_processed']
        avg_hybrid = hybrid_scores['total'] / hybrid_stats['days_processed']
        avg_diff = avg_hybrid - avg_greedy
        print(f"{'Average Daily Score':<30} {avg_greedy:<20.2f} {avg_hybrid:<20.2f} {f'+{avg_diff:.2f}':<20}")

        print("-"*80)

        # Table 2: Daily Score Comparison
        print("\nTable 2: Daily Score Breakdown")
        print("-"*80)
        print(
            f"{'Day':<15} {'Pure Greedy':<15} {'Hybrid':<15} {'Improvement':<15} {'Change %':<15}")
        print("-"*80)

        for day in greedy_scores['daily'].keys():
            g_score = greedy_scores['daily'][day]
            h_score = hybrid_scores['daily'][day]
            diff = h_score - g_score
            pct = (diff / g_score) * 100 if g_score > 0 else 0
            print(
                f"{day:<15} {g_score:<15.2f} {h_score:<15.2f} {diff:<15.2f} {pct:<14.1f}%")

        # Add weekly total row
        print("-"*80)
        print(f"{'Weekly Total':<15} {greedy_scores['total']:<15.2f} {hybrid_scores['total']:<15.2f} "
              f"{score_diff:<15.2f} {score_improvement:<14.1f}%")
        print("-"*80)

        # Table 3: Exercise Type Distribution
        print("\nTable 3: Exercise Type Distribution")
        print("-"*80)
        print(
            f"{'Exercise Type':<20} {'Pure Greedy':<15} {'Hybrid':<15} {'Difference':<15}")
        print("-"*80)

        g_total = greedy_stats['total_exercises']
        h_total = hybrid_stats['total_exercises']

        # Major muscle exercises
        g_major_pct = (greedy_stats['exercise_types']
                       ['major'] / g_total) * 100 if g_total > 0 else 0
        h_major_pct = (hybrid_stats['exercise_types']
                       ['major'] / h_total) * 100 if h_total > 0 else 0
        print(f"{'Major Muscle':<20} {greedy_stats['exercise_types']['major']:<3} ({g_major_pct:5.1f}%) "
              f"{'':6} {hybrid_stats['exercise_types']['major']:<3} ({h_major_pct:5.1f}%) "
              f"{'':6} {hybrid_stats['exercise_types']['major'] - greedy_stats['exercise_types']['major']:+3}")

        # Compound exercises
        g_compound_pct = (
            greedy_stats['exercise_types']['compound'] / g_total) * 100 if g_total > 0 else 0
        h_compound_pct = (
            hybrid_stats['exercise_types']['compound'] / h_total) * 100 if h_total > 0 else 0
        print(f"{'Compound':<20} {greedy_stats['exercise_types']['compound']:<3} ({g_compound_pct:5.1f}%) "
              f"{'':6} {hybrid_stats['exercise_types']['compound']:<3} ({h_compound_pct:5.1f}%) "
              f"{'':6} {hybrid_stats['exercise_types']['compound'] - greedy_stats['exercise_types']['compound']:+3}")

        # Machine exercises
        g_machine_pct = (
            greedy_stats['exercise_types']['machine'] / g_total) * 100 if g_total > 0 else 0
        h_machine_pct = (
            hybrid_stats['exercise_types']['machine'] / h_total) * 100 if h_total > 0 else 0
        print(f"{'Machine':<20} {greedy_stats['exercise_types']['machine']:<3} ({g_machine_pct:5.1f}%) "
              f"{'':6} {hybrid_stats['exercise_types']['machine']:<3} ({h_machine_pct:5.1f}%) "
              f"{'':6} {hybrid_stats['exercise_types']['machine'] - greedy_stats['exercise_types']['machine']:+3}")

        print("-"*80)

        # Table 4: Algorithm Characteristics
        print("\nTable 4: Algorithm Characteristics")
        print("-"*80)
        print(f"{'Characteristic':<35} {'Pure Greedy':<25} {'Hybrid Algorithm':<25}")
        print("-"*80)

        print(
            f"{'Algorithm Type':<35} {'Local Optimization':<25} {'Adaptive (Exhaustive/2-opt)':<25}")
        print(f"{'Solution Quality Guarantee':<35} {'Local Optimum':<25} {'Global/Near-Global Optimum':<25}")
        print(
            f"{'Time Complexity (per day)':<35} {'O(n × m)':<25} {'O(C(n,5)×5!) or O(n×m×i)':<25}")
        print(f"{'Deterministic':<35} {'Yes':<25} {'Yes':<25}")
        print(f"{'Scalability':<35} {'Excellent':<25} {'Good (adaptive)':<25}")

        print("-"*80)

        # Summary Statistics
        print("\nSummary Statistics:")
        print("-"*40)

        print(f"Score Improvement: {score_improvement:.2f}%")
        print(f"Time Ratio: {time_ratio:.2f}x")
        print(
            f"Score per Second (Greedy): {greedy_scores['total']/greedy_time:.2f}")
        print(
            f"Score per Second (Hybrid): {hybrid_scores['total']/hybrid_time:.2f}")
        print(
            f"Efficiency Ratio: {score_improvement/time_ratio:.2f}% improvement per unit time")

        print("\n" + "="*80)
        print("End of Report")
        print("="*80)


def main():
    """Main execution function"""
    tester = GreedyVsHybridTester()
    tester.run_test()


if __name__ == "__main__":
    main()
