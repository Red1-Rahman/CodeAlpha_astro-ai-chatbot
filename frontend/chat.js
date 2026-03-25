// --- CORE DOM ELEMENTS ---
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const themeToggle = document.getElementById('theme-toggle');
const sunIcon = document.getElementById('sun-icon');
const moonIcon = document.getElementById('moon-icon');

// --- THEME MANAGEMENT ---
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        sunIcon.style.display = 'block';
        moonIcon.style.display = 'none';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
    }
}

themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        sunIcon.style.display = 'block';
        moonIcon.style.display = 'none';
    }
});

initTheme();

// --- UTILITY ---
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// --- CHAT LOGIC ---
let isLoading = false;

function addMessage(text, isUser = false, isMarkdown = false) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', isUser ? 'user-message' : 'bot-message');

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');

    if (isMarkdown && !isUser) {
        // Sanitize to prevent XSS
        const rawHTML = marked.parse(text);
        contentDiv.innerHTML = DOMPurify.sanitize(rawHTML);
    } else {
        contentDiv.textContent = text;
    }

    msgDiv.appendChild(contentDiv);
    chatBox.appendChild(msgDiv);
    scrollToBottom();
    return msgDiv;
}

function addRelatedQuestions(msgElement, questions) {
    if (!questions || questions.length === 0) return;

    const contentDiv = msgElement.querySelector('.message-content');
    questions.forEach(q => {
        const btn = document.createElement('button');
        btn.classList.add('related-btn');
        btn.textContent = `↳ ${q.question}`;
        btn.addEventListener('click', () => {
            userInput.value = q.question;
            handleSend();
        });
        contentDiv.appendChild(btn);
    });
    scrollToBottom();
}

async function handleSend() {
    if (isLoading) return;
    const query = userInput.value.trim();
    if (!query) return;

    isLoading = true;
    addMessage(query, true);
    userInput.value = '';

    const typingIndicator = addMessage("Thinking...", false);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();
        typingIndicator.remove();
        const botMsgElement = addMessage(data.answer, false, true);
        addRelatedQuestions(botMsgElement, data.related_questions);
    } catch (error) {
        console.error("Fetch Error:", error);
        typingIndicator.remove();
        addMessage("Connection to the server was lost. Please check your network or try again later.", false);
    } finally {
        isLoading = false;
    }
}

// --- EVENT LISTENERS ---
sendBtn.addEventListener('click', handleSend);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});