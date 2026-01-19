document.addEventListener("DOMContentLoaded", function () {
    const messagesDiv = document.getElementById("messages");
    const messageInput = document.getElementById("messageInput");
    const newsQueryInput = document.getElementById("newsQuery");
    const newsList = document.getElementById("newsList");

    // Function: Send News for Fake/Real Prediction
    function sendMessage() {
        const messageText = messageInput.value.trim();
        if (!messageText) {
            alert("Please enter news content.");
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
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator();
            // Add bot response
            addMessage(`Analysis Result: ${data.prediction}`, false);
        })
        .catch(error => {
            console.error("Error:", error);
            removeTypingIndicator();
            addMessage("❌ Sorry, I couldn't analyze the news. Please try again.", false);
        });
    }

    // Function: Add message to chat
    function addMessage(text, isUser) {
        const messageElement = document.createElement("div");
        messageElement.className = `message ${isUser ? 'sent' : 'received'}`;
        messageElement.innerHTML = `<p>${text}</p>`;
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
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
        
        // Show loading state
        newsList.innerHTML = '<div class="loading">Fetching news...</div>';
        
        fetch(`/fetch_news?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            newsList.innerHTML = "";

            data.news.forEach((article, index) => {
                const newsItem = document.createElement("div");
                newsItem.className = "news-item";
                newsItem.innerHTML = `
                    <div class="news-content">
                        <strong>${index + 1}.</strong> ${article}
                    </div>
                    <div class="news-status ${data.predictions[index] === 'Fake News' ? 'fake' : 'real'}">
                        ${data.predictions[index]}
                    </div>
                `;
                newsList.appendChild(newsItem);
            });
        })
        .catch(error => {
            console.error("Error fetching news:", error);
            newsList.innerHTML = '<div class="error">Failed to fetch news. Please try again.</div>';
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
        window.location.href = "/";
    }

    // Make functions accessible globally
    window.sendMessage = sendMessage;
    window.fetchNews = fetchNews;
    window.handleAttach = handleAttach;
    window.logout = logout;

    // Handle Enter key press
    messageInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
