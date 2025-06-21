/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

document.addEventListener('DOMContentLoaded', () => {
    const LS_PREFIX = 'learnBuddy_';

    // --- DOM Elements ---
    const hamburgerButton = document.getElementById('hamburgerButton');
    const mobileMenu = document.getElementById('mobileMenu');
    const menuIcon = document.getElementById('menuIcon');
    const closeIcon = document.getElementById('closeIcon');

    const editProfilePicButton = document.getElementById('editProfilePicButton');
    const profilePicInput = document.getElementById('profilePicInput');
    const mainProfileAvatar = document.getElementById('mainProfileAvatar');
    const headerProfileAvatar = document.getElementById('headerProfileAvatar');

    const profileNameDisplay = document.getElementById('profileNameDisplay');
    const profileNameInput = document.getElementById('profileNameInput');
    const profileAgeDisplay = document.getElementById('profileAgeDisplay');
    const profileAgeInput = document.getElementById('profileAgeInput');
    const editProfileButton = document.getElementById('editProfileButton');
    const saveProfileButton = document.getElementById('saveProfileButton');
    const cancelProfileButton = document.getElementById('cancelProfileButton');
    const profileSavedMessage = document.getElementById('profileSavedMessage');

    const mathProgressBar = document.getElementById('mathProgressBar');
    const mathProgressText = document.getElementById('mathProgressText');
    const mathLessonsCount = document.getElementById('mathLessonsCount');
    const completeMathLessonButton = document.getElementById('completeMathLessonButton');

    const readingProgressBar = document.getElementById('readingProgressBar');
    const readingProgressText = document.getElementById('readingProgressText');
    const readingLessonsCount = document.getElementById('readingLessonsCount');
    const completeReadingLessonButton = document.getElementById('completeReadingLessonButton');

    const newActivityInput = document.getElementById('newActivityInput');
    const addActivityButton = document.getElementById('addActivityButton');
    const recentActivitiesList = document.getElementById('recentActivitiesList');
    const clearActivitiesButton = document.getElementById('clearActivitiesButton');

    const parentalControlsList = document.getElementById('parentalControlsList');

    // --- State Variables (with defaults) ---
    let profileState = {
        name: "Ella",
        age: "Age 5",
        avatar: null
    };
    let progressState = {
        math: {
            percent: 70,
            lessons: 3
        },
        reading: {
            percent: 90,
            lessons: 4
        }
    };
    let activitiesState = [{
            name: "Counting 101",
            status: "Completed lesson",
            percent: "100%",
            imageClass: "activity-image-1"
        },
        {
            name: "Addition 101",
            status: "Completed lesson",
            percent: "100%",
            imageClass: "activity-image-2"
        },
        {
            name: "Subtraction 101",
            status: "Completed lesson",
            percent: "100%",
            imageClass: "activity-image-3"
        },
        {
            name: "Spelling 101",
            status: "Completed lesson",
            percent: "100%",
            imageClass: "activity-image-4"
        },
        {
            name: "Reading 101",
            status: "Completed lesson",
            percent: "100%",
            imageClass: "activity-image-5"
        }
    ];
    let parentalControlsState = [{
            id: "mathSwitch",
            subject: "Math",
            description: "Turn off lessons in this subject",
            enabled: true
        },
        {
            id: "readingSwitch",
            subject: "Reading",
            description: "Turn off lessons in this subject",
            enabled: true
        },
        {
            id: "artSwitch",
            subject: "Art",
            description: "Turn off lessons in this subject",
            enabled: false
        },
        {
            id: "scienceSwitch",
            subject: "Science",
            description: "Turn off lessons in this subject",
            enabled: true
        },
        {
            id: "musicSwitch",
            subject: "Music",
            description: "Turn off lessons in this subject",
            enabled: false
        },
        {
            id: "peSwitch",
            subject: "P.E.",
            description: "Turn off lessons in this subject",
            enabled: true
        },
    ];

    // --- LocalStorage Functions ---
    function saveToLS(key, data) {
        try {
            localStorage.setItem(LS_PREFIX + key, JSON.stringify(data));
        } catch (e) {
            console.error("Error saving to localStorage:", e);
        }
    }

    function loadFromLS(key, defaultValue) {
        try {
            const storedValue = localStorage.getItem(LS_PREFIX + key);
            return storedValue ? JSON.parse(storedValue) : defaultValue;
        } catch (e) {
            console.error("Error loading from localStorage:", e);
            return defaultValue;
        }
    }

    // --- Initialization ---
    function loadStateFromLocalStorage() {
        profileState = loadFromLS('profile', profileState);
        progressState = loadFromLS('progress', progressState);
        activitiesState = loadFromLS('activities', activitiesState);
        parentalControlsState = loadFromLS('parentalControls', parentalControlsState);

        updateProfileUI();
        updateProgressUI('math');
        updateProgressUI('reading');
        renderRecentActivities();
        renderParentalControls();

        if (profileState.avatar && mainProfileAvatar && headerProfileAvatar) {
            mainProfileAvatar.style.backgroundImage = `url(${profileState.avatar})`;
            headerProfileAvatar.style.backgroundImage = `url(${profileState.avatar})`;
        }
    }

    // --- UI Update Functions ---
    function updateProfileUI() {
        if (profileNameDisplay) profileNameDisplay.textContent = profileState.name;
        if (profileNameInput) profileNameInput.value = profileState.name;
        if (profileAgeDisplay) profileAgeDisplay.textContent = profileState.age;
        if (profileAgeInput) profileAgeInput.value = profileState.age;
    }

    function showProfileEditMode(isEditing) {
        profileNameDisplay?.classList.toggle('hidden', isEditing);
        profileNameInput?.classList.toggle('hidden', !isEditing);
        profileAgeDisplay?.classList.toggle('hidden', isEditing);
        profileAgeInput?.classList.toggle('hidden', !isEditing);
        editProfileButton?.classList.toggle('hidden', isEditing);
        saveProfileButton?.classList.toggle('hidden', !isEditing);
        cancelProfileButton?.classList.toggle('hidden', !isEditing);
        if (isEditing && profileNameInput) profileNameInput.focus();
    }

    function showConfirmationMessage(element, message, duration = 2000) {
        if (!element) return;
        element.textContent = message;
        element.classList.remove('hidden', 'fade-out');
        element.classList.add('fade-in');
        setTimeout(() => {
            element.classList.remove('fade-in');
            element.classList.add('fade-out');
            setTimeout(() => element.classList.add('hidden'), 500); // Wait for fade out
        }, duration);
    }

    function animatePercentage(element, startValue, endValue, duration = 300) {
        if (!element) return;
        let startTime = null;

        function animationStep(timestamp) {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            const currentValue = Math.floor(progress * (endValue - startValue) + startValue);
            element.textContent = `${currentValue}% complete`;
            if (progress < 1) {
                requestAnimationFrame(animationStep);
            } else {
                element.textContent = `${endValue}% complete`; // Ensure final value is accurate
            }
        }
        requestAnimationFrame(animationStep);
    }

    function updateProgressUI(subject, animate = false, oldPercentValue = null) {
        const bar = subject === 'math' ? mathProgressBar : readingProgressBar;
        const textElement = subject === 'math' ? mathProgressText : readingProgressText;
        const lessons = subject === 'math' ? mathLessonsCount : readingLessonsCount;

        const currentPercent = progressState[subject].percent;

        if (bar) bar.style.width = `${currentPercent}%`;
        if (lessons) lessons.textContent = progressState[subject].lessons.toString();

        if (textElement) {
            if (animate && oldPercentValue !== null && oldPercentValue !== currentPercent) {
                animatePercentage(textElement, oldPercentValue, currentPercent);
            } else {
                textElement.textContent = `${currentPercent}% complete`;
            }
        }
    }

    function renderRecentActivities() {
        if (!recentActivitiesList) return;
        recentActivitiesList.innerHTML = ''; // Clear existing
        activitiesState.forEach((activity, index) => {
            const activityElement = `
        <div class="flex items-center gap-4 bg-[#18141f] px-4 min-h-[72px] py-2 justify-between activity-item recent-activity-wrapper" style="animation-delay: ${index * 0.05}s">
          <div class="flex items-center gap-4 overflow-hidden">
            <div class="bg-center bg-no-repeat aspect-square bg-cover rounded-lg size-14 shrink-0 ${activity.imageClass || 'activity-image-default'} activity-image-container"></div>
            <div class="flex flex-col justify-center overflow-hidden">
              <p class="text-white text-base font-medium leading-normal truncate">${activity.name}</p>
              <p class="text-[#aa9bc0] text-sm font-normal leading-normal truncate">${activity.status}</p>
            </div>
          </div>
          <div class="shrink-0 ml-2"><p class="text-white text-base font-normal leading-normal">${activity.percent}</p></div>
        </div>`;
            recentActivitiesList.insertAdjacentHTML('beforeend', activityElement);
        });
    }

    function renderParentalControls() {
        if (!parentalControlsList) return;
        parentalControlsList.innerHTML = '';
        parentalControlsState.forEach((control, index) => {
            const controlHtml = `
            <div class="flex items-center justify-between gap-4 bg-[#18141f] px-4 min-h-[72px] py-2 parental-control-item" style="animation-delay: ${index * 0.05}s">
              <div class="flex flex-col justify-center">
                <p class="text-white text-base font-medium leading-normal line-clamp-1">${control.subject}</p>
                <p class="text-[#aa9bc0] text-sm font-normal leading-normal line-clamp-2">${control.description}</p>
              </div>
              <label for="${control.id}" class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" id="${control.id}" class="sr-only peer toggle-checkbox" data-index="${index}" ${control.enabled ? 'checked' : ''} role="switch" aria-checked="${control.enabled}">
                <div class="w-11 h-6 toggle-label-bg rounded-full peer peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-[#773fcb] peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all toggle-switch"></div>
              </label>
            </div>
        `;
            parentalControlsList.insertAdjacentHTML('beforeend', controlHtml);
        });

        // Add event listeners after rendering
        parentalControlsState.forEach((control) => {
            const checkbox = document.getElementById(control.id);
            checkbox?.addEventListener('change', (event) => {
                const target = event.target;
                const controlIndex = parseInt(target.dataset.index, 10);
                parentalControlsState[controlIndex].enabled = target.checked;
                target.setAttribute('aria-checked', target.checked.toString());
                saveToLS('parentalControls', parentalControlsState);
            });
        });
    }


    // --- Event Listeners ---
    hamburgerButton?.addEventListener('click', () => {
        const isMenuOpen = mobileMenu?.classList.toggle('hidden');
        hamburgerButton.setAttribute('aria-expanded', String(!isMenuOpen));
        menuIcon?.classList.toggle('hidden', !isMenuOpen);
        closeIcon?.classList.toggle('hidden', isMenuOpen);
    });

    window.addEventListener('resize', () => {
        const mdBreakpoint = 768;
        if (window.innerWidth >= mdBreakpoint) {
            if (!mobileMenu?.classList.contains('hidden')) {
                mobileMenu?.classList.add('hidden');
                hamburgerButton?.setAttribute('aria-expanded', 'false');
                menuIcon?.classList.remove('hidden');
                closeIcon?.classList.add('hidden');
            }
        }
    });

    editProfilePicButton?.addEventListener('click', () => profilePicInput?.click());

    profilePicInput?.addEventListener('change', (event) => {
        const target = event.target;
        const file = target.files?. [0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const imageUrl = e.target?.result;
                if (imageUrl && typeof imageUrl === 'string') {
                    if (mainProfileAvatar) mainProfileAvatar.style.backgroundImage = `url(${imageUrl})`;
                    if (headerProfileAvatar) headerProfileAvatar.style.backgroundImage = `url(${imageUrl})`;
                    profileState.avatar = imageUrl;
                    saveToLS('profile', profileState);
                }
            }
            reader.readAsDataURL(file);
        } else if (file) {
            alert("Please select a valid image file (e.g., JPG, PNG).");
        }
    });

    editProfileButton?.addEventListener('click', () => showProfileEditMode(true));

    cancelProfileButton?.addEventListener('click', () => {
        if (profileNameInput) profileNameInput.value = profileState.name;
        if (profileAgeInput) profileAgeInput.value = profileState.age;
        showProfileEditMode(false);
    });

    saveProfileButton?.addEventListener('click', () => {
        profileState.name = profileNameInput?.value || profileState.name;
        profileState.age = profileAgeInput?.value || profileState.age;
        updateProfileUI();
        saveToLS('profile', profileState);
        showProfileEditMode(false);
        showConfirmationMessage(profileSavedMessage, "Profile Saved!");
    });

    function handleCompleteLesson(subject) {
        const oldPercent = progressState[subject].percent;
        if (progressState[subject].percent < 100) {
            progressState[subject].percent = Math.min(100, progressState[subject].percent + 10);
        }
        progressState[subject].lessons += 1;
        updateProgressUI(subject, true, oldPercent); // Pass true to animate and oldPercent
        saveToLS('progress', progressState);
    }

    completeMathLessonButton?.addEventListener('click', () => handleCompleteLesson('math'));
    completeReadingLessonButton?.addEventListener('click', () => handleCompleteLesson('reading'));

    addActivityButton?.addEventListener('click', () => {
        const activityName = newActivityInput?.value.trim();
        if (activityName && newActivityInput) {
            activitiesState.unshift({
                name: activityName,
                status: "Newly added",
                percent: "0%",
                imageClass: "activity-image-default"
            });
            newActivityInput.value = '';
            renderRecentActivities();
            saveToLS('activities', activitiesState);
        } else if (newActivityInput) {
            newActivityInput.focus();
        }
    });

    clearActivitiesButton?.addEventListener('click', () => {
        if (confirm("Are you sure you want to clear all recent activities?")) {
            activitiesState = [];
            renderRecentActivities();
            saveToLS('activities', activitiesState);
        }
    });

    // --- Load initial state from LocalStorage ---
    loadStateFromLocalStorage();
});