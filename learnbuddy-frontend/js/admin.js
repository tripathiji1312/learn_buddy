document.addEventListener('DOMContentLoaded', () => {
    // --- Config & State ---
    const API_BASE_URL = 'http://127.0.0.1:8000';
    const token = localStorage.getItem('adminAccessToken');
    let currentView = 'dashboard';
    let difficultyChart = null;

    // --- Element Selectors ---
    const loadingOverlay = document.getElementById('loading-overlay');
    const adminViews = document.querySelectorAll('.admin-view');
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
    const logoutBtn = document.getElementById('admin-logout-btn');

    // Dashboard Elements
    const statsTotalUsers = document.getElementById('stats-total-users');
    const statsTotalQuestions = document.getElementById('stats-total-questions');
    const statsAnswers = document.getElementById('stats-answers');

    // Users Elements
    const usersTableBody = document.getElementById('users-table-body');
    const addUserBtn = document.getElementById('add-user-btn');
    const userModal = document.getElementById('user-modal');
    const userModalCloseBtn = document.getElementById('user-modal-close-btn');
    const userForm = document.getElementById('user-form');
    const userModalTitle = document.getElementById('user-modal-title');
    const userIdInput = document.getElementById('user-id-input');
    const userUsernameInput = document.getElementById('user-username-input');
    const userEmailInput = document.getElementById('user-email-input');
    const userPasswordInput = document.getElementById('user-password-input');
    const userXpInput = document.getElementById('user-xp-input');
    const userIsAdminInput = document.getElementById('user-is-admin-input');

    // Questions Elements
    const questionsTableBody = document.getElementById('questions-table-body');
    const addQuestionBtn = document.getElementById('add-question-btn');
    const questionModal = document.getElementById('question-modal');
    const questionModalCloseBtn = document.getElementById('question-modal-close-btn');
    const questionForm = document.getElementById('question-form');
    const questionModalTitle = document.getElementById('question-modal-title');
    const questionIdInput = document.getElementById('question-id-input');
    const questionTextInput = document.getElementById('question-text-input');
    const correctAnswerInput = document.getElementById('correct-answer-input');
    const questionDifficultyInput = document.getElementById('question-difficulty-input');
    const lessonIdInput = document.getElementById('lesson-id-input');

    // --- Initial Check ---
    if (!token) {
        window.location.href = 'admin-login.html';
        return;
    }

    // --- Helper Functions ---
    const showLoading = (show) => loadingOverlay.classList.toggle('hidden', !show);

    const apiFetch = async (endpoint, options = {}) => {
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers,
            ...options
        });

        if (response.status === 401) {
            logout();
            return;
        }
        if (response.status === 204) {
            return null;
        } // Handle 204 No Content for DELETE

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'An API error occurred.');
        }
        return data;
    };

    const logout = () => {
        localStorage.removeItem('adminAccessToken');
        window.location.href = 'admin-login.html';
    };

    // --- View Switching ---
    const switchView = (view) => {
        currentView = view;
        adminViews.forEach(v => v.classList.remove('active'));
        document.getElementById(`${view}-view`).classList.add('active');
        navItems.forEach(n => n.classList.remove('active'));
        document.querySelector(`.nav-item[data-view="${view}"]`).classList.add('active');
        loadDataForView(view);
    };

    const loadDataForView = (view) => {
        switch (view) {
            case 'dashboard':
                loadDashboardData();
                break;
            case 'users':
                loadUsers();
                break;
            case 'questions':
                loadQuestions();
                break;
        }
    };

    // --- Data Loading & Rendering ---
    const loadDashboardData = async () => {
        showLoading(true);
        try {
            const data = await apiFetch('/admin/stats');
            statsTotalUsers.textContent = data.total_users;
            statsTotalQuestions.textContent = data.total_questions;
            statsAnswers.textContent = data.total_answers_submitted;
            renderDifficultyChart(data.questions_by_difficulty);
        } catch (error) {
            alert(`Error loading dashboard: ${error.message}`);
        } finally {
            showLoading(false);
        }
    };

    const renderDifficultyChart = (data) => {
        const ctx = document.getElementById('difficulty-chart').getContext('2d');
        if (difficultyChart) difficultyChart.destroy();
        difficultyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(data).map(l => `Level ${l}`),
                datasets: [{
                    label: '# of Questions',
                    data: Object.values(data),
                    backgroundColor: 'rgba(102, 126, 234, 0.5)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    };

    const loadUsers = async () => {
        showLoading(true);
        usersTableBody.innerHTML = '<tr><td colspan="6">Loading...</td></tr>';
        try {
            const users = await apiFetch('/admin/users');
            usersTableBody.innerHTML = '';
            if (!users || users.length === 0) {
                usersTableBody.innerHTML = '<tr><td colspan="6">No users found.</td></tr>';
                return;
            }
            users.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>${user.xp}</td>
                    <td><span class="role-badge ${user.is_admin ? 'admin' : ''}">${user.is_admin ? 'Admin' : 'User'}</span></td>
                    <td>
                        <button class="btn-edit" data-id="${user.id}" title="Edit User"><i class="fas fa-edit"></i></button>
                        <button class="btn-delete" data-id="${user.id}" data-username="${user.username}" title="Delete User"><i class="fas fa-trash-alt"></i></button>
                    </td>
                `;
                usersTableBody.appendChild(row);
            });
        } catch (error) {
            usersTableBody.innerHTML = `<tr><td colspan="6" class="error-text">Error loading users: ${error.message}</td></tr>`;
        } finally {
            showLoading(false);
        }
    };

    const loadQuestions = async () => {
        showLoading(true);
        questionsTableBody.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';
        try {
            const questions = await apiFetch('/admin/questions');
            questionsTableBody.innerHTML = '';
            if (!questions || questions.length === 0) {
                questionsTableBody.innerHTML = '<tr><td colspan="5">No questions found.</td></tr>';
                return;
            }
            questions.forEach(q => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${q.id}</td>
                    <td class="question-text-cell">${q.question_text}</td>
                    <td>${q.difficulty_level}</td>
                    <td>${q.lesson_id}</td>
                    <td>
                        <button class="btn-edit" data-id="${q.id}" title="Edit Question"><i class="fas fa-edit"></i></button>
                        <button class="btn-delete" data-id="${q.id}" title="Delete Question"><i class="fas fa-trash-alt"></i></button>
                    </td>
                `;
                questionsTableBody.appendChild(row);
            });
        } catch (error) {
            questionsTableBody.innerHTML = `<tr><td colspan="5" class="error-text">Error loading questions: ${error.message}</td></tr>`;
        } finally {
            showLoading(false);
        }
    };

    // --- Modal & Form Handling ---

    // User Modal Logic
    const openUserModal = (user = null) => {
        userForm.reset();
        userPasswordInput.placeholder = "Leave blank to keep unchanged";
        userPasswordInput.required = false;

        if (user) {
            userModalTitle.textContent = 'Edit User';
            userIdInput.value = user.id;
            userUsernameInput.value = user.username;
            userEmailInput.value = user.email;
            userXpInput.value = user.xp;
            userIsAdminInput.checked = user.is_admin;
        } else {
            userModalTitle.textContent = 'Add New User';
            userIdInput.value = '';
            userPasswordInput.placeholder = "Enter new password (required)";
            userPasswordInput.required = true;
        }
        userModal.classList.remove('hidden');
    };
    const closeUserModal = () => userModal.classList.add('hidden');

    // Question Modal Logic
    const openQuestionModal = () => {
        questionForm.reset();
        questionModalTitle.textContent = 'Add New Question';
        questionIdInput.value = '';
        questionModal.classList.remove('hidden');
    };
    const closeQuestionModal = () => questionModal.classList.add('hidden');

    // --- Event Listeners ---
    navItems.forEach(item => {
        if (!item.id?.includes('logout')) {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                switchView(item.dataset.view);
            });
        }
    });

    logoutBtn.addEventListener('click', logout);

    // Modal Open/Close Listeners
    addUserBtn.addEventListener('click', () => openUserModal());
    userModalCloseBtn.addEventListener('click', closeUserModal);
    addQuestionBtn.addEventListener('click', () => openQuestionModal());
    questionModalCloseBtn.addEventListener('click', closeQuestionModal);

    // Form Submission Handlers
    userForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        showLoading(true);
        const id = userIdInput.value;
        const isEditing = !!id;
        const payload = {
            username: userUsernameInput.value,
            email: userEmailInput.value,
            xp: parseInt(userXpInput.value, 10),
            is_admin: userIsAdminInput.checked,
        };
        if (!isEditing || (isEditing && userPasswordInput.value)) {
            payload.password = userPasswordInput.value;
        }
        const endpoint = isEditing ? `/admin/users/${id}` : '/admin/users';
        const method = isEditing ? 'PUT' : 'POST';
        try {
            await apiFetch(endpoint, {
                method,
                body: JSON.stringify(payload)
            });
            closeUserModal();
            loadUsers();
        } catch (error) {
            alert(`Error saving user: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    questionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        showLoading(true);
        const id = questionIdInput.value;
        const isEditing = !!id;
        const payload = {
            question_text: questionTextInput.value,
            correct_answer_text: correctAnswerInput.value,
            difficulty_level: parseInt(questionDifficultyInput.value, 10),
            lesson_id: parseInt(lessonIdInput.value, 10),
        };
        const endpoint = isEditing ? `/admin/questions/${id}` : '/admin/questions';
        const method = isEditing ? 'PUT' : 'POST';
        try {
            await apiFetch(endpoint, {
                method,
                body: JSON.stringify(payload)
            });
            closeQuestionModal();
            loadQuestions();
        } catch (error) {
            alert(`Error saving question: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // Main Event Delegation for Edit/Delete Buttons
    document.body.addEventListener('click', async (e) => {
        const editButton = e.target.closest('.btn-edit');
        const deleteButton = e.target.closest('.btn-delete');
        if (!editButton && !deleteButton) return;

        const id = (editButton || deleteButton).dataset.id;
        showLoading(true);
        try {
            if (editButton) {
                if (currentView === 'users') {
                    const user = await apiFetch(`/admin/users/${id}`);
                    openUserModal(user);
                } else {
                    alert("To edit a question, its correct answer is needed. A new GET /admin/questions/{id} endpoint would be required to implement this safely.");
                }
            } else if (deleteButton) {
                let confirmMsg = `Are you sure you want to delete this item (ID: ${id})?`;
                if (currentView === 'users') {
                    confirmMsg = `Are you sure you want to delete user "${deleteButton.dataset.username}" (ID: ${id})? This action cannot be undone.`;
                }
                if (confirm(confirmMsg)) {
                    const endpoint = currentView === 'users' ? `/admin/users/${id}` : `/admin/questions/${id}`;
                    await apiFetch(endpoint, {
                        method: 'DELETE'
                    });
                    loadDataForView(currentView);
                }
            }
        } catch (error) {
            alert(`Operation failed: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // --- Initial Load ---
    // --- Initial Load ---
    switchView('dashboard');

});