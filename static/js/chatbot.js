class Chatbot {
    constructor() {
        this.isOpen = false;
        this.initElements();
        this.initEvents();
        this.isListening = false;
    }

    initElements() {
        // Создаем кнопку-тоггл
        this.toggleButton = document.createElement('button');
        this.toggleButton.className = 'chatbot-toggle';
        this.toggleButton.innerHTML = '💬';

        // Создаем контейнер чата
        this.chatbot = document.createElement('div');
        this.chatbot.className = 'chatbot-container';
        this.chatbot.innerHTML = `
            <div class="chatbot-header">
                <h3>Freshmart Assistant</h3>
                <button class="close-btn">×</button>
            </div>
            <div class="chatbot-messages"></div>
            <div class="chatbot-input">
                <input type="text" placeholder="Type your question..." class="chatbot-input-field">
                <button class="voice-btn">🎤</button>
                <button class="send-btn">Send</button>
            </div>
        `;

        document.body.appendChild(this.toggleButton);
        document.body.appendChild(this.chatbot);
    }

    initEvents() {
        this.messagesEl = this.chatbot.querySelector('.chatbot-messages');
        this.inputEl = this.chatbot.querySelector('.chatbot-input-field');
        this.sendBtn = this.chatbot.querySelector('.send-btn');
        this.voiceBtn = this.chatbot.querySelector('.voice-btn');
        this.closeBtn = this.chatbot.querySelector('.close-btn');

        // Обработчики событий
        this.toggleButton.addEventListener('click', () => this.toggleChat());
        this.closeBtn.addEventListener('click', () => this.toggleChat(false));
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.inputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceInput());
    }

    toggleChat(forceState) {
        this.isOpen = forceState !== undefined ? forceState : !this.isOpen;
        this.chatbot.classList.toggle('active', this.isOpen);
        this.toggleButton.innerHTML = this.isOpen ? '✕' : '💬';
    }

    async sendMessage() {
        const message = this.inputEl.value.trim();
        if (!message) return;

        this.addMessage('user', message);
        this.inputEl.value = '';

        await new Promise(resolve => setTimeout(resolve, 1000))

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'},
                    'X-CSRFToken': getCookie('csrftoken'),
                body: JSON.stringify({message: message})
            });
                if (response.status === 429) {
        alert("Слишком много запросов! Подождите немного.");
        return;
    }


    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

            const data = await response.json();
            this.addMessage('bot', data.response);
        } catch (error) {
            this.addMessage('bot', "Sorry, I'm having trouble connecting.");
        }
    }

toggleVoiceInput() {
        if (this.isListening) {
            this.stopVoiceRecognition();
            return;
        }

        this.voiceBtn.textContent = '🔴';
        this.isListening = true;

        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.lang = 'ru-RU'

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.inputEl.value = transcript;
            this.stopVoiceRecognition();
        };

        recognition.onerror = () => this.stopVoiceRecognition();
        recognition.start();
    }

    stopVoiceRecognition() {
        this.voiceBtn.textContent = '🎤';
        this.isListening = false;
    }

    addMessage(sender, text) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${sender}`;
        messageEl.textContent = text;
        this.messagesEl.appendChild(messageEl);
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => new Chatbot());