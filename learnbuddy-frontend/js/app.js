document.addEventListener('DOMContentLoaded', () => {
    // Auth Guard: If no token, kick the user out to the login page.
    const token = getToken();
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    // --- State & DOM Elements ---
    let currentQuestion = null;
    let lessonProgress = 0;
    
    const dashboardView = document.getElementById('dashboard-view');
    const lessonView = document.getElementById('lesson-view');
    const questionContainer = document.getElementById('question-card');
    const questionText = document.getElementById('question-text');
    const answerForm = document.getElementById('answer-form');
    const userAnswerInput = document.getElementById('user-answer');
    const progressBar = document.getElementById('progress-bar');
    const feedbackOverlay = document.getElementById('feedback-overlay');
    const feedbackIcon = feedbackOverlay.querySelector('.feedback-icon');
    const feedbackText = feedbackOverlay.querySelector('.feedback-text');
    
    // NEW: Get the difficulty indicator element
    const difficultyIndicator = document.getElementById('difficulty-indicator');

    // Trigger the intro animation for the dashboard
    document.querySelector('.mission-briefing')?.classList.add('animate-on-load');
    
    // --- Core Functions ---
    const showFeedback = (isCorrect, callback) => {
        questionContainer.classList.add(isCorrect ? 'correct' : 'incorrect');
        feedbackIcon.textContent = isCorrect ? '🎉' : '🤔';
        feedbackText.textContent = isCorrect ? 'Awesome!' : 'Good Try!';
        
        setTimeout(() => {
            questionContainer.classList.remove('correct', 'incorrect');
            if (callback) callback();
        }, 1500);
    };

    const fetchNextQuestion = async () => {
        // Reset the input for the next question
        userAnswerInput.value = '';
        userAnswerInput.disabled = false;
        
        try {
            const response = await fetch(`${API_BASE_URL}/next_question`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ lesson_id: 1 }), // Assuming lesson_id 1
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Couldn't get a new question.");

            currentQuestion = data;
            questionText.textContent = data.question_text;
            
            // NEW: Update the difficulty indicator with the level from the API
            if (difficultyIndicator) {
                difficultyIndicator.textContent = `Difficulty: ${currentQuestion.difficulty_level}`;
            }
            
        } catch (error) {
            showStatus(error.message, true);
            questionText.textContent = "Oops! Buddy couldn't find a question. Maybe try refreshing?";
        }
    };

    const submitAnswer = async (e) => {
        e.preventDefault();
        if (!currentQuestion) return;
        userAnswerInput.disabled = true; // Prevent multiple submissions

        try {
            const response = await fetch(`${API_BASE_URL}/submit_answer`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lesson_id: 1,
                    question_id: currentQuestion.question_id,
                    difficulty_answered: currentQuestion.difficulty_level,
                    user_answer: userAnswerInput.value,
                }),
            });
            const result = await response.json();
            if (!response.ok) throw new Error('Submission failed');

            lessonProgress = Math.min(100, lessonProgress + 10); // Assume 10 questions per lesson
            progressBar.style.width = `${lessonProgress}%`;
            showFeedback(result.is_correct, fetchNextQuestion); // Fetch the next question *after* feedback
            
        } catch (error) {
            showStatus(error.message, true);
            userAnswerInput.disabled = false; // Re-enable on error
        }
    };
    
    // --- Event Listeners ---
    document.getElementById('start-lesson-btn').addEventListener('click', () => {
        // FIXED: Explicitly hide the dashboard and show the lesson view
        dashboardView.classList.add('hidden');
        lessonView.classList.remove('hidden');

        lessonProgress = 0;
        progressBar.style.width = '0%';
        fetchNextQuestion();
    });

    answerForm.addEventListener('submit', submitAnswer);
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('learnbuddy_token');
        window.location.href = 'index.html';
    });
});