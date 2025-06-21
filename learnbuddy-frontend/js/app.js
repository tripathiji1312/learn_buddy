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
    const rootEl = document.documentElement;

    // Button Selections
    const nextQuestionBtn = document.getElementById('next-question-btn');
    const submitAnswerBtn = document.getElementById('submit-answer-btn');
    const backToDashboardBtn = document.getElementById('back-to-dashboard-btn');
    const skipQuestionBtn = document.getElementById('skip-question-btn');
    const continueBtn = document.getElementById('continue-btn');
    const logoutBtn = document.getElementById('logout-btn');

    // Quest & Achievement Elements
    const questTitleEl = document.getElementById('quest-title');
    const questContentEl = document.getElementById('quest-content');
    const achievementsListEl = document.getElementById('achievements-list');

    // Question View Elements
    const questionTextEl = document.getElementById('question-text');
    const userAnswerTextarea = document.getElementById('user-answer');
    const feedbackContainer = document.getElementById('answer-feedback');
    const feedbackIcon = document.getElementById('feedback-icon').querySelector('i');
    const feedbackTitle = document.getElementById('feedback-title');
    const feedbackMessage = document.getElementById('feedback-message');
    const similarityScoreEl = document.getElementById('similarity-score');
    const difficultyStarsEl = document.getElementById('difficulty-stars');
    const difficultyNumberEl = document.getElementById('difficulty-number');

    // Modals & Celebrations
    const errorModal = document.getElementById('error-modal');
    const errorModalText = document.getElementById('error-modal-text');
    const errorModalCloseBtn = document.getElementById('error-modal-close-btn');
    const errorModalConfirmBtn = document.getElementById('error-modal-confirm-btn');
    const celebrationEl = document.getElementById('celebration');
    const celebrationTitle = document.getElementById('celebration-title');
    const celebrationMessage = document.getElementById('celebration-message');

    // Accessibility Elements
    const highContrastToggle = document.getElementById('high-contrast-toggle');
    const increaseFontBtn = document.getElementById('increase-font-btn');
    const decreaseFontBtn = document.getElementById('decrease-font-btn');

    // --- Core Functions ---
    const logout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('username');
        window.location.href = 'index.html';
    };

    const apiFetch = async (endpoint, options = {}) => {
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        if (response.status === 401) {
            logout();
            return;
        }
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'An API error occurred.');
        }
        return response.status === 204 ? null : response.json();
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
    const closeErrorModal = () => errorModal.classList.add('hidden');

    const switchToView = (viewName) => {
        dashboardView.classList.toggle('active', viewName === 'dashboard');
        questionView.classList.toggle('active', viewName === 'question');
    };

    const showCelebration = (title, message) => {
        celebrationTitle.textContent = title;
        celebrationMessage.innerHTML = message;
        celebrationEl.classList.remove('hidden');
        setTimeout(() => celebrationEl.classList.add('hidden'), 2500);
    };

    // --- UI Update Functions ---
    // NEW, CORRECTED AND ROBUST VERSION
    // NEW AND CORRECTED VERSION
    const displayDifficulty = (level) => {
        // THE FIX: Convert the 'level' to a number immediately.
        const numericLevel = parseInt(level, 10);

        difficultyNumberEl.textContent = `Lvl ${numericLevel}`;
        difficultyStarsEl.innerHTML = '';

        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('i');
            star.className = 'fas fa-star';

            // Now the comparison is between two numbers (e.g., 1 <= 1)
            if (i <= numericLevel) {
                star.classList.add('filled');
            }

            difficultyStarsEl.appendChild(star);
        }
    };

    const updateAchievementsUI = (achievements) => {
        if (achievements.length === 0) {
            achievementsListEl.innerHTML = `<div class="achievement-placeholder"><i class="fas fa-trophy"></i><p>Answer questions correctly to unlock achievements!</p></div>`;
            return;
        }
        achievementsListEl.innerHTML = '';
        achievements.forEach(ach => {
            const item = document.createElement('div');
            item.className = 'achievement-item';
            item.innerHTML = `<div class="achievement-icon"><i class="${ach.icon_class}"></i></div><div class="achievement-details"><h4>${ach.name}</h4><p>${ach.description}</p></div>`;
            achievementsListEl.appendChild(item);
        });
    };

    // --- Main Application Logic ---
    const getNextQuestion = async () => {
        showLoading('Preparing your personalized question...');
        try {
            const data = await apiFetch('/next_question', {
                method: 'POST',
                body: JSON.stringify({
                    lesson_id: lessonId
                })
            });
            currentQuestion = data;
            displayDifficulty(data.difficulty_level);
            questionTextEl.textContent = data.question_text;
            userAnswerTextarea.value = '';
            submitAnswerBtn.disabled = false;
            feedbackContainer.classList.add('hidden');
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

            feedbackContainer.classList.remove('hidden', 'correct', 'incorrect');
            feedbackIcon.className = result.is_correct ? 'fas fa-check-circle' : 'fas fa-times-circle';
            feedbackContainer.classList.add(result.is_correct ? 'correct' : 'incorrect');
            feedbackTitle.textContent = result.is_correct ? 'Great job!' : 'Not quite';
            feedbackMessage.textContent = result.is_correct ? "That's the right idea!" : "That wasn't the answer we were looking for, but keep trying!";
            similarityScoreEl.textContent = `${Math.round(result.similarity_score * 100)}%`;

            if (result.is_correct) showCelebration('Correct!', `You earned +10 XP!`);
            if (result.quest_completed) setTimeout(() => showCelebration('Quest Complete!', `Awesome work!`), 1000);

            // THE FIX: Do NOT call loadInitialData() here. It causes a race condition.
            // Data will be reloaded when the user returns to the dashboard.

        } catch (error) {
            showError(error.message);
            submitAnswerBtn.disabled = false;
        } finally {
            hideLoading();
        }
    };

    const loadInitialData = async () => {
        try {
            const [stats, quest, achievements] = await Promise.all([
                apiFetch('/users/me/stats'),
                apiFetch('/quests/today'),
                apiFetch('/achievements')
            ]);

            usernameDisplay.textContent = username;
            xpCountEl.textContent = stats.xp;
            streakCountEl.textContent = stats.streak_count;

            questTitleEl.textContent = quest.title;
            if (quest.is_completed) {
                questContentEl.innerHTML = `<div class="quest-placeholder"><i class="fas fa-check-circle" style="color: var(--success-color);"></i><h4>Quest Complete!</h4><p>You've earned your daily bonus! Feel free to keep practicing.</p></div>`;
                nextQuestionBtn.disabled = false;
                nextQuestionBtn.textContent = 'Practice More';
            } else {
                const progressPercent = (quest.current_progress / quest.completion_target) * 100;
                questContentEl.innerHTML = `<p class="quest-description">${quest.description}</p><div class="progress-bar-container"><div class="progress-bar" style="width: ${progressPercent}%"></div></div><p class="quest-progress">${quest.current_progress} / ${quest.completion_target}</p>`;
                nextQuestionBtn.disabled = false;
                nextQuestionBtn.textContent = 'Continue Quest';
            }

            updateAchievementsUI(achievements);
        } catch (error) {
            showError(`Failed to load dashboard data: ${error.message}`);
        }
    };

    // --- Accessibility Logic ---
    const accessibilityToggleBtn = document.getElementById('accessibility-fab-toggle');
    const accessibilityPopup = document.getElementById('accessibility-options-popup');

    accessibilityToggleBtn.addEventListener('click', () => {
        accessibilityPopup.classList.toggle('hidden');
        const expanded = accessibilityToggleBtn.getAttribute('aria-expanded') === 'true';
        accessibilityToggleBtn.setAttribute('aria-expanded', !expanded);
    });

    const applyAccessibilitySettings = () => {
        const isHighContrast = localStorage.getItem('highContrast') === 'true';
        highContrastToggle.checked = isHighContrast;
        document.body.classList.toggle('high-contrast', isHighContrast);
        const savedFontSize = localStorage.getItem('fontSize');
        if (savedFontSize) rootEl.style.fontSize = savedFontSize;
    };

    const changeFontSize = (amount) => {
        const currentSize = parseFloat(getComputedStyle(rootEl).fontSize);
        const newSize = currentSize + amount;
        if (newSize >= 12 && newSize <= 24) {
            const newSizePx = `${newSize}px`;
            rootEl.style.fontSize = newSizePx;
            localStorage.setItem('fontSize', newSizePx);
        }
    };

    // --- Initial Setup & Event Listeners ---
    if (!token || !username) {
        window.location.href = 'auth.html';
        return;
    }

    logoutBtn.addEventListener('click', logout);
    nextQuestionBtn.addEventListener('click', getNextQuestion);
    submitAnswerBtn.addEventListener('click', submitAnswer);
    skipQuestionBtn.addEventListener('click', getNextQuestion);
    backToDashboardBtn.addEventListener('click', () => {
        loadInitialData();
        switchToView('dashboard');
    });
    continueBtn.addEventListener('click', () => {
        feedbackContainer.classList.add('hidden');
        getNextQuestion();
    });
    errorModalCloseBtn.addEventListener('click', closeErrorModal);
    errorModalConfirmBtn.addEventListener('click', closeErrorModal);

    highContrastToggle.addEventListener('change', () => {
        localStorage.setItem('highContrast', highContrastToggle.checked);
        document.body.classList.toggle('high-contrast', highContrastToggle.checked);
    });
    increaseFontBtn.addEventListener('click', () => changeFontSize(2));
    decreaseFontBtn.addEventListener('click', () => changeFontSize(-2));

    // --- Initial Load ---
    applyAccessibilitySettings();
    loadInitialData();
});

const loadUserProfile = async () => {
    try {
        const response = await fetch('http://127.0.0.1:8000/users/me', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            }
        });

        if (!response.ok) throw new Error("Unable to fetch profile");

        const data = await response.json();
        document.getElementById('profile-username').textContent = data.username;
        document.getElementById('profile-email').textContent = data.email;
        document.getElementById('account-username').textContent = data.username;
        document.getElementById('account-email').textContent = data.email;
    } catch (err) {
        console.error("Profile loading failed", err);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
});

document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("accessToken");

    fetch("http://localhost:8000/users/me/stats", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        })
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            document.getElementById("xp-value").textContent = data.xp;
            document.getElementById("streak-value").textContent = data.streak_count;
            const formattedDate = new Date(data.last_login_date).toLocaleString();
            document.getElementById("last-login").textContent = formattedDate;
        })
        .catch(error => {
            console.error("Error fetching profile stats:", error);
        });
});