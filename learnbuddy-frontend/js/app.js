document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('home-body') || document.body.classList.contains('auth-body')) return; // Exit if not on the main app page

    // --- SECTION 1: DOM ELEMENT SELECTOR & STATE ---
    const token = getToken();
    if (!token) { window.location.href = 'auth.html'; return; }

    const elements = {
        appBody: document.getElementById('app-body'), dashboardView: document.getElementById('dashboard-view'), lessonView: document.getElementById('lesson-view'),
        startLessonBtn: document.getElementById('start-lesson-btn'), questionText: document.getElementById('question-text'), answerForm: document.getElementById('answer-form'),
        userAnswerInput: document.getElementById('user-answer'), progressBar: document.getElementById('progress-bar'), difficultyIndicator: document.getElementById('difficulty-indicator'),
        themeSelector: document.getElementById('theme-selector'), increaseFontBtn: document.querySelector('[data-action="increase-font"]'),
        decreaseFontBtn: document.querySelector('[data-action="decrease-font"]'), fontSwitch: document.getElementById('font-switch'),
        readAloudBtn: document.getElementById('read-aloud-btn'), voiceCommandBtn: document.getElementById('voice-command-btn'), voiceStatus: document.getElementById('voice-status'),
        logoutBtn: document.getElementById('logout-btn')
    };

    let state = { currentQuestion: null, lessonProgress: 0, fontSizeIndex: 1, isListening: false };

    // --- SECTION 2: ACCESSIBILITY & SETTINGS ---
    const applyPreference = (key, value) => {
        localStorage.setItem(key, value);
        if (key === 'theme') {
            const currentClasses = Array.from(elements.appBody.classList).filter(c => c.startsWith('font-'));
            elements.appBody.className = `${value} ${currentClasses.join(' ')}`;
        } else if (key === 'fontFamily') {
            elements.appBody.classList.toggle('font-family-alt', value);
        } else if (key === 'fontSizeIndex') {
            state.fontSizeIndex = parseInt(value);
            for(let i=0; i<=3; i++) elements.appBody.classList.remove(`font-size-${i}`);
            elements.appBody.classList.add(`font-size-${state.fontSizeIndex}`);
        }
    };
    const loadPreferences = () => {
        const theme = localStorage.getItem('theme') || 'theme-lumina';
        elements.themeSelector.value = theme; applyPreference('theme', theme);
        state.fontSizeIndex = parseInt(localStorage.getItem('fontSizeIndex') || '1'); applyPreference('fontSizeIndex', state.fontSizeIndex);
        const useAltFont = localStorage.getItem('fontFamily') === 'true'; elements.fontSwitch.checked = useAltFont; applyPreference('fontFamily', useAltFont);
    };
    elements.themeSelector.addEventListener('change', e => applyPreference('theme', e.target.value));
    elements.increaseFontBtn.addEventListener('click', () => applyPreference('fontSizeIndex', Math.min(3, state.fontSizeIndex + 1)));
    elements.decreaseFontBtn.addEventListener('click', () => applyPreference('fontSizeIndex', Math.max(0, state.fontSizeIndex - 1)));
    elements.fontSwitch.addEventListener('change', e => applyPreference('fontFamily', e.target.checked));
    
    // --- SECTION 3: SPEECH API ---
    const synth = window.speechSynthesis;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false; recognition.lang = 'en-US';
        recognition.onstart = () => { state.isListening = true; elements.voiceStatus.textContent = "Listening..."; elements.voiceCommandBtn.classList.add('is-listening'); };
        recognition.onend = () => { state.isListening = false; elements.voiceStatus.textContent = "Say 'Submit' or 'Repeat'"; elements.voiceCommandBtn.classList.remove('is-listening'); };
        recognition.onresult = e => {
            const command = e.results[0][0].transcript.toLowerCase().trim();
            if (command.includes('submit')) elements.answerForm.requestSubmit ? elements.answerForm.requestSubmit() : elements.answerForm.submit();
            if (command.includes('repeat')) speak(elements.questionText.textContent);
        };
        elements.voiceCommandBtn.addEventListener('click', () => state.isListening ? recognition.stop() : recognition.start());
    } else { if(elements.voiceCommandBtn) elements.voiceCommandBtn.closest('.voice-controls').style.display = 'none'; }
    const speak = (text) => { if(synth.speaking) synth.cancel(); if(text) synth.speak(new SpeechSynthesisUtterance(text)); };
    elements.readAloudBtn.addEventListener('click', () => speak(elements.questionText.textContent));

    // --- SECTION 4: CORE APP LOGIC ---
    const fetchNextQuestion = async () => {
        elements.userAnswerInput.value = ''; elements.userAnswerInput.disabled = false; elements.userAnswerInput.focus();
        try {
            const res = await fetch(`${API_BASE_URL}/next_question`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ lesson_id: 1 }) });
            if (!res.ok) throw new Error("Could not fetch quest.");
            state.currentQuestion = await res.json();
            elements.questionText.textContent = state.currentQuestion.question_text;
            elements.difficultyIndicator.textContent = `Soil: Level ${state.currentQuestion.difficulty_level}`;
        } catch (error) { showStatus(error.message, true); }
    };
    const submitAnswer = async e => {
        e.preventDefault(); if (!state.currentQuestion || elements.userAnswerInput.disabled) return;
        elements.userAnswerInput.disabled = true;
        try {
            const res = await fetch(`${API_BASE_URL}/submit_answer`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ lesson_id: 1, question_id: state.currentQuestion.question_id, difficulty_answered: state.currentQuestion.difficulty_level, user_answer: elements.userAnswerInput.value }) });
            if (!res.ok) throw new Error('Submission failed.');
            const result = await res.json();
            state.lessonProgress = Math.min(100, state.lessonProgress + 10);
            elements.progressBar.style.width = `${state.lessonProgress}%`;
            showStatus(result.is_correct ? "Correct! 🌱" : "Let's try another one.", !result.is_correct);
            await new Promise(r => setTimeout(r, 1200));
            await fetchNextQuestion();
        } catch (error) { showStatus(error.message, true); elements.userAnswerInput.disabled = false; }
    };
    elements.startLessonBtn.addEventListener('click', () => { elements.dashboardView.classList.add('hidden'); elements.lessonView.classList.remove('hidden'); elements.lessonView.classList.add('visible'); fetchNextQuestion(); });
    elements.answerForm.addEventListener('submit', submitAnswer);
    elements.logoutBtn.addEventListener('click', () => { localStorage.removeItem('learnbuddy_token'); window.location.href = 'index.html'; });
    loadPreferences();
});