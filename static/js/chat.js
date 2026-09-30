// Conversational AI Chatbot Client JS

let isChatInitialized = false;

window.initChatView = function() {
    if (isChatInitialized) return;
    isChatInitialized = true;

    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msgText = chatInput.value.trim();
            if (!msgText) return;

            // Render User Message
            appendMessage(msgText, 'user');
            chatInput.value = '';

            // Render Typing Indicator
            const typingId = appendTypingIndicator();

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msgText })
                });

                const data = await res.json();
                removeMessage(typingId);

                if (data.success) {
                    appendMessage(data.bot_response, 'bot');
                    updateAIInsightsPanel(data.nlp_analysis, data.context_memory);

                    if (data.nlp_analysis.is_critical) {
                        showCrisisBanner(data.bot_response);
                    }
                } else {
                    appendMessage("I apologize, but I encountered an error processing your message. Please try again.", 'bot');
                }
            } catch (err) {
                removeMessage(typingId);
                appendMessage("Network communication error. Please check your connection.", 'bot');
            }
        });
    }

    // Load existing messages for active conversation
    loadConversationHistory();
};

async function loadConversationHistory() {
    try {
        const res = await fetch('/api/chat/history');
        const data = await res.json();
        if (data.success && data.messages) {
            const container = document.getElementById('chatMessages');
            container.innerHTML = '';
            data.messages.forEach(m => {
                appendMessage(m.message, m.sender);
            });
            container.scrollTop = container.scrollHeight;
        }
    } catch (e) {
        console.error("Error loading chat history:", e);
    }
}

function appendMessage(text, sender) {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message-bubble message-${sender}`;
    msgDiv.innerHTML = text.replace(/\n/g, '<br>');
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
    return msgDiv;
}

function appendTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    const id = 'typing_' + Date.now();
    typingDiv.id = id;
    typingDiv.className = 'message-bubble message-bot';
    typingDiv.innerHTML = '<em>Support AI is reflecting...</em>';
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function updateAIInsightsPanel(nlp, context) {
    const emotionEl = document.getElementById('insightEmotion');
    const intentEl = document.getElementById('insightIntent');
    const sentimentEl = document.getElementById('insightSentiment');
    const riskEl = document.getElementById('insightRisk');
    const xaiTokensEl = document.getElementById('insightXAI');

    if (emotionEl) emotionEl.innerText = `${nlp.emotion} (${Math.round(nlp.emotion_confidence * 100)}%)`;
    if (intentEl) intentEl.innerText = nlp.intent;
    if (sentimentEl) sentimentEl.innerText = `${nlp.sentiment} (Score: ${nlp.sentiment_score})`;
    if (riskEl) {
        riskEl.innerText = nlp.risk_level;
        riskEl.className = nlp.is_critical ? 'insight-val status-danger' : 'insight-val';
    }

    if (xaiTokensEl && nlp.xai && nlp.xai.key_feature_weights) {
        let html = '<ul style="list-style:none;padding:0;font-size:0.85rem;">';
        nlp.xai.key_feature_weights.forEach(w => {
            html += `<li style="margin-bottom:4px;">🔑 <strong>"${w.word}"</strong>: <span style="color:#38bdf8">${w.influence}</span></li>`;
        });
        html += '</ul>';
        xaiTokensEl.innerHTML = html;
    }
}

function showCrisisBanner(crisisMessage) {
    const banner = document.getElementById('globalCrisisBanner');
    if (banner) {
        banner.style.display = 'flex';
        document.getElementById('crisisBannerText').innerText = "Crisis/Safety Support Triggered. Immediate help resources available.";
    }
}
