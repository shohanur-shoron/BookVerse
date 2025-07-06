const chatMessagesContainer = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('prompt');
const sendButton = document.getElementById('send-button');
const initialGreeting = document.querySelector('.initial-greeting'); // May not be relevant on this page
const startingPromptElement = document.getElementById('starting-prompt'); // <--- Added selector
const backButton = document.getElementById('back-button');
const profilePicture = document.getElementById('profile-picture'); // For side menu
const sideMenu = document.getElementById('sideMenu');             // For side menu
const sideMenuCover = document.getElementById('sideMenuCover');   // For side menu
const closeBtn = document.getElementById('closeBtn');             // For side menu


// --- State ---
let isFirstUserMessage = true; // Flag to track if it's the first *user-typed* message

// --- UI Update Functions ---

/**
 * Adds a message bubble to the chat.
 * @param {string} text - The message text (can be empty for loading state).
 * @param {'user' | 'bot' | 'error'} sender - The sender type.
 * @param {string | null} elementId - Optional ID for the message element.
 * @returns {HTMLElement} The created message element.
 */
function addMessage(text, sender, elementId = null) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    if (elementId) {
        messageElement.id = elementId;
    }

    // Handle initial content (use marked for bot, plain text otherwise)
    if (sender === 'bot' && text && typeof marked !== 'undefined') {
         if (elementId && elementId.startsWith('bot-message-') || elementId && elementId.startsWith('initial-bot-message-')) {
            // It's a loading or error message, set text directly first
            messageElement.textContent = text;
         } else {
             messageElement.innerHTML = marked.parse(text); // Parse regular bot messages
         }
    } else {
        // Basic text content for user, error, or initial bot message before parsing
        messageElement.textContent = text;
    }

    // Special handling for the static book cover image in the user message
    if (sender === 'user' && elementId === 'initial-user-message-visual') {
        // Clear text content if we are adding the image structure
        messageElement.textContent = '';
        const img = document.createElement('img');
        img.classList.add('book-cover-gemini'); // Use the same class as in HTML
        // You might need to get the actual book cover URL from Django context
        // For now, using the placeholder from the HTML example:
        img.src = "{% static 'images/no_book_cover.jpg' %}"; // Adjust path if needed
        img.alt = "Book Cover";
        messageElement.appendChild(img);

        const textDiv = document.createElement('div');
        textDiv.textContent = "Tell me more about this book."; // The static text
        messageElement.appendChild(textDiv);
    }


    chatMessagesContainer.appendChild(messageElement);
    scrollToBottom(); // Scroll after adding ANY message
    return messageElement;
}

/**
 * Adds a bot message bubble specifically for the loading state.
 * @param {string} elementId - The ID to assign to the loading message element.
 * @returns {HTMLElement} The created loading message element.
 */
function showLoadingIndicator(elementId) {
    const loadingElement = addMessage('', 'bot', elementId); // Start with empty content
    loadingElement.classList.add('loading-state'); // Add class for styling
    loadingElement.innerHTML = '<span class="loading-text">Generating response...</span>';
    return loadingElement;
}

/**
 * Updates the content of an existing bot message bubble, parsing Markdown.
 * @param {HTMLElement} element - The message element to update.
 * @param {string} fullHtmlContent - The full HTML content (already parsed).
 * @param {boolean} isFirstChunk - Flag indicating if this is the first chunk of real data.
 */
function updateBotMessageContent(element, fullHtmlContent, isFirstChunk) {
    if (isFirstChunk) {
        element.classList.remove('loading-state');
        element.textContent = ''; // Clear previous content (like "Generating response...")
    }
    element.innerHTML = fullHtmlContent; // Update/set the main content

    // Apply Syntax Highlighting using highlight.js (hljs)
    if (typeof hljs !== 'undefined') {
        const codeBlocks = element.querySelectorAll('pre code');
        codeBlocks.forEach((block) => {
            hljs.highlightElement(block);
            // console.log("Applied highlighting to code block:", block);
        });
    } else {
        console.warn("highlight.js (hljs) not loaded, cannot apply syntax highlighting.");
    }
    scrollToBottom(); // Keep scrolled down as content streams
}

/**
 * Updates a message bubble to show an error state.
 * @param {HTMLElement} element - The message element (likely the loading one).
 * @param {string} errorText - The error message to display.
 */
function showStreamError(element, errorText) {
     element.classList.remove('loading-state', 'bot');
     element.classList.add('error');
     element.innerHTML = ''; // Clear any potential loading HTML
     element.textContent = `Error: ${errorText}`;
     scrollToBottom();
}

/**
 * Handles UI changes needed when the stream completes successfully.
 * Re-enables input and sets focus.
 * @param {HTMLElement} element - The final bot message element.
 */
function handleStreamCompletion(element) {
    // Optional: element.classList.add('finished');
    setSendButtonState(true); // Re-enable button and input
    userInput.focus();        // Set focus back to input field
}

/**
 * Scrolls the chat container to the bottom smoothly.
 */
function scrollToBottom() {
    setTimeout(() => {
        chatMessagesContainer.scrollTo({
            top: chatMessagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 50); // Small delay helps ensure DOM is updated
}

/**
 * Enables or disables the send button and user input.
 * @param {boolean} enabled - True to enable, false to disable.
 */
function setSendButtonState(enabled) {
    sendButton.disabled = !enabled;
    userInput.disabled = !enabled; // Also disable/enable the input field
    // No focus change here, handled by completion/initial load
}

// --- Side Menu Logic ---
const closeSidePanel = () => {
    if (sideMenu && sideMenuCover) {
        sideMenu.style.transform = 'translateX(100%)'; // Adjust if needed based on CSS
        sideMenuCover.style.display = 'none';
        sideMenuCover.style.opacity = '0';
        // Re-enable body scroll if it was disabled
        document.body.style.overflow = '';
    }
};

const openSidePanel = () => {
    if (sideMenu && sideMenuCover) {
        sideMenu.style.transform = 'translateX(0)';
        sideMenuCover.style.display = 'block';
        sideMenuCover.style.opacity = '1';
        // Optionally disable body scroll
        document.body.style.overflow = 'hidden';
    }
};

// --- Event Listeners ---

// Handles USER-INITIATED messages AFTER the page loads and initial message
chatForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const userMessage = userInput.value.trim();
    if (!userMessage || sendButton.disabled) return; // Don't submit if empty or disabled

    // Hide initial greeting (might not exist on this page, but safe check)
    if (isFirstUserMessage && initialGreeting) {
        initialGreeting.classList.add('hidden');
        isFirstUserMessage = false;
    }

    // 1. Add user message to UI
    addMessage(userMessage, 'user');
    const promptValue = userInput.value; // Grab value *before* clearing
    userInput.value = '';
    setSendButtonState(false); // Disable input during processing

    // 2. Show loading indicator for bot response
    const botMessageId = `bot-message-${Date.now()}`;
    const loadingElement = showLoadingIndicator(botMessageId);

    // 3. Call the API function (defined in gemini2.js or similar)
    // Ensure `streamChatResponse` is globally available (e.g., window.streamChatResponse)
    if (typeof streamChatResponse === 'function') {
        streamChatResponse(promptValue, loadingElement, {
            onData: updateBotMessageContent,
            onError: showStreamError,
            onComplete: handleStreamCompletion // Re-enables input on completion
        });
    } else {
        console.error("streamChatResponse function not found!");
        showStreamError(loadingElement, "Chat functionality is unavailable.");
        setSendButtonState(true); // Re-enable if function is missing
    }
});

// Optional: Enter key submission
userInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit(); // Trigger form submit event
    }
});

// Back button navigation
if (backButton) {
    backButton.addEventListener('click', () => {
        window.history.back(); // Navigate to the previous page
    });
}

// Side Menu triggers
if (closeBtn) closeBtn.addEventListener('click', closeSidePanel);
if (sideMenuCover) sideMenuCover.addEventListener('click', closeSidePanel);
if (profilePicture) profilePicture.addEventListener('click', openSidePanel);


// --- Initial Page Load Logic ---
document.addEventListener('DOMContentLoaded', () => {
    // Don't focus initially, wait for first response or error
    // userInput.focus();

    // --- Automatic initial prompt handling ---
    if (startingPromptElement) {
        const startingPromptText = startingPromptElement.textContent?.trim();

        if (startingPromptText) {
            console.log("Found starting prompt:", startingPromptText);

            // The initial user message (cover + text) is already in the HTML.
            // We don't need addMessage for the *user's* first turn.

            // Show loading indicator for the *bot's* response immediately
            const initialBotMessageId = `initial-bot-message-${Date.now()}`;
            const loadingElement = showLoadingIndicator(initialBotMessageId);
            setSendButtonState(false); // Disable input while loading initial response

            console.log("Calling streamChatResponse for initial prompt...");
            // Call the API with the hidden prompt
            if (typeof streamChatResponse === 'function') {
                streamChatResponse(startingPromptText, loadingElement, {
                    onData: updateBotMessageContent,
                    onError: (element, errorText) => {
                        showStreamError(element, errorText);
                        handleStreamCompletion(element); // Still run completion to re-enable UI
                    },
                    onComplete: (element) => {
                        handleStreamCompletion(element); // Re-enables input/button and sets focus
                        console.log("Initial prompt processing complete.");
                    }
                });
            } else {
                 console.error("streamChatResponse function not found for initial call!");
                 showStreamError(loadingElement, "Chat functionality is unavailable.");
                 setSendButtonState(true); // Re-enable if function missing
            }

        } else {
            console.warn("Starting prompt element found, but it is empty.");
            // Enable input if there's no automatic prompt to run
            setSendButtonState(true);
            userInput.focus(); // Focus if no initial load
        }
    } else {
        console.warn("Starting prompt element (#starting-prompt) not found.");
        // Enable input if the element is missing
        setSendButtonState(true);
        userInput.focus(); // Focus if no initial load
    }


});
