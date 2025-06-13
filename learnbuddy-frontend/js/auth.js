document.addEventListener('DOMContentLoaded', () => {
    const loginView = document.getElementById('login-view');
    const signupView = document.getElementById('signup-view');
    if (!loginView || !signupView) return;
    const switchView = () => {
        if (window.location.hash === '#signup') {
            loginView.classList.add('hidden'); signupView.classList.remove('hidden');
        } else {
            loginView.classList.remove('hidden'); signupView.classList.add('hidden');
        }
    };
    window.addEventListener('hashchange', switchView); switchView();
    document.getElementById('signup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = { username: document.getElementById('signup-username').value, email: document.getElementById('signup-email').value, password: document.getElementById('signup-password').value };
        try {
            const res = await fetch(`${API_BASE_URL}/signup`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
            const data = await res.json(); if (!res.ok) throw new Error(data.detail);
            showStatus('Account created! Please log in.', false); window.location.hash = 'login';
        } catch (error) { showStatus(error.message, true); }
    });
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new URLSearchParams({ username: document.getElementById('login-username').value, password: document.getElementById('login-password').value });
        try {
            const res = await fetch(`${API_BASE_URL}/token`, { method: 'POST', body: formData });
            const data = await res.json(); if (!res.ok) throw new Error(data.detail);
            localStorage.setItem('learnbuddy_token', data.access_token); window.location.href = 'app.html';
        } catch (error) { showStatus(error.message, true); }
    });
});