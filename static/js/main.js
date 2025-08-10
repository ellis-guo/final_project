// Global state - use var or check if exists
if (typeof muscleTiers === 'undefined') {
    var muscleTiers = {
        chest: 3,
        back: 3,
        shoulder: 3,
        arm: 3,
        leg: 3,
        core: 3
    };
}

if (typeof currentPlan === 'undefined') {
    var currentPlan = null;
}

if (typeof isGenerating === 'undefined') {
    var isGenerating = false;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTierButtons();
});

// Initialize tier buttons
function initializeTierButtons() {
    document.querySelectorAll('.tier-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const muscle = this.dataset.muscle;
            const tier = parseInt(this.dataset.tier);
            setMuscleTier(muscle, tier);
        });
    });
}

// Set muscle tier
function setMuscleTier(muscle, tier) {
    muscleTiers[muscle] = tier;
    
    // Update UI
    document.querySelectorAll(`.tier-btn[data-muscle="${muscle}"]`).forEach(btn => {
        btn.classList.remove('active');
        if (parseInt(btn.dataset.tier) === tier) {
            btn.classList.add('active');
        }
    });
}

// Generate workout plan
async function generatePlan() {
    if (isGenerating) return;
    
    isGenerating = true;
    const button = document.getElementById('generate-btn');
    const originalText = button.innerHTML;
    button.innerHTML = 'Generating... <span class="loading"></span>';
    button.disabled = true;
    
    // Hide previous results
    document.getElementById('results-container').classList.remove('show');
    
    // Collect form data
    const formData = {
        training_days: parseInt(document.getElementById('training-days').value),
        muscle_tiers: muscleTiers
    };
    
    try {
        const response = await fetch('/api/generate_plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPlan = data.plan;
            displayPlan(data.plan);
            updateStats(data.plan);
        } else {
            alert('Failed to generate plan: ' + data.error);
        }
    } catch (error) {
        alert('Error generating plan: ' + error.message);
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
        isGenerating = false;
    }
}

// Display the generated plan
function displayPlan(plan) {
    const container = document.getElementById('plan-display');
    container.innerHTML = '';
    
    // Sort days properly
    const days = Object.keys(plan).sort((a, b) => {
        const dayA = parseInt(a.replace('Day ', ''));
        const dayB = parseInt(b.replace('Day ', ''));
        return dayA - dayB;
    });
    
    days.forEach(day => {
        const dayData = plan[day];
        
        if (!dayData.exercises || dayData.exercises.length === 0) {
            // Rest day
            const restCard = document.createElement('div');
            restCard.className = 'day-card rest-day';
            restCard.innerHTML = `
                <div class="day-header">
                    <div class="day-title">${day}: Rest Day</div>
                </div>
                <div class="rest-icon">🏖️</div>
                <div class="rest-text">Recovery and muscle growth</div>
            `;
            container.appendChild(restCard);
        } else {
            // Training day
            const dayCard = createDayCard(day, dayData);
            container.appendChild(dayCard);
        }
    });
    
    // Show results container
    document.getElementById('results-container').classList.add('show');
}

// Create a day card element
function createDayCard(day, data) {
    const card = document.createElement('div');
    card.className = 'day-card';
    
    // Create header
    const header = document.createElement('div');
    header.className = 'day-header';
    header.innerHTML = `
        <div>
            <div class="day-title">${day}</div>
            <div class="day-type">${data.type}</div>
        </div>
        <div class="score-badge">Score: ${data.total_score}</div>
    `;
    card.appendChild(header);
    
    // Create exercise list
    const exerciseList = document.createElement('div');
    exerciseList.className = 'exercise-list';
    
    data.exercises.forEach((ex, i) => {
        const exerciseItem = document.createElement('div');
        exerciseItem.className = 'exercise-item';
        exerciseItem.style.cursor = 'pointer';
        
        exerciseItem.innerHTML = `
            <div class="exercise-number">${i + 1}</div>
            <div class="exercise-info">
                <div class="exercise-name">${ex.name}</div>
                <div class="exercise-muscles">
                    ${ex.primaryMuscles.join(', ')}
                </div>
            </div>
            <div class="exercise-score">${ex.score.toFixed(1)}</div>
        `;
        
        // Add click event to toggle steps
        exerciseItem.addEventListener('click', function() {
            // First we need to fetch the full exercise data with steps
            fetch('/api/exercise/' + ex.pk)
                .then(response => response.json())
                .then(exerciseData => {
                    toggleExerciseSteps(this, exerciseData);
                })
                .catch(error => {
                    console.error('Error fetching exercise details:', error);
                    // Fallback: if API fails, use the data we have
                    if (ex.steps) {
                        toggleExerciseSteps(this, ex);
                    }
                });
        });
        
        exerciseList.appendChild(exerciseItem);
    });
    
    card.appendChild(exerciseList);
    return card;
}

// Update statistics
function updateStats(plan) {
    let totalExercises = 0;
    let totalScore = 0;
    let trainingDays = 0;
    
    Object.values(plan).forEach(day => {
        if (day.exercises && day.exercises.length > 0) {
            totalExercises += day.exercises.length;
            totalScore += day.total_score;
            trainingDays++;
        }
    });
    
    document.getElementById('stat-exercises').textContent = totalExercises;
    document.getElementById('stat-days').textContent = trainingDays;
    document.getElementById('stat-score').textContent = totalScore.toFixed(1);
}

// Reset all tiers to default (3)
function resetTiers() {
    Object.keys(muscleTiers).forEach(muscle => {
        setMuscleTier(muscle, 3);
    });
}

// Toggle exercise steps display
function toggleExerciseSteps(exerciseElement, exerciseData) {
    const existingSteps = exerciseElement.nextElementSibling;
    
    // If steps already shown, remove them
    if (existingSteps && existingSteps.classList.contains('exercise-steps')) {
        existingSteps.remove();
        return;
    }
    
    // Create and insert steps element
    const stepsDiv = document.createElement('div');
    stepsDiv.className = 'exercise-steps';
    
    const stepsHTML = `
        <div class="steps-header">📝 How to perform:</div>
        <ol class="steps-list">
            ${exerciseData.steps.map(step => `<li>${step}</li>`).join('')}
        </ol>
    `;
    
    stepsDiv.innerHTML = stepsHTML;
    exerciseElement.after(stepsDiv);
}