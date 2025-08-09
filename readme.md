# Intelligent Fitness Plan Generator

An advanced exercise selection system that generates personalized weekly workout plans using intelligent algorithms and scientific training principles.

## Features

- **Smart Algorithm Selection**: Automatically chooses between exhaustive search (for small problems) and greedy optimization (for large problems)
- **Scientific Training Templates**: 1-7 day training splits based on exercise science principles
- **Multi-Dimensional Scoring**: Evaluates exercises across 6 classification dimensions
- **Personalized Preferences**: Adjustable muscle group coefficients for customized plans
- **Diversity Optimization**: Ensures balanced workouts with variety in movement patterns

## Quick Start

```bash
# Run the system
python main.py

# The system will:
# 1. Display current configuration
# 2. Generate optimized weekly plan
# 3. Show execution time and scores
# 4. Optionally display detailed workout plan
```

## Project Structure

```
final_project/
├── algorithms/
│   ├── __init__.py              # Package initialization
│   ├── base_selector.py         # Abstract base class with shared logic
│   ├── greedy_selector.py       # Greedy algorithm implementation
│   └── hybrid_selector.py       # Adaptive hybrid algorithm
├── classification/
│   ├── categoryMapping.json     # Exercise-to-muscle mapping
│   ├── preferenceMapping.json   # Muscle group categories
│   ├── trainingTemplates.json   # Training split templates
│   ├── type1_isMajor.json      # Major/minor muscle classification
│   ├── type2_isCompound.json   # Compound/isolation classification
│   ├── type3_isSingle.json     # Bilateral/unilateral classification
│   ├── type4_isMachine.json    # Free weight/machine classification
│   ├── type5_isCommon.json     # Common/uncommon exercises
│   └── type6_movementFamily.json # Movement pattern families
├── config.json                  # Algorithm configuration
├── strength.json                # Database of 340 exercises
├── main.py                      # Main entry point
└── README.md                    # This file
```

## Configuration

### User Settings (in base_selector.py)

```python
# Training days per week (1-7)
TRAINING_DAYS = 5

# Muscle group preferences (0.1-10.0, default: 1.0)
MUSCLE_PREFERENCES = {
    "chest": 1.2,    # 20% bonus
    "back": 1.0,     # Normal
    "shoulder": 1.0,
    "arm": 1.0,
    "leg": 0.8,      # 20% reduction
    "core": 1.0
}

# Excluded exercise IDs
EXCLUDED_EXERCISES = {35, 42}  # Example IDs to exclude
```

### Algorithm Settings (config.json)

```json
{
  "algorithm_params": {
    "exercises_per_day": 5,
    "exhaustive_threshold": 10, // Switch point between algorithms
    "max_2opt_iterations": 100
  }
}
```

## Training Templates

The system supports 7 different training splits:

1. **1 Day**: Full Body
2. **2 Days**: Upper/Lower Split
3. **3 Days**: Push/Pull/Legs
4. **4 Days**: Push/Pull × 2
5. **5 Days**: Bro Split (Chest, Legs, Back, Shoulders, Arms)
6. **6 Days**: Push/Pull/Legs × 2
7. **7 Days**: Push/Pull/Legs × 2 + Active Recovery

## Scoring System

### Static Score (Position-Independent)

- Primary muscles: 3.0 ÷ num_muscles × preference
- Secondary muscles: 2.0 ÷ num_muscles × preference
- Common exercise bonus: +2.0

### Dynamic Score (Position-Dependent)

#### Layer 1: Position Bonuses

| Exercise Type | Pos 1 | Pos 2 | Pos 3 | Pos 4 | Pos 5 |
| ------------- | ----- | ----- | ----- | ----- | ----- |
| Major Muscle  | +8    | +5    | 0     | 0     | 0     |
| Minor Muscle  | 0     | 0     | 0     | +5    | +8    |
| Compound      | +8    | +5    | 0     | 0     | 0     |
| Isolation     | 0     | 0     | 0     | +5    | +8    |
| Free Weight   | +3    | +2    | 0     | 0     | 0     |
| Machine       | 0     | 0     | 0     | +2    | +3    |

#### Layer 2: Diversity Penalties

- Balance threshold: 3 exercises
- Penalty for exceeding: -3 points

#### Layer 3: Repetition Penalties

- Same movement family: -10
- Weekly repetition: -8
- Muscle group overlap: -1 per overlap

## Algorithm Details

### Greedy Selector

- **Time Complexity**: O(n × 5)
- **Space Complexity**: O(n)
- **Strategy**: Selects best exercise for each position sequentially

### Hybrid Selector

- **Adaptive Strategy**:
  - n ≤ 10: Complete exhaustive search (O(C(n,5) × 120))
  - n > 10: Greedy + 2-opt optimization
- **Guarantees**: Global optimum for small problems, good solutions for large problems

## Performance Benchmarks

Based on testing with 340 exercises:

| Candidates | Algorithm    | Time   | Quality      |
| ---------- | ------------ | ------ | ------------ |
| 5          | Exhaustive   | <0.01s | Optimal      |
| 10         | Exhaustive   | ~1s    | Optimal      |
| 15         | Exhaustive   | ~15s   | Optimal      |
| 20         | Exhaustive   | ~80s   | Optimal      |
| 30+        | Greedy+2-opt | <0.1s  | Near-optimal |

## Example Output

```
CURRENT CONFIGURATION:
----------------------------------------
Training Days: 5
Algorithm: Hybrid (Adaptive)
Exhaustive Threshold: 10 candidates

RESULTS SUMMARY
----------------------------------------
Generation Time: 0.156 seconds

Daily Scores:
Day 1   : 5 exercises | Score:  67.45
Day 2   : 5 exercises | Score:  62.30
Day 3   : 5 exercises | Score:  71.20
Day 4   : 5 exercises | Score:  65.80
Day 5   : 5 exercises | Score:  69.15
----------------------------------------
Total   : 25 exercises | Score: 335.90
```

## Requirements

- Python 3.6+
- No external dependencies (uses only Python standard library)

## Usage Examples

### Basic Usage

```python
from algorithms import HybridSelector

# Create selector
selector = HybridSelector()

# Generate plan
plan = selector.generate_weekly_plan()

# Display results
selector.print_detailed_plan(plan)
```

### Custom Configuration

```python
from algorithms import HybridSelector

selector = HybridSelector()

# Customize settings
selector.TRAINING_DAYS = 3
selector.MUSCLE_PREFERENCES = {
    "chest": 1.5,  # 50% more chest focus
    "back": 1.2,
    "shoulder": 1.0,
    "arm": 0.8,
    "leg": 1.0,
    "core": 0.5   # 50% less core
}

# Exclude specific exercises
selector.EXCLUDED_EXERCISES = {35, 42, 108}

# Generate customized plan
plan = selector.generate_weekly_plan()
```

## License

MIT License

## Author

Developed as part of an intelligent fitness planning system project.

## Acknowledgments

- Exercise database includes 340 professionally curated exercises
- Training templates based on established exercise science principles
- Scoring system designed to optimize workout quality and variety
