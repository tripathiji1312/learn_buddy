/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

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
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            // If unauthorized, the token is invalid or expired. Redirect to login.
            window.location.href = 'auth.html';
            throw new Error('Unauthorized');
        }

        if (!response.ok) {
            throw new Error(`API call failed for ${endpoint} with status ${response.status}`);
        }

        return response.json();
    }

    /**
     * Main function to fetch all user data and update the UI.
     */
    async function loadProfileData() {
        // Assumption: The token is stored in localStorage after login.
        // You must ensure your login logic saves the token like this:
        // localStorage.setItem('learnBuddyToken', data.access_token);
        const token = localStorage.getItem('learnBuddyToken');

        if (!token) {
            // If no token is found, redirect to the login page.
            console.error("No authentication token found. Redirecting to login.");
            window.location.href = 'auth.html';
            return;
        }

        try {
            // Use Promise.all to fetch user profile, stats, and achievements concurrently
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
            console.error("Failed to load profile data:", error);
            // Optional: Show an error message to the user on the page
        }
    }

    /**
     * Updates the profile information section of the UI.
     * @param {object} profile - The user profile data from /users/me.
     */
    function updateProfileUI(profile) {
        if (usernameSpan) usernameSpan.textContent = profile.username;
        if (emailSpan) emailSpan.textContent = profile.email;
        if (accountUsernameSpan) accountUsernameSpan.textContent = profile.username;
        if (accountEmailSpan) accountEmailSpan.textContent = profile.email;
    }

    /**
     * Updates the learning stats section of the UI.
     * @param {object} stats - The user stats data from /users/me/stats.
     */
    function updateStatsUI(stats) {
        if (xpValueSpan) xpValueSpan.textContent = stats.xp;
        if (streakValueSpan) streakValueSpan.textContent = stats.streak_count;
        if (lastLoginSpan) {
            // Format the date for better readability
            const lastLoginDate = new Date(stats.last_login_date);
            lastLoginSpan.textContent = lastLoginDate.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    }

    /**
     * Updates the achievements section of the UI.
     * @param {Array<object>} achievements - The list of achievements from /achievements.
     */
    function updateAchievementsUI(achievements) {
        if (!achievementsListDiv) return;

        achievementsListDiv.innerHTML = ''; // Clear any static/placeholder badges

        if (achievements.length === 0) {
            achievementsListDiv.innerHTML = '<p>No achievements unlocked yet. Keep learning!</p>';
            return;
        }

        achievements.forEach(ach => {
            const badge = document.createElement('span');
            badge.className = 'achievement-badge';
            badge.innerHTML = `<i class="${ach.icon_class}"></i> ${ach.name}`;
            badge.title = ach.description; // Add description on hover
            achievementsListDiv.appendChild(badge);
        });
    }

    // --- Event Listeners ---
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            // Clear user token and redirect to login
            localStorage.removeItem('learnBuddyToken');
            window.location.href = 'auth.html';
        });
    }


    // --- Load initial data from the backend ---
    loadProfileData();
});