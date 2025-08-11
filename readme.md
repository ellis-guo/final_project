# 🏋️ Intelligent Fitness Plan Generator

> One-click personalized weekly workout plans powered by intelligent algorithms and exercise science

## ✨ Features

- 🚀 **One-Click Launch** - No installation required, just double-click and go
- 🧬 **Smart Algorithms** - Adaptive selection between exhaustive/greedy/hybrid approaches
- 📊 **Scientific Scoring** - 6-dimensional evaluation with multi-layer optimization
- 🎯 **Personalization** - Support for 1-7 training days with muscle group preferences
- 💪 **Professional Templates** - Science-based training splits for all fitness levels

## 🚀 Quick Start (30 seconds)

### Easiest Method: Direct Run

1. Download `WorkoutPlanner.exe`
2. Double-click to run
3. Browser opens automatically - start training!

**That's it!** No Python, no configuration needed.

## 📸 Screenshots

![Interface](https://github.com/ellis-guo/final_project/blob/main/images/interface.png)

## 🎮 User Guide

### Three Ways to Run

#### Option 1: Standalone Program (Recommended for Users)

```
Run dist/WorkoutPlanner.exe directly
```

#### Option 2: Web Interface (For Developers)

```bash
python app.py
# Visit http://localhost:5000
```

#### Option 3: Command Line (For Debugging)

```bash
python main.py
```

### How to Use

1. Select training days (1-7 days)
2. Set muscle group priorities (drag sliders, levels 1-5)
3. Click "Generate Workout Plan"
4. Review your generated plan
5. Click exercise names for detailed instructions


## 📋 System Components

### Key Interfaces

- **Command-line interface (main.py)**: Displays daily workout scores and total metrics; users can enter 'y' to view detailed exercise selections
- **Configuration module (base_selector.py)**: Sets user parameters including training days, muscle group coefficients, and excluded exercises
- **Web interface (app.py)**: Provides graphical interface with 5-tier muscle priority system for real-time plan generation
- **Standalone executable (WorkoutPlanner.exe)**: Packaged with PyInstaller, runs without Python installation by launching local Flask server and auto-opening browser


## 🧠 Core Algorithms

### Intelligent Algorithm Selection

- **Small Scale (≤10 candidates)**: Exhaustive search, guarantees global optimum
- **Large Scale (>10 candidates)**: Greedy + 2-opt optimization, fast near-optimal solution

### Performance Benchmarks

| Candidates | Algorithm    | Runtime | Solution Quality |
| ---------- | ------------ | ------- | ---------------- |
| 5          | Exhaustive   | <0.01s  | Optimal          |
| 10         | Exhaustive   | ~2s     | Optimal          |
| 30+        | Greedy+2-opt | <0.1s   | Near-optimal     |


## 📊 Test Results & Analysis

For detailed algorithm performance comparisons and workout plan quality assessments, see our comprehensive test results in:
- **📄 [Test Results Sample Document](test_result_samples.pdf)** - Contains program output examples and validation against exercise science guidelines


## 📊 Scientific Scoring System

### Multi-Dimensional Evaluation

- **Major/Minor Muscle Classification** - Proper training focus distribution
- **Compound/Isolation Balance** - Comprehensive muscle stimulation
- **Free Weight/Machine Mix** - Balance between stability and safety
- **Movement Pattern Diversity** - Avoid repetition, maximize effectiveness
- **Position Optimization** - Exercise order based on fatigue management
- **Weekly Deduplication** - Prevent overtraining

### Scoring Formula

#### Static Score (Position-Independent)

- Primary muscles: `3.0 ÷ muscle_count × preference_coefficient`
- Secondary muscles: `2.0 ÷ muscle_count × preference_coefficient`
- Common exercise bonus: `+2.0`

#### Dynamic Score (Position-Dependent)

- **Position Bonuses**: Compound exercises front-loaded, isolation exercises back-loaded
- **Diversity Penalties**: `-3` points when exceeding threshold
- **Repetition Penalties**: `-10` for same movement family

## 🏗️ Project Structure

```
final_project/
├── dist/
│   └── WorkoutPlanner.exe     # Standalone executable
├── algorithms/                # Core algorithms
│   ├── base_selector.py       # Base class with shared logic
│   ├── greedy_selector.py     # Greedy algorithm
│   └── hybrid_selector.py     # Adaptive hybrid algorithm
├── classification/            # Exercise classification data
│   ├── categoryMapping.json   # Exercise-to-muscle mapping
│   ├── trainingTemplates.json # Training split templates
│   └── type1-6_*.json         # 6-dimensional classifications
├── templates/                 # Web interface templates
├── test_result_sample.pdf     # Result tables
├── static/                    # Static resources
├── strength.json              # Database of 340 exercises
├── config.json                # Algorithm configuration
├── app.py                     # Flask web application
└── main.py                    # Command line entry point
```

## 🛠️ Tech Stack

- **Backend**: Python 3.6+
- **Algorithms**: Combinatorial optimization, Greedy, 2-opt
- **Web Framework**: Flask
- **Frontend**: HTML/CSS/JavaScript
- **Packaging**: PyInstaller
- **Data**: JSON (340 professional exercises)

## 📈 Algorithm Performance Comparison
Time-Quality tradeoff curves for different algorithms at various scales

### Test Results Summary

- **Greedy vs Hybrid**: 5-10% quality improvement, 2-3x time overhead
- **Greedy vs 2-opt**: 3-5% quality improvement, 50% time increase
- **Exhaustive Search**: Guarantees global optimum for small problems

## 🎯 Training Templates

7 science-based training splits available:

1. **1 Day**: Full Body
2. **2 Days**: Upper/Lower Split
3. **3 Days**: Push/Pull/Legs (PPL)
4. **4 Days**: Push/Pull × 2
5. **5 Days**: Bro Split (Chest, Legs, Back, Shoulders, Arms)
6. **6 Days**: Push/Pull/Legs × 2
7. **7 Days**: Push/Pull/Legs × 2 + Rest

## 💡 Use Cases

- 💪 **Fitness Enthusiasts**: Get professional, personalized workout plans
- 👨‍💻 **Developers**: Learn combinatorial optimization implementations
- 🏋️ **Personal Trainers**: Quickly generate client programs
- 📚 **Students**: Algorithm course project reference

## 🔧 Advanced Configuration

### User Preferences (base_selector.py)

```python
# Training days per week
TRAINING_DAYS = 5

# Muscle group preference coefficients (0.3-1.5)
MUSCLE_PREFERENCES = {
    "chest": 0.9,   # Standard weight (Tier 3)
    "back": 0.9,
    "shoulder": 0.3,# Minimal training (Tier 1)
    "arm": 0.9,
    "leg": 1.5,     # Intensive training (Tier 5)
    "core": 0.9
}

# Excluded exercise IDs
EXCLUDED_EXERCISES = {...}
```

### Algorithm Parameters (config.json)

```json
{
  "algorithm_params": {
    "exercises_per_day": 5,
    "exhaustive_threshold": 10,
    "max_2opt_iterations": 100
  }
}
```

## 📝 Development Documentation

### Adding New Exercises

1. Edit `strength.json` to add exercise information
2. Update classification files in `classification/`
3. Run tests to ensure proper categorization

### Implementing New Algorithms

1. Inherit from `BaseSelector` class
2. Implement `_select_exercises_for_day` method
3. Register new algorithm in `main.py`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

## 👨‍💻 Author

**[Ellis Guo](https://github.com/ellis-guo)**,
**[Clarisse Li](https://github.com/clarisseli)**,
**Difan Xie**

- Northeastern University CS5800 Algorithms Final Project

## 🙏 Acknowledgments

- Professional exercise database from https://github.com/longhaul-fitness/exercises.git
- Exercise science training guidelines from ACSM and NASM
- Combinatorial optimization theory
