document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration ---
    const API_BASE_URL = 'http://127.0.0.1:8000'; // Replace with your actual backend URL

    // --- Element Selections ---
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const switchBtn = document.getElementById('switch-btn');
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    const switchText = document.getElementById('switch-text');

    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessageContainer = document.getElementById('error-message');
    const errorTextSpan = document.getElementById('error-text');
    const successMessageContainer = document.getElementById('success-message');
    const successTextSpan = document.getElementById('success-text');

    let isLoginMode = true;

    // --- Functions ---

    /**
     * Toggles the visibility of a password field.
     * @param {string} fieldId - The ID of the password input field.
     * @param {HTMLElement} toggleButton - The button element that triggers the toggle.
     */
    window.togglePassword = (fieldId, toggleButton) => {
        const passwordField = document.getElementById(fieldId);
        const icon = toggleButton.querySelector('i');
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            passwordField.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    };

    /**
     * Switches the view between the login and signup forms.
     */
    window.switchAuthMode = () => {
        isLoginMode = !isLoginMode;
        hideMessages(); // Hide any existing messages

        if (isLoginMode) {
            loginForm.classList.remove('hidden');
            signupForm.classList.add('hidden');
            authTitle.textContent = 'Welcome Back';
            authSubtitle.textContent = 'Sign in to continue your learning journey';
            switchText.textContent = "Don't have an account?";
            switchBtn.textContent = 'Sign up';
        } else {
            loginForm.classList.add('hidden');
            signupForm.classList.remove('hidden');
            authTitle.textContent = 'Create Your Account';
            authSubtitle.textContent = 'Start your personalized learning adventure today';
            switchText.textContent = 'Already have an account?';
            switchBtn.textContent = 'Sign in';
        }
    };

    /**
     * Displays a loading state.
     * @param {boolean} isLoading - Whether to show or hide the loader.
     */
    const showLoading = (isLoading) => {
        loadingSpinner.classList.toggle('hidden', !isLoading);
    };
    
    /**
     * Hides all feedback messages.
     */
    const hideMessages = () => {
        errorMessageContainer.classList.add('hidden');
        successMessageContainer.classList.add('hidden');
    };

    /**
     * Displays an error message.
     * @param {string} message - The error message to display.
     */
    const showError = (message) => {
        hideMessages();
        errorTextSpan.textContent = message;
        errorMessageContainer.classList.remove('hidden');
    };

    /**
     * Displays a success message.
     * @param {string} message - The success message to display.
     */
    const showSuccess = (message) => {
        hideMessages();
        successTextSpan.textContent = message;
        successMessageContainer.classList.remove('hidden');
    };


    /**
     * Handles the signup form submission.
     * @param {Event} e - The form submission event.
     */
    const handleSignup = async (e) => {
        e.preventDefault();
        hideMessages();
        showLoading(true);

        const formData = new FormData(signupForm);
        const userData = Object.fromEntries(formData.entries());

        try {
            const response = await fetch(`${API_BASE_URL}/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An unknown error occurred.');
            }

            showSuccess(`Account for ${data.username} created! Please log in.`);
            // Automatically switch to login mode after successful signup
            setTimeout(switchAuthMode, 1500);

        } catch (error) {
            showError(error.message);
        } finally {
            showLoading(false);
        }
    };

    /**
     * Handles the login form submission.
     * @param {Event} e - The form submission event.
     */
    const handleLogin = async (e) => {
        e.preventDefault();
        hideMessages();
        showLoading(true);

        const formData = new FormData(loginForm);
        // The /token endpoint expects 'x-www-form-urlencoded' data.
        const urlEncodedData = new URLSearchParams(formData);

        try {
            const response = await fetch(`${API_BASE_URL}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: urlEncodedData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Incorrect username or password.');
            }
            
            // Store the token and redirect
            localStorage.setItem('accessToken', data.access_token);
            // Also store username for easy access in the app
            const username = new FormData(loginForm).get('username');
            localStorage.setItem('username', username);

            window.location.href = 'app.html';

        } catch (error) {
            showError(error.message);
        } finally {
            showLoading(false);
        }
    };

    // --- Event Listeners ---
    signupForm.addEventListener('submit', handleSignup);
    loginForm.addEventListener('submit', handleLogin);
});