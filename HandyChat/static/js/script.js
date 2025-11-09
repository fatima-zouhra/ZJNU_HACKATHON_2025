const API_BASE = '/api/chat';

function askQuestion() {
    const input = document.getElementById('chatInput');
    const question = input.value.trim();
    if (!question) return;
    
    addMessage(question, 'user');
    input.value = '';
    showTypingIndicator();

    fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        hideTypingIndicator();
        handleBotResponse(data, question);
    })
    .catch(error => { 
        hideTypingIndicator(); 
        console.error('Error:', error);
        addMessage('Sorry, there was an error connecting to the server. Please try again.', 'bot');
    });
}

// ... rest of your JavaScript functions remain the same
function askQuickQuestion(question) {
    document.getElementById('chatInput').value = question;
    askQuestion();
}

function handleBotResponse(data, originalQuestion) {
    if (data.status === 'success') {
        if (data.type === 'pe' || data.sport) {
            showPEClassResponse(data, originalQuestion);
        } else if (data.type === 'handbook') {
            showHandbookResponse(data, originalQuestion);
        } else if (data.type === 'combined') {
            showCombinedResponse(data, originalQuestion);
        } else {
            addMessage(data.response, 'bot');
        }
        
        if (data.suggestions && data.suggestions.length > 0) {
            showSuggestions(data.suggestions);
        }
    } else if (data.status === 'not_found') {
        showNotFoundResponse(data);
    } else if (data.status === 'clarify_needed') {
        showClarifyResponse(data);
    } else {
        addMessage(data.response || 'Sorry, I encountered an error.', 'bot');
    }
}

function showPEClassResponse(data, originalQuestion) {
    let html = '';
    
    html += `<div class="response-title">${getSportEmoji(data.sport)} ${data.sport.charAt(0).toUpperCase() + data.sport.slice(1)} Class</div>`;
    html += `<p>${data.response}</p>`;
    
    if (data.location_details) {
        const loc = data.location_details;
        html += `<div class="location-details">`;
        html += `<div class="location-title"><i class="fas fa-map-marker-alt"></i> ${loc.name}</div>`;
        html += `<div class="info-grid">`;
        if (loc.building) html += `<div class="info-item"><i class="fas fa-building"></i> ${loc.building}</div>`;
        if (loc.floor) html += `<div class="info-item"><i class="fas fa-layer-group"></i> ${loc.floor}</div>`;
        if (loc.room_number) html += `<div class="info-item"><i class="fas fa-door-open"></i> Room ${loc.room_number}</div>`;
        html += `</div>`;
        if (loc.description) html += `<p style="margin-top: 10px; color: var(--gray); font-size: 14px;">${loc.description}</p>`;
        html += `</div>`;
    }
    
    if (data.schedule) {
        const sched = data.schedule;
        html += `<div class="response-section">`;
        html += `<div class="response-title"><i class="fas fa-calendar"></i> Schedule</div>`;
        html += `<div class="schedule-badges">`;
        if (sched.day) html += `<div class="schedule-badge">${sched.day}</div>`;
        if (sched.time) html += `<div class="schedule-badge">${sched.time}</div>`;
        if (sched.semester) html += `<div class="schedule-badge">${sched.semester}</div>`;
        html += `</div>`;
        html += `</div>`;
    }
    
    if (data.teacher && data.teacher.name) {
        const teacher = data.teacher;
        html += `<div class="response-section">`;
        html += `<div class="response-title"><i class="fas fa-chalkboard-teacher"></i> Instructor</div>`;
        html += `<div class="info-grid">`;
        html += `<div class="info-item"><i class="fas fa-user"></i> ${teacher.name}</div>`;
        if (teacher.contact) html += `<div class="info-item"><i class="fas fa-phone"></i> ${teacher.contact}</div>`;
        if (teacher.email) html += `<div class="info-item"><i class="fas fa-envelope"></i> ${teacher.email}</div>`;
        html += `</div>`;
        html += `</div>`;
    }
    
    if (data.images && data.images.length > 0) {
        html += `<div class="response-section">`;
        html += `<div class="response-title"><i class="fas fa-images"></i> Location Photos</div>`;
        html += `<div class="media-grid">`;
        data.images.forEach((img, index) => {
            if (index < 4) {
                html += `<div class="media-card">`;
                html += `<img src="${img}" alt="Location photo ${index + 1}" onerror="this.style.display='none'">`;
                html += `<div class="media-caption">Photo ${index + 1}</div>`;
                html += `</div>`;
            }
        });
        html += `</div>`;
        html += `</div>`;
    }
    
    if (data.maps && (data.maps.amap_link || data.maps.baidu_map_link)) {
        html += `<div class="response-section">`;
        html += `<div class="response-title"><i class="fas fa-map"></i> Navigation</div>`;
        html += `<div class="map-buttons">`;
        if (data.maps.amap_link && data.maps.amap_link !== "https://uri.amap.com/xxx") {
            html += `<a href="${data.maps.amap_link}" target="_blank" class="map-btn amap-btn">`;
            html += `<i class="fas fa-map-marked-alt"></i> Amap`;
            html += `</a>`;
        }
        if (data.maps.baidu_map_link && data.maps.baidu_map_link !== "https://api.map.baidu.com/xxx") {
            html += `<a href="${data.maps.baidu_map_link}" target="_blank" class="map-btn baidu-btn">`;
            html += `<i class="fas fa-map-pin"></i> Baidu Maps`;
            html += `</a>`;
        }
        html += `</div>`;
        html += `</div>`;
    }
    
    if (data.ai_enhanced) {
        html += `<div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid var(--gray-light); font-size: 12px; color: var(--gray);">`;
        html += `<i class="fas fa-robot"></i> AI Enhanced • Your question: "${escapeHtml(originalQuestion)}"`;
        html += `</div>`;
    }
    
    addMessage(html, 'bot', true);
}

function showHandbookResponse(data, originalQuestion) {
    let html = '';
    
    html += `<div class="response-title"><i class="fas fa-book"></i> Handbook Information</div>`;
    html += `<div class="response-content">`;
    
    const content = data.answer || data.response;
    const formattedContent = content.replace(/\n/g, '<br>');
    html += `<p>${formattedContent}</p>`;
    
    html += `</div>`;
    
    html += `<div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid var(--gray-light);">`;
    html += `<div style="font-size: 12px; color: var(--gray);">`;
    if (data.source) html += `<div><i class="fas fa-database"></i> Source: ${data.source}</div>`;
    if (data.ai_enhanced) html += `<div><i class="fas fa-robot"></i> AI Enhanced</div>`;
    html += `<div>Your question: "${escapeHtml(originalQuestion)}"</div>`;
    html += `</div>`;
    html += `</div>`;
    
    addMessage(html, 'bot', true);
}

function showCombinedResponse(data, originalQuestion) {
    let html = '';
    
    html += `<div class="response-title"><i class="fas fa-link"></i> Combined Information</div>`;
    html += `<div class="response-content">`;
    html += `<p>${data.response}</p>`;
    html += `</div>`;
    
    if (data.ai_generated) {
        html += `<div style="margin-top: 10px; font-size: 12px; color: var(--gray);">`;
        html += `<i class="fas fa-robot"></i> AI Generated Response`;
        html += `</div>`;
    }
    
    addMessage(html, 'bot', true);
}

function showNotFoundResponse(data) {
    let html = `<div class="response-title"><i class="fas fa-search"></i> Not Found</div>`;
    html += `<p>${data.response}</p>`;
    
    if (data.available_sports && data.available_sports.length > 0) {
        html += `<div class="suggestions">`;
        html += `<div class="suggestion-title">Available Sports:</div>`;
        html += `<div class="suggestion-buttons">`;
        data.available_sports.forEach(sport => {
            html += `<button class="suggestion-btn" onclick="askQuickQuestion('${sport} class')">${getSportEmoji(sport)} ${sport}</button>`;
        });
        html += `</div>`;
        html += `</div>`;
    }
    
    addMessage(html, 'bot', true);
}

function showClarifyResponse(data) {
    let html = `<div class="response-title"><i class="fas fa-question-circle"></i> Need Clarification</div>`;
    html += `<p>${data.response}</p>`;
    
    if (data.available_sports && data.available_sports.length > 0) {
        html += `<div class="suggestions">`;
        html += `<div class="suggestion-title">Try asking about:</div>`;
        html += `<div class="suggestion-buttons">`;
        data.available_sports.forEach(sport => {
            html += `<button class="suggestion-btn" onclick="askQuickQuestion('${sport} class location')">${getSportEmoji(sport)} ${sport}</button>`;
        });
        html += `</div>`;
        html += `</div>`;
    }
    
    if (data.examples && data.examples.length > 0) {
        html += `<div class="suggestions" style="margin-top: 10px;">`;
        html += `<div class="suggestion-title">Example Questions:</div>`;
        html += `<div class="suggestion-buttons">`;
        data.examples.forEach(example => {
            html += `<button class="suggestion-btn" onclick="askQuickQuestion('${example}')">"${example}"</button>`;
        });
        html += `</div>`;
        html += `</div>`;
    }
    
    addMessage(html, 'bot', true);
}

function showSuggestions(suggestions) {
    let html = `<div class="suggestions">`;
    html += `<div class="suggestion-title">Related Questions:</div>`;
    html += `<div class="suggestion-buttons">`;
    suggestions.forEach(suggestion => {
        html += `<button class="suggestion-btn" onclick="askQuickQuestion('${escapeHtml(suggestion)}')">${escapeHtml(suggestion)}</button>`;
    });
    html += `</div>`;
    html += `</div>`;
    
    const lastBotMessage = document.querySelector('.message.bot:last-child .message-content');
    if (lastBotMessage) {
        lastBotMessage.innerHTML += html;
    }
}

function addMessage(content, sender, isHTML = false) {
    const container = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isHTML) {
        contentDiv.innerHTML = content;
    } else {
        contentDiv.textContent = content;
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);
    
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const container = document.getElementById('messagesContainer');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div style="display: flex; align-items: center; gap: 10px; color: var(--gray);">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                Assistant is typing...
            </div>
        </div>
    `;
    
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function getSportEmoji(sport) {
    const emojiMap = {
        basketball: "🏀",
        swimming: "🏊",
        tennis: "🎾",
        badminton: "🏸",
        soccer: "⚽",
        volleyball: "🏐",
        "table tennis": "🏓",
        "tai chi": "☯️",
    };
    return emojiMap[sport.toLowerCase()] || "🎯";
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// School Map Functions
function showSchoolMap() {
    const modal = document.getElementById('schoolMapModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    } else {
        addMessage("The interactive campus map feature is coming soon! For now, you can ask me about specific locations like 'Where is the library?' or 'Where are the basketball courts?'", 'bot');
    }
}

function showFullScreenMap() {
    showSchoolMap();
}

function closeSchoolMap() {
    const modal = document.getElementById('schoolMapModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        resetMap();
    }
}

function zoomIn() {
    const map = document.querySelector('.campus-map');
    if (map) {
        const currentScale = parseFloat(map.style.transform.replace('scale(', '').replace(')', '')) || 1;
        map.style.transform = `scale(${Math.min(currentScale + 0.2, 3)})`;
    }
}

function zoomOut() {
    const map = document.querySelector('.campus-map');
    if (map) {
        const currentScale = parseFloat(map.style.transform.replace('scale(', '').replace(')', '')) || 1;
        map.style.transform = `scale(${Math.max(currentScale - 0.2, 0.5)})`;
    }
}

function resetMap() {
    const map = document.querySelector('.campus-map');
    if (map) {
        map.style.transform = 'scale(1)';
    }
}

function downloadMap() {
    addMessage("You can download the campus map from the university's official website or visit the administration office for a printed copy.", 'bot');
    closeSchoolMap();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('schoolMapModal');
    if (event.target === modal) {
        closeSchoolMap();
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeSchoolMap();
    }
});

document.getElementById('chatInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        askQuestion();
    }
});

document.getElementById('chatInput').focus();