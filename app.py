from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from algorithms import HybridSelector
import json

app = Flask(__name__)
CORS(app)

# Tier coefficients mapping
TIER_COEFFICIENTS = {
    1: 0.3,  # Minimal training
    2: 0.6,
    3: 0.9,  # Normal
    4: 1.2,
    5: 1.5   # Intensive training
}

# Correct 7-day template (PPL x2 + Rest)
CUSTOM_7DAY_TEMPLATE = [
    ["chest", "shoulder", "tricep"],  # Day 1: Push
    ["legs"],                         # Day 2: Legs
    ["back", "bicep"],                # Day 3: Pull
    ["chest", "shoulder", "tricep"],  # Day 4: Push
    ["legs"],                         # Day 5: Legs
    ["back", "bicep"],                # Day 6: Pull
    []                                # Day 7: Rest
]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    try:
        data = request.json if request.json else {}

        # Initialize selector
        selector = HybridSelector()

        # Apply user settings
        if 'training_days' in data:
            training_days = int(data['training_days'])
            selector.TRAINING_DAYS = training_days

            # Override template for 7 days to ensure rest day
            if training_days == 7:
                selector.training_templates["7"] = CUSTOM_7DAY_TEMPLATE

        if 'muscle_tiers' in data:
            # Convert tiers to preference coefficients
            muscle_preferences = {}
            for muscle, tier in data['muscle_tiers'].items():
                coefficient = TIER_COEFFICIENTS.get(int(tier), 0.9)
                muscle_preferences[muscle] = coefficient

            selector.MUSCLE_PREFERENCES = muscle_preferences

        if 'excluded_exercises' in data:
            selector.EXCLUDED_EXERCISES = set(data['excluded_exercises'])

        # Generate the workout plan
        plan = selector.generate_weekly_plan()

        # Return success response
        return jsonify({
            "success": True,
            "plan": plan,
            "config": {
                "training_days": selector.TRAINING_DAYS,
                "muscle_preferences": selector.MUSCLE_PREFERENCES
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/exercise/<int:exercise_id>')
def get_exercise_details(exercise_id):
    try:
        selector = HybridSelector()

        # Find the exercise by ID
        for exercise in selector.exercises:
            if exercise['pk'] == exercise_id:
                return jsonify(exercise)

        return jsonify({"error": "Exercise not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/exercises/count')
def get_exercise_count():
    try:
        selector = HybridSelector()
        # Count actual exercises (the strength.json file has 334 exercises based on your data)
        return jsonify({
            "total_exercises": 334,  # Updated to correct number
            "muscle_groups": ["chest", "back", "shoulder", "arm", "leg", "core"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
