"""
Exercise Selection System - Main Entry Point

Demonstrates the hybrid algorithm for generating optimized workout plans.
"""

from algorithms import HybridSelector
import time


def main():
    """Generate and display workout plan using hybrid algorithm."""

    print("="*70)
    print(" INTELLIGENT FITNESS PLAN GENERATOR ")
    print("="*70)

    # Initialize selector
    selector = HybridSelector()

    # Display current configuration
    print("\nCURRENT CONFIGURATION:")
    print("-"*40)
    print(f"Training Days: {selector.TRAINING_DAYS}")
    print(f"Algorithm: Hybrid (Adaptive)")
    print(
        f"Exhaustive Threshold: {selector.config['algorithm_params'].get('exhaustive_threshold', 10)} candidates")

    print(f"\nMuscle Preferences:")
    for muscle, coefficient in selector.MUSCLE_PREFERENCES.items():
        status = "default" if coefficient == 1.0 else f"{coefficient:.1f}x"
        print(f"  {muscle:8s}: {status}")

    if selector.EXCLUDED_EXERCISES:
        print(f"\nExcluded Exercises: {selector.EXCLUDED_EXERCISES}")
    else:
        print(f"\nExcluded Exercises: None")

    # Generate plan with timing
    print("\n" + "="*70)
    print(" GENERATING WEEKLY PLAN... ")
    print("="*70)

    start_time = time.perf_counter()
    weekly_plan = selector.generate_weekly_plan()
    elapsed_time = time.perf_counter() - start_time

    # Display summary results
    print("\n" + "="*70)
    print(" RESULTS SUMMARY ")
    print("="*70)

    print(f"\nGeneration Time: {elapsed_time:.3f} seconds")
    print("\nDaily Scores:")
    print("-"*40)

    total_score = 0
    total_exercises = 0

    for day, plan in weekly_plan.items():
        if plan['exercises']:
            exercises_count = len(plan['exercises'])
            day_score = plan['total_score']
            total_exercises += exercises_count
            total_score += day_score
            print(f"{day:8s}: {exercises_count} exercises | Score: {day_score:6.2f}")
        else:
            print(f"{day:8s}: Rest Day")

    print("-"*40)
    print(f"{'Total':8s}: {total_exercises} exercises | Score: {total_score:6.2f}")

    # Ask for detailed plan
    print("\n" + "="*70)
    show_detailed = input(
        "\nShow detailed workout plan? (y/n): ").strip().lower()

    if show_detailed == 'y':
        print("\n" + "="*70)
        print(" DETAILED WORKOUT PLAN ")
        print("="*70)

        for day, plan in weekly_plan.items():
            print(f"\n{day}: {plan['type']}")

            if 'muscle_groups' in plan and plan['muscle_groups']:
                print(f"Target Muscles: {', '.join(plan['muscle_groups'])}")

            if plan['exercises']:
                print("-"*50)
                for i, exercise in enumerate(plan['exercises'], 1):
                    print(f"\n{i}. [{exercise['pk']}] {exercise['name']}")
                    print(
                        f"   Score: {exercise['score']:.2f} (Static: {exercise['static_score']:.2f}, Dynamic: {exercise['dynamic_score']:.2f})")
                    print(
                        f"   Primary: {', '.join(exercise['primaryMuscles'])}")
                    if exercise.get('secondaryMuscles'):
                        print(
                            f"   Secondary: {', '.join(exercise['secondaryMuscles'])}")
            else:
                print("   Rest and Recovery")

    print("\n" + "="*70)
    print(" Thank you for using the Exercise Selection System! ")
    print("="*70)


if __name__ == "__main__":
    main()
