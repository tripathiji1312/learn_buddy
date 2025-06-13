document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8000'; // Your backend URL
    const loginForm = document.getElementById('admin-login-form');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessageContainer = document.getElementById('error-message');
    const errorTextSpan = document.getElementById('error-text');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorMessageContainer.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');

        const formData = new FormData(loginForm);
        const urlEncodedData = new URLSearchParams(formData);

        try {
            // Note: We are using a new, proposed endpoint for admin auth
            const response = await fetch(`${API_BASE_URL}/admin/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: urlEncodedData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Authentication failed.');
            }

            // Use a different key for the admin token to avoid conflicts
            localStorage.setItem('adminAccessToken', data.access_token);
            window.location.href = 'admin.html';

        } catch (error) {
            errorTextSpan.textContent = error.message;
            errorMessageContainer.classList.remove('hidden');
        } finally {
            loadingSpinner.classList.add('hidden');
        }
    });
});