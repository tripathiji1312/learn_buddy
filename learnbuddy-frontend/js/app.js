document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration & State ---
    const API_BASE_URL = 'http://127.0.0.1:8000';
    const token = localStorage.getItem('accessToken');
    const username = localStorage.getItem('username');
    let currentQuestion = null;
    let lessonId = 1;

    // --- Element Selections ---
    const usernameDisplay = document.getElementById('username-display');
    const xpCountEl = document.getElementById('xp-count');
    const streakCountEl = document.getElementById('streak-count');
    const dashboardView = document.getElementById('dashboard-view');
    const questionView = document.getElementById('question-view');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');

    // Quest Elements
    const questTitleEl = document.getElementById('quest-title');
    const questContentEl = document.getElementById('quest-content');
    const nextQuestionBtn = document.getElementById('next-question-btn');
    
    // Question Elements
    const questionTextEl = document.getElementById('question-text');
    const userAnswerTextarea = document.getElementById('user-answer');
    const submitAnswerBtn = document.getElementById('submit-answer-btn');
    const feedbackContainer = document.getElementById('answer-feedback');
    const feedbackIcon = document.getElementById('feedback-icon').querySelector('i');
    const feedbackTitle = document.getElementById('feedback-title');
    const feedbackMessage = document.getElementById('feedback-message');
    const similarityScoreEl = document.getElementById('similarity-score');
    
    // Modals & Celebrations
    const errorModal = document.getElementById('error-modal');
    const errorModalText = document.getElementById('error-modal-text');
    const celebrationEl = document.getElementById('celebration');
    const celebrationTitle = document.getElementById('celebration-title');
    const celebrationMessage = document.getElementById('celebration-message');

    // --- Initial Check ---
    if (!token || !username) {
        window.location.href = 'auth.html';
        return;
    }
    usernameDisplay.textContent = username;

    // --- Core Functions ---
    const apiFetch = async (endpoint, options = {}) => {
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) {
            logout();
            return;
        }
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'An API error occurred.');
        }
        // Handle responses with no content (like DELETE)
        return response.status === 204 ? null : response.json();
    };
    
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
    
    const submitAnswer = async () => {
        const userAnswer = userAnswerTextarea.value.trim();
        if (!userAnswer || !currentQuestion) return;

        showLoading('Analyzing your answer...');
        submitAnswerBtn.disabled = true;

        try {
            const result = await apiFetch('/submit_answer', {
                method: 'POST',
                body: JSON.stringify({
                    lesson_id: lessonId,
                    question_id: currentQuestion.question_id,
                    difficulty_answered: currentQuestion.difficulty_level,
                    user_answer: userAnswer,
                })
            });
            displayFeedback(result);

            if (result.is_correct) {
                const xpGain = result.quest_completed ? 10 + ' (+Quest Bonus!)' : '+10';
                showCelebration('Correct!', `You earned ${xpGain} XP!`);
            }
            if(result.quest_completed) {
                // Give a bigger celebration for completing a quest
                setTimeout(() => showCelebration('Quest Complete!', `Awesome work!`), 1000);
            }
            // Refresh stats and quest info after every answer
            loadInitialData();
        } catch (error) {
            showError(error.message);
            submitAnswerBtn.disabled = false;
        } finally {
            hideLoading();
        }
    };

    // --- UI Update Functions ---
    const switchToView = (viewName) => {
        dashboardView.classList.toggle('active', viewName === 'dashboard');
        questionView.classList.toggle('active', viewName === 'question');
    };

    const displayQuestion = (questionData) => {
        questionTextEl.textContent = questionData.question_text;
        userAnswerTextarea.value = '';
        submitAnswerBtn.disabled = false;
        feedbackContainer.classList.add('hidden');
    };

    const displayFeedback = (result) => {
        feedbackContainer.classList.remove('hidden', 'correct', 'incorrect');
        feedbackIcon.className = result.is_correct ? 'fas fa-check-circle' : 'fas fa-times-circle';
        feedbackContainer.classList.add(result.is_correct ? 'correct' : 'incorrect');
        feedbackTitle.textContent = result.is_correct ? 'Great job!' : 'Not quite';
        feedbackMessage.textContent = result.is_correct ? "That's the right idea!" : "That wasn't the answer we were looking for, but keep trying!";
        similarityScoreEl.textContent = `${Math.round(result.similarity_score * 100)}%`;
    };

    const updateStatsUI = (stats) => {
        xpCountEl.textContent = stats.xp;
        streakCountEl.textContent = stats.streak_count;
    };

    const updateQuestUI = (quest) => {
        questTitleEl.textContent = quest.title;
        if (quest.is_completed) {
            questContentEl.innerHTML = `
                <div class="quest-placeholder">
                    <i class="fas fa-check-circle" style="color: var(--success-color);"></i>
                    <h4>Quest Complete!</h4>
                    <p>Great job! Come back tomorrow for a new quest.</p>
                </div>`;
            nextQuestionBtn.disabled = true;
            nextQuestionBtn.textContent = 'Quest Done for Today';
        } else {
            const progressPercent = (quest.current_progress / quest.completion_target) * 100;
            questContentEl.innerHTML = `
                <p class="quest-description">${quest.description}</p>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${progressPercent}%"></div>
                </div>
                <p class="quest-progress">${quest.current_progress} / ${quest.completion_target}</p>
            `;
            nextQuestionBtn.disabled = false;
        }
    };

    const showLoading = (message) => {
        loadingText.textContent = message;
        loadingOverlay.classList.remove('hidden');
    };

    const hideLoading = () => loadingOverlay.classList.add('hidden');

    const showError = (message) => {
        errorModalText.textContent = message;
        errorModal.classList.remove('hidden');
    };

    const showCelebration = (title, message) => {
        celebrationTitle.textContent = title;
        celebrationMessage.innerHTML = message;
        celebrationEl.classList.remove('hidden');
        setTimeout(() => celebrationEl.classList.add('hidden'), 2500);
    };

    // --- Global Functions & Initial Load ---
    window.closeErrorModal = () => errorModal.classList.add('hidden');
    window.getNextQuestion = getNextQuestion;
    window.submitAnswer = submitAnswer;
    window.continueToNext = () => {
        feedbackContainer.classList.add('hidden');
        getNextQuestion();
    };
    window.skipQuestion = getNextQuestion;
    window.backToDashboard = () => {
        loadInitialData(); // Refresh data when coming back to dashboard
        switchToView('dashboard');
    };
    window.logout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('username');
        window.location.href = 'index.html';
    };

    const loadInitialData = async () => {
        try {
            const [stats, quest] = await Promise.all([
                apiFetch('/users/me/stats'),
                apiFetch('/quests/today')
            ]);
            updateStatsUI(stats);
            updateQuestUI(quest);
        } catch (error) {
            showError(`Failed to load dashboard data: ${error.message}`);
        }
    };

    // Load all data when the page loads
    loadInitialData();
});