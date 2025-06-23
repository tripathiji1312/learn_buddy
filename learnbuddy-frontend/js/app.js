document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration & State ---
    const API_BASE_URL = 'https://tripathiji1312-learnbuddy-app.hf.space';
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
    // FIX: Add selectors for the new difficulty display elements
    const difficultyNumberEl = document.getElementById('difficulty-number');
    const difficultyStarsEl = document.getElementById('difficulty-stars');

    // Modals & Celebrations
    const errorModal = document.getElementById('error-modal');
    const errorModalText = document.getElementById('error-modal-text');
    const errorModalCloseBtn = document.getElementById('error-modal-close-btn');
    const errorModalConfirmBtn = document.getElementById('error-modal-confirm-btn');
    const celebrationEl = document.getElementById('celebration');
    const celebrationTitle = document.getElementById('celebration-title');
    const celebrationMessage = document.getElementById('celebration-message');

    // Accessibility Elements

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
    // FIX: This function now populates the new difficulty elements in the question card
    const displayDifficulty = (level) => {
        const numericLevel = parseInt(level, 10);
        if (isNaN(numericLevel)) return;

        if (difficultyNumberEl) {
            difficultyNumberEl.textContent = `Lvl ${numericLevel}`;
        }
        if (difficultyStarsEl) {
            difficultyStarsEl.innerHTML = ''; // Clear existing stars
            for (let i = 1; i <= 5; i++) {
                const star = document.createElement('i');
                star.className = 'fas fa-star';
                if (i <= numericLevel) {
                    star.classList.add('filled');
                }
                difficultyStarsEl.appendChild(star);
            }
        }
    };

    const updateAchievementsUI = (achievements) => {
        if (!achievementsListEl) return;
        if (achievements.length === 0) {
            achievementsListEl.innerHTML = `<div class="achievement-placeholder"><i class="fas fa-trophy"></i><p>Answer questions to unlock achievements!</p></div>`;
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
            displayDifficulty(data.difficulty_level); // This will now update the new elements
            questionTextEl.textContent = data.question_text;
            userAnswerTextarea.value = '';
            submitAnswerBtn.disabled = false;
            feedbackContainer.classList.add('hidden');
            // FIX: This is the core of the view switching logic
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
            feedbackMessage.textContent = result.is_correct ? "That's the right idea!" : "That wasn't the answer we were looking for.";
            similarityScoreEl.textContent = `${Math.round(result.similarity_score * 100)}%`;

            if (result.is_correct) showCelebration('Correct!', `You earned +10 XP!`);
            if (result.quest_completed) setTimeout(() => showCelebration('Quest Complete!', `Awesome work!`), 1000);

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

            if (usernameDisplay) usernameDisplay.textContent = username;
            if (xpCountEl) xpCountEl.textContent = stats.xp;
            if (streakCountEl) streakCountEl.textContent = stats.streak_count;

            if (questTitleEl) questTitleEl.textContent = quest.title;
            if (questContentEl) {
                if (quest.is_completed) {
                    questContentEl.innerHTML = `<div class="quest-placeholder"><i class="fas fa-check-circle" style="color: var(--success-color);"></i><h4>Quest Complete!</h4><p>Great job today. Feel free to practice more.</p></div>`;
                    if (nextQuestionBtn) {
                        nextQuestionBtn.disabled = false;
                        nextQuestionBtn.textContent = 'Practice More';
                    }
                } else {
                    const progressPercent = (quest.current_progress / quest.completion_target) * 100;
                    questContentEl.innerHTML = `<p class="quest-description">${quest.description}</p><div class="progress-bar-container"><div class="progress-bar" style="width: ${progressPercent}%"></div></div><p class="quest-progress">${quest.current_progress} / ${quest.completion_target}</p>`;
                    if (nextQuestionBtn) {
                        nextQuestionBtn.disabled = false;
                        nextQuestionBtn.textContent = 'Continue Quest';
                    }
                }
            }

            updateAchievementsUI(achievements);
        } catch (error) {
            showError(`Failed to load dashboard data: ${error.message}`);
        }
    };

    // --- Accessibility Logic ---
    const accessibilityToggleBtn = document.getElementById('accessibility-fab-toggle');
    const accessibilityPopup = document.getElementById('accessibility-options-popup');
    if (accessibilityToggleBtn) {
        accessibilityToggleBtn.addEventListener('click', () => {
            accessibilityPopup.classList.toggle('hidden');
            accessibilityToggleBtn.setAttribute('aria-expanded', !accessibilityToggleBtn.getAttribute('aria-expanded'));
        });
    }
    const applyAccessibilitySettings = () => {
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

    if (logoutBtn) logoutBtn.addEventListener('click', logout);
    if (nextQuestionBtn) nextQuestionBtn.addEventListener('click', getNextQuestion);
    if (submitAnswerBtn) submitAnswerBtn.addEventListener('click', submitAnswer);
    if (skipQuestionBtn) skipQuestionBtn.addEventListener('click', getNextQuestion);
    if (backToDashboardBtn) {
        backToDashboardBtn.addEventListener('click', () => {
            loadInitialData();
            switchToView('dashboard');
        });
    }
    if (continueBtn) {
        continueBtn.addEventListener('click', () => {
            feedbackContainer.classList.add('hidden');
            getNextQuestion();
        });
    }
    if (errorModalCloseBtn) errorModalCloseBtn.addEventListener('click', closeErrorModal);
    if (errorModalConfirmBtn) errorModalConfirmBtn.addEventListener('click', closeErrorModal);

    if (increaseFontBtn) increaseFontBtn.addEventListener('click', () => changeFontSize(1));
    if (decreaseFontBtn) decreaseFontBtn.addEventListener('click', () => changeFontSize(-1));

    // --- Initial Load ---
    applyAccessibilitySettings();
    if (dashboardView && dashboardView.classList.contains('active')) {
        loadInitialData();
    }
});

const loadUserProfile = async () => {
    try {
        const response = await fetch('https://tripathiji1312-learnbuddy-app.hf.space', {
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

    fetch("https://tripathiji1312-learnbuddy-app.hf.space", {
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