// --- js/profile.js ---

document.addEventListener('DOMContentLoaded', () => {
    // Define the base URL of your deployed API
    const API_BASE_URL = 'https://tripathiji1312-learnbuddy-app.hf.space';

    // --- DOM Elements ---
    const usernameSpan = document.getElementById('profile-username');
    const emailSpan = document.getElementById('profile-email');
    const accountUsernameSpan = document.getElementById('account-username');
    const accountEmailSpan = document.getElementById('account-email');
    const lastLoginSpan = document.getElementById('last-login');
    const streakValueSpan = document.getElementById('streak-value');
    const xpValueSpan = document.getElementById('xp-value');
    const achievementsListDiv = document.querySelector('.achievements-list');
    const logoutButton = document.getElementById('logout-btn');

    /**
     * Fetches data from a protected API endpoint.
     * @param {string} endpoint The API endpoint to call (e.g., '/users/me').
     * @param {string} token The JWT authentication token.
     * @returns {Promise<any>} The JSON response from the API.
     */
    async function fetchProtectedData(endpoint, token) {
        const fullUrl = `${API_BASE_URL}${endpoint}`;
        console.log(`Fetching from: ${fullUrl}`); // Log the URL to debug

        const response = await fetch(fullUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            // If unauthorized, the token is invalid or expired. Redirect to login.
            console.error("Authorization failed (401). Redirecting to auth.html");
            window.location.href = 'auth.html';
            throw new Error('Unauthorized');
        }

        if (!response.ok) {
            console.error(`API call to ${endpoint} failed with status: ${response.status}`);
            throw new Error(`API call failed for ${endpoint}`);
        }

        return response.json();
    }

    /**
     * Main function to fetch all user data and update the UI.
     */
    async function loadProfileData() {
        const token = localStorage.getItem('learnBuddyToken');

        if (!token) {
            console.error("No authentication token found in localStorage. Redirecting to login.");
            window.location.href = 'auth.html';
            return;
        }

        try {
            // Fetch all required data concurrently for better performance
            const [profile, stats, achievements] = await Promise.all([
                fetchProtectedData('/users/me', token),
                fetchProtectedData('/users/me/stats', token),
                fetchProtectedData('/achievements', token)
            ]);

            // Update the UI with the fetched data
            updateProfileUI(profile);
            updateStatsUI(stats);
            updateAchievementsUI(achievements);

        } catch (error) {
            console.error("Failed to load and display profile data:", error);
        }
    }

    function updateProfileUI(profile) {
        if (usernameSpan) usernameSpan.textContent = profile.username;
        if (emailSpan) emailSpan.textContent = profile.email;
        if (accountUsernameSpan) accountUsernameSpan.textContent = profile.username;
        if (accountEmailSpan) accountEmailSpan.textContent = profile.email;
    }

    function updateStatsUI(stats) {
        if (xpValueSpan) xpValueSpan.textContent = stats.xp;
        if (streakValueSpan) streakValueSpan.textContent = stats.streak_count;
        if (lastLoginSpan) {
            const lastLoginDate = new Date(stats.last_login_date);
            lastLoginSpan.textContent = lastLoginDate.toLocaleDateString('en-US', {
                year: 'numeric', month: 'long', day: 'numeric'
            });
        }
    }

    function updateAchievementsUI(achievements) {
        if (!achievementsListDiv) return;
        achievementsListDiv.innerHTML = ''; // Clear placeholder badges

        if (!achievements || achievements.length === 0) {
            achievementsListDiv.innerHTML = '<p>No achievements unlocked yet. Keep learning!</p>';
            return;
        }

        achievements.forEach(ach => {
            const badge = document.createElement('span');
            badge.className = 'achievement-badge';
            badge.innerHTML = `<i class="${ach.icon_class}"></i> ${ach.name}`;
            badge.title = `${ach.description} (Unlocked on: ${new Date(ach.unlocked_at).toLocaleDateString()})`;
            achievementsListDiv.appendChild(badge);
        });
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent default link behavior
            localStorage.removeItem('learnBuddyToken');
            window.location.href = 'auth.html';
        });
    }

    // Load initial data from the backend when the page loads
    loadProfileData();
});