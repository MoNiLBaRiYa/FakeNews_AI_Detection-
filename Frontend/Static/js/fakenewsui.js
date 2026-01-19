document.addEventListener("DOMContentLoaded", function () {
    const messagesDiv = document.getElementById("messages");
    const messageInput = document.getElementById("messageInput");
    const newsQueryInput = document.getElementById("newsQuery");
    const newsList = document.getElementById("newsList");

    // Show welcome message
    setTimeout(() => {
        addMessage("👋 Welcome! I'm your Fake News Detector. I support English, Hindi (हिंदी), and Gujarati (ગુજરાતી). Paste any news article to analyze its authenticity.", false);
    }, 500);

    // Function: Send News for Fake/Real Prediction
    function sendMessage() {
        const messageText = messageInput.value.trim();
        if (!messageText) {
            showNotification("Please enter news content.", "warning");
            return;
        }

        if (messageText.length < 10) {
            showNotification("Please enter at least 10 characters for accurate analysis.", "warning");
            return;
        }

        // Add user message
        addMessage(messageText, true);
        messageInput.value = "";

        // Show typing indicator
        showTypingIndicator();

        // Send data to Flask backend for Fake News Detection
        fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: messageText })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            removeTypingIndicator();
            
            if (data.error) {
                addMessage(`❌ Error: ${data.error}`, false);
                return;
            }
            
            // Add bot response with confidence, reliability, and language
            const confidence = data.confidence || 0;
            const emoji = data.prediction_en === 'Fake News' ? '🚫' : '✅';
            const reliability = data.reliability || 'Unknown';
            const reliabilityEmoji = reliability === 'High' || data.reliability_en === 'High' ? '⭐⭐⭐' : 
                                    reliability === 'Medium' || data.reliability_en === 'Medium' ? '⭐⭐' : '⭐';
            const confidenceBar = createConfidenceBar(confidence);
            
            // Language detection info
            const langInfo = data.language_name ? 
                `<div style="font-size: 12px; color: #8696a0; margin-top: 4px;">
                    🌐 Detected: ${data.language_name}
                </div>` : '';
            
            addMessage(
                `${emoji} <strong>${data.prediction}</strong><br>` +
                `Confidence: ${confidence}%<br>` +
                `Reliability: ${reliabilityEmoji} ${reliability}<br>` +
                confidenceBar +
                langInfo,
                false
            );
        })
        .catch(error => {
            console.error("Error:", error);
            removeTypingIndicator();
            addMessage("❌ Sorry, I couldn't analyze the news. Please try again.", false);
            showNotification("Analysis failed. Please try again.", "error");
        });
    }

    // Function: Add message to chat
    function addMessage(text, isUser) {
        const messageElement = document.createElement("div");
        messageElement.className = `message ${isUser ? 'sent' : 'received'}`;
        
        const timestamp = new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageElement.innerHTML = `
            <p>${text}</p>
            <span class="message-time">${timestamp}</span>
        `;
        
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // Function: Create confidence bar with animation
    function createConfidenceBar(confidence) {
        const color = confidence > 80 ? '#00ff00' : 
                     confidence > 70 ? '#7fff00' :
                     confidence > 60 ? '#ffaa00' : 
                     confidence > 50 ? '#ff8800' : '#ff4444';
        return `
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${confidence}%; background: ${color}; animation: fillBar 0.8s ease-out;"></div>
            </div>
        `;
    }

    // Function: Show notification
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Function: Show typing indicator
    function showTypingIndicator() {
        const typingElement = document.createElement("div");
        typingElement.className = "typing-indicator";
        typingElement.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        typingElement.id = "typingIndicator";
        messagesDiv.appendChild(typingElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // Function: Remove typing indicator
    function removeTypingIndicator() {
        const typingElement = document.getElementById("typingIndicator");
        if (typingElement) {
            typingElement.remove();
        }
    }

    // Function: Fetch Real-Time News Based on User Query
    function fetchNews() {
        let query = newsQueryInput.value.trim() || "latest";
        
        if (!query) {
            showNotification("Please enter a search topic.", "warning");
            return;
        }
        
        // Show loading state
        newsList.innerHTML = '<div class="loading"><div class="spinner"></div>Fetching news...</div>';
        
        fetch(`/fetch_news?query=${encodeURIComponent(query)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            newsList.innerHTML = "";

            if (data.error) {
                newsList.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }

            if (!data.news || data.news.length === 0) {
                newsList.innerHTML = '<div class="error">No news found for this topic.</div>';
                return;
            }

            // Add header
            const header = document.createElement("div");
            header.className = "news-header";
            header.innerHTML = `<strong>Found ${data.news.length} articles</strong>`;
            newsList.appendChild(header);

            data.news.forEach((article, index) => {
                const newsItem = document.createElement("div");
                newsItem.className = "news-item";
                const prediction = data.predictions[index];
                const isFake = prediction === 'Fake News';
                
                newsItem.innerHTML = `
                    <div class="news-number">${index + 1}</div>
                    <div class="news-content">
                        <p>${article}</p>
                    </div>
                    <div class="news-status ${isFake ? 'fake' : 'real'}">
                        ${isFake ? '🚫' : '✅'} ${prediction}
                    </div>
                `;
                
                // Add click to analyze
                newsItem.addEventListener('click', () => {
                    messageInput.value = article;
                    messageInput.focus();
                });
                
                newsList.appendChild(newsItem);
            });

            showNotification(`Analyzed ${data.news.length} articles`, "success");
        })
        .catch(error => {
            console.error("Error fetching news:", error);
            newsList.innerHTML = '<div class="error">Failed to fetch news. Please try again.</div>';
            showNotification("Failed to fetch news", "error");
        });
    }

    // Function: Handle File Attachment
    function handleAttach() {
        const fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.accept = "image/*,application/pdf";
        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                addMessage(`📎 ${file.name}`, true);
            }
        };
        fileInput.click();
    }

    // Function: Logout User
    function logout() {
        if (confirm("Are you sure you want to logout?")) {
            fetch('/logout', { method: 'POST' })
                .then(() => {
                    showNotification("Logged out successfully", "success");
                    setTimeout(() => {
                        window.location.href = "/";
                    }, 1000);
                })
                .catch(() => {
                    window.location.href = "/";
                });
        }
    }

    // Make functions accessible globally
    window.sendMessage = sendMessage;
    window.fetchNews = fetchNews;
    window.handleAttach = handleAttach;
    window.logout = logout;

    // Handle Enter key press for message input
    messageInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Handle Enter key press for news query
    newsQueryInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            fetchNews();
        }
    });

    // Auto-resize textarea
    messageInput.addEventListener("input", function() {
        this.style.height = "auto";
        this.style.height = (this.scrollHeight) + "px";
    });
});
