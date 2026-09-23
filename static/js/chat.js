/**
 * TourAI Chatbot Client-Side Logic.
 * Handles async fetch to POST /api/chat, rendering messages, tour cards, and loading states.
 */

document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const messagesContainer = document.getElementById("chat-messages");
    const promptChips = document.querySelectorAll(".prompt-chip");

    // Auto-scroll to bottom of messages container
    const scrollToBottom = () => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    // Format currency VND
    const formatVND = (num) => {
        try {
            return Number(num).toLocaleString("vi-VN") + " ₫";
        } catch (e) {
            return num + " VNĐ";
        }
    };

    // Basic markdown formatter (bold, line breaks)
    const formatText = (text) => {
        if (!text) return "";
        let formatted = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Bold: **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

        // Bullet points: * or -
        formatted = formatted.replace(/(?:^|\n)[*-]\s+(.*)/g, "<br>• $1");

        // Line breaks
        formatted = formatted.replace(/\n/g, "<br>");
        return formatted;
    };

    // Append a message bubble to chat
    const appendMessage = (sender, content, tours = []) => {
        const row = document.createElement("div");
        row.className = `message-row ${sender}`;

        const avatar = document.createElement("div");
        avatar.className = "msg-avatar";
        avatar.innerHTML = sender === "bot" ? "🤖" : "👤";

        const bubble = document.createElement("div");
        bubble.className = "msg-bubble";
        bubble.innerHTML = `<p>${formatText(content)}</p>`;

        // If bot returned tour products, render Product Cards
        if (sender === "bot" && Array.isArray(tours) && tours.length > 0) {
            const cardsContainer = document.createElement("div");
            cardsContainer.className = "chat-tour-cards";

            tours.forEach(tour => {
                const card = document.createElement("div");
                card.className = "chat-tour-card";

                const thumb = tour.image_url || "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=400&q=80";
                const nextDate = tour.next_departure ? `Khởi hành: ${tour.next_departure}` : "";
                const seats = tour.total_available_seats !== undefined ? ` (Còn ${tour.total_available_seats} chỗ)` : "";

                card.innerHTML = `
                    <img src="${thumb}" alt="${tour.title}" class="chat-card-thumb" loading="lazy">
                    <div class="chat-card-content">
                        <div class="chat-card-title">${tour.title}</div>
                        <div class="chat-card-meta">
                            📍 ${tour.destination_name || "Việt Nam"} • ⏱️ ${tour.duration_days || 1}N${tour.duration_nights || 0}Đ<br>
                            ${nextDate}${seats}
                        </div>
                        <div class="chat-card-price">${formatVND(tour.base_price)}</div>
                        <a href="/tours/${tour.slug}" class="chat-card-btn" target="_blank">Xem chi tiết & Đặt</a>
                    </div>
                `;
                cardsContainer.appendChild(card);
            });

            bubble.appendChild(cardsContainer);
        }

        row.appendChild(avatar);
        row.appendChild(bubble);
        messagesContainer.appendChild(row);
        scrollToBottom();
    };

    // Show typing/loading indicator
    const showTypingIndicator = () => {
        const indicator = document.createElement("div");
        indicator.className = "message-row bot typing-indicator-row";
        indicator.id = "bot-typing";

        indicator.innerHTML = `
            <div class="msg-avatar">🤖</div>
            <div class="msg-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        messagesContainer.appendChild(indicator);
        scrollToBottom();
    };

    // Remove typing indicator
    const removeTypingIndicator = () => {
        const indicator = document.getElementById("bot-typing");
        if (indicator) {
            indicator.remove();
        }
    };

    // Send query to backend API
    const handleSend = async (question) => {
        const cleanQuestion = question.trim();
        if (!cleanQuestion) return;

        // Display user message
        appendMessage("user", cleanQuestion);
        chatInput.value = "";
        chatInput.disabled = true;
        sendBtn.disabled = true;

        showTypingIndicator();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ question: cleanQuestion })
            });

            const data = await response.json();
            removeTypingIndicator();

            if (response.ok && data.answer) {
                appendMessage("bot", data.answer, data.tours || []);
            } else {
                appendMessage("bot", data.error || "Rất tiếc, đã xảy ra lỗi trong khi xử lý câu hỏi. Bạn vui lòng thử lại sau nhé!");
            }
        } catch (error) {
            removeTypingIndicator();
            appendMessage("bot", "Không thể kết nối với máy chủ. Vui lòng kiểm tra kết nối mạng của bạn!");
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
            scrollToBottom();
        }
    };

    // Form submission
    if (chatForm) {
        chatForm.addEventListener("submit", (e) => {
            e.preventDefault();
            handleSend(chatInput.value);
        });
    }

    // Quick prompt chip click
    promptChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const promptText = chip.getAttribute("data-prompt") || chip.textContent.trim();
            handleSend(promptText);
        });
    });
});

