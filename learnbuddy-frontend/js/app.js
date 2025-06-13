document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration & State ---
    const API_BASE_URL = 'http://127.0.0.1:8000'; // Replace with your actual backend URL
    const token = localStorage.getItem('accessToken');
    const username = localStorage.getItem('username');

    let currentQuestion = null; // Will store { question_id, difficulty_level, question_text }
    let lessonId = 1; // Default lesson
    
    // --- Element Selections ---
    const usernameDisplay = document.getElementById('username-display');
    const dashboardView = document.getElementById('dashboard-view');
    const questionView = document.getElementById('question-view');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');

    const startQuestBtn = document.getElementById('start-quest-btn');
    const nextQuestionBtn = document.getElementById('next-question-btn');
    const questionContent = document.getElementById('quest-content');

    const questionTextEl = document.getElementById('question-text');
    const userAnswerTextarea = document.getElementById('user-answer');
    const submitAnswerBtn = document.getElementById('submit-answer-btn');
    
    const feedbackContainer = document.getElementById('answer-feedback');
    const feedbackIcon = document.getElementById('feedback-icon').querySelector('i');
    const feedbackTitle = document.getElementById('feedback-title');
    const feedbackMessage = document.getElementById('feedback-message');
    const similarityScoreEl = document.getElementById('similarity-score');
    
    const errorModal = document.getElementById('error-modal');
    const errorModalText = document.getElementById('error-modal-text');
    const celebrationEl = document.getElementById('celebration');

    // --- Initial Check ---
    if (!token || !username) {
        // If no token, redirect to the login page immediately.
        window.location.href = 'auth.html';
        return; // Stop further execution
    }
    
    // Personalize the UI
    usernameDisplay.textContent = username;

    // --- Core Functions ---
    
    /**
     * Performs an authenticated fetch request to the API.
     * @param {string} endpoint - The API endpoint to call.
     * @param {object} options - The options for the fetch call (method, body, etc.).
     * @returns {Promise<any>} - The JSON response from the API.
     */
    const apiFetch = async (endpoint, options = {}) => {
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };

        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

        if (response.status === 401) {
            // Token is invalid or expired
            logout();
            return;
        }

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'An API error occurred.');
        }
        return data;
    };

    /**
     * Fetches the next question from the AI.
     */
    const getNextQuestion = async () => {
        showLoading('Preparing your personalized question...');
        try {
            const data = await apiFetch('/next_question', {
                method: 'POST',
                body: JSON.stringify({ lesson_id: lessonId })
            });

            currentQuestion = data;
            displayQuestion(data);
            switchToView('question');
        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading();
        }
    };
    
    /**
     * Handles the submission of a user's answer.
     */
    const submitAnswer = async () => {
        const userAnswer = userAnswerTextarea.value.trim();
        if (!userAnswer || !currentQuestion) return;

        showLoading('Analyzing your answer...');
        submitAnswerBtn.disabled = true;

        const payload = {
            lesson_id: lessonId,
            question_id: currentQuestion.question_id,
            difficulty_answered: currentQuestion.difficulty_level,
            user_answer: userAnswer,
        };

        try {
            const result = await apiFetch('/submit_answer', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            displayFeedback(result);

            // If correct, show celebration
            if (result.is_correct) {
                showCelebration();
            }
        } catch (error) {
            showError(error.message);
            submitAnswerBtn.disabled = false;
        } finally {
            hideLoading();
        }
    };

    // --- UI Update Functions ---
    
    /**
     * Switches between the 'dashboard' and 'question' views.
     * @param {'dashboard' | 'question'} viewName - The name of the view to switch to.
     */
    const switchToView = (viewName) => {
        dashboardView.classList.remove('active');
        questionView.classList.remove('active');

        if (viewName === 'dashboard') {
            dashboardView.classList.add('active');
        } else {
            questionView.classList.add('active');
        }
    };

    const displayQuestion = (questionData) => {
        questionTextEl.textContent = questionData.question_text;
        userAnswerTextarea.value = '';
        submitAnswerBtn.disabled = false;
        feedbackContainer.classList.add('hidden');
    };

    const displayFeedback = (result) => {
        feedbackContainer.classList.remove('hidden', 'correct', 'incorrect');
        feedbackIcon.classList.remove('fa-check-circle', 'fa-times-circle');
        
        if (result.is_correct) {
            feedbackContainer.classList.add('correct');
            feedbackIcon.classList.add('fa-check-circle');
            feedbackTitle.textContent = 'Great job!';
            feedbackMessage.textContent = "That's correct! You're doing amazing.";
        } else {
            feedbackContainer.classList.add('incorrect');
            feedbackIcon.classList.add('fa-times-circle');
            feedbackTitle.textContent = 'Not quite';
            feedbackMessage.textContent = "That wasn't the answer we were looking for, but keep trying!";
        }
        
        similarityScoreEl.textContent = `${Math.round(result.similarity_score * 100)}%`;
    };
    
    const showLoading = (message) => {
        loadingText.textContent = message;
        loadingOverlay.classList.remove('hidden');
    };

    const hideLoading = () => {
        loadingOverlay.classList.add('hidden');
    };

    const showError = (message) => {
        errorModalText.textContent = message;
        errorModal.classList.remove('hidden');
    };

    window.closeErrorModal = () => {
        errorModal.classList.add('hidden');
    };
    
    const showCelebration = () => {
        celebrationEl.classList.remove('hidden');
        setTimeout(() => {
            celebrationEl.classList.add('hidden');
        }, 2000); // Animation lasts 2 seconds
    };
    
    // --- UI Event Handlers (exposed to global scope) ---
    
    window.startQuest = () => {
        startQuestBtn.classList.add('hidden');
        nextQuestionBtn.classList.remove('hidden');
        questionContent.innerHTML = `<p>Your quest is active! Click "Next Question" to begin.</p>`;
        getNextQuestion();
    };

    window.getNextQuestion = getNextQuestion;

    window.submitAnswer = submitAnswer;
    
    window.continueToNext = () => {
        feedbackContainer.classList.add('hidden');
        getNextQuestion();
    };
    
    window.skipQuestion = () => {
        // A simple skip just gets the next question
        getNextQuestion();
    };

    window.backToDashboard = () => {
        switchToView('dashboard');
    };

    window.logout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('username');
        window.location.href = 'index.html';
    };

});