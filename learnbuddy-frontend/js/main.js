const API_BASE_URL = 'http://127.0.0.1:8000';

function showStatus(message, isError = false) {
    const statusEl = document.getElementById('status-notification');
    if (!statusEl) return;

    statusEl.textContent = message;
    statusEl.className = isError ? 'status-error' : 'status-success';
    statusEl.classList.add('show');

    setTimeout(() => {
        statusEl.classList.remove('show');
    }, 4000);
}

function getToken() { return localStorage.getItem('learnbuddy_token'); }