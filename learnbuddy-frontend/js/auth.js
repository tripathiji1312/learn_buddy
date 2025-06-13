document.addEventListener('DOMContentLoaded', () => {
    const loginView = document.getElementById('login-view');
    const signupView = document.getElementById('signup-view');
    
    // Safety check to ensure we are on the auth page
    if (!loginView || !signupView) return;

    // This is the single source of truth for switching views
    const switchView = () => {
        if (window.location.hash === '#signup') {
            // Show signup, hide login
            loginView.classList.add('hidden');
            signupView.classList.remove('hidden');
        } else {
            // Show login, hide signup (this is the default)
            loginView.classList.remove('hidden');
            signupView.classList.add('hidden');
        }
    };

    // Listen for when the user clicks a link that changes the hash (e.g., #signup)
    window.addEventListener('hashchange', switchView);
    
    // IMPORTANT: Call switchView() once on page load to set the correct initial state
    // based on the URL the user arrived with (e.g., if they came directly to learnbuddy/auth.html#signup)
    switchView();

    // --- The form submission logic is unchanged and correct ---

    // Handle Signup Form
    document.getElementById('signup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = {
            username: document.getElementById('signup-username').value,
            email: document.getElementById('signup-email').value,
            password: document.getElementById('signup-password').value,
        };

        try {
            const response = await fetch(`${API_BASE_URL}/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Signup failed');
            
            showStatus('Account created! Please log in.', false);
            window.location.hash = 'login'; // Go to login view after successful signup
        } catch (error) { showStatus(error.message, true); }
    });

    // Handle Login Form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new URLSearchParams({
            username: document.getElementById('login-username').value,
            password: document.getElementById('login-password').value,
        });

        try {
            const response = await fetch(`${API_BASE_URL}/token`, { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Login failed');
            
            localStorage.setItem('learnbuddy_token', data.access_token);
            window.location.href = 'app.html'; // Redirect to the app
        } catch (error) { showStatus(error.message, true); }
    });
});