const API_BASE_URL = 'https://tripathiji1312-learnbuddy-app.hf.space';
function getToken() { return localStorage.getItem('learnbuddy_token'); }
function showStatus(message, isError = false) {
    const el = document.getElementById('status-notification') || document.createElement('div');
    if (!el.id) {
        el.id = 'status-notification';
        document.body.appendChild(el);
    }
    el.textContent = message;
    el.className = 'status-notification';
    el.classList.add(isError ? 'status-error' : 'status-success');
    setTimeout(() => el.classList.add('show'), 10);
    setTimeout(() => {
        el.classList.remove('show');
        if(el.parentElement === document.body) setTimeout(() => document.body.removeChild(el), 500);
    }, 4000);
}