// Get DOM elements
const inputBox = document.getElementById('authors');
const suggestionContainer = document.getElementById('sugesteditem2');
let activeIndex = -1;
let dataPool = []; // Store all data
let matchingResults = []; // Store filtered results

// Function to truncate text to 48 characters
function truncateText(content) {
    if (content.length > 48) {
        return content.substring(0, 45) + '...';
    }
    return content;
}

// Function to search and filter data
function searchResults(input) {
    if (!input) return [];
    const query = input.toLowerCase();
    return dataPool.filter(entry => 
        entry.toLowerCase().includes(query)
    );
}

// Function to display suggestions
function displaySuggestions(input) {
    if (!input) {
        suggestionContainer.innerHTML = '';
        activeIndex = -1;
        return;
    }

    matchingResults = searchResults(input);
    suggestionContainer.innerHTML = '';
    
    matchingResults.forEach((entry) => {
        const suggestionItem = document.createElement('div');
        suggestionItem.className = 'suggestedText2';
        suggestionItem.textContent = truncateText(entry);
        
        // Add click event
        suggestionItem.addEventListener('click', () => {
            inputBox.value = entry;
            suggestionContainer.innerHTML = '';
            activeIndex = -1;
        });
        
        suggestionContainer.appendChild(suggestionItem);
    });
}

// Fetch initial dataset when page loads
async function loadData() {
    try {
        const response = await fetch('http://127.0.0.1:8000/books/getAuthors/');
        dataPool = await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        dataPool = [];
    }
}

// Add input event listener
inputBox.addEventListener('input', (event) => {
    displaySuggestions(event.target.value);
});

// Handle keyboard navigation
inputBox.addEventListener('keydown', (event) => {
    const suggestionItems = suggestionContainer.getElementsByClassName('suggestedText2');
    
    if (suggestionItems.length === 0) return;
    
    // Remove active class from current selection
    if (activeIndex >= 0 && activeIndex < suggestionItems.length) {
        suggestionItems[activeIndex].classList.remove('active2');
    }
    
    switch (event.key) {
        case 'ArrowDown':
            event.preventDefault();
            activeIndex++;
            if (activeIndex >= suggestionItems.length) activeIndex = 0;
            break;
            
        case 'ArrowUp':
            event.preventDefault();
            activeIndex--;
            if (activeIndex < 0) activeIndex = suggestionItems.length - 1;
            break;
            
        case 'Enter':
            event.preventDefault();
            if (activeIndex >= 0 && activeIndex < suggestionItems.length) {
                inputBox.value = matchingResults[activeIndex];
                suggestionContainer.innerHTML = '';
                activeIndex = -1;
            }
            break;
            
        case 'Escape':
            suggestionContainer.innerHTML = '';
            activeIndex = -1;
            break;
            
        default:
            return;
    }
    
    // Add active class to new selection
    if (activeIndex >= 0 && activeIndex < suggestionItems.length) {
        suggestionItems[activeIndex].classList.add('active2');
        // Scroll suggestion into view if needed
        suggestionItems[activeIndex].scrollIntoView({ 
            behavior: 'auto',
            block: 'nearest'
        });
    }
});

// Close suggestions when clicking outside
document.addEventListener('click', (event) => {
    if (!inputBox.contains(event.target) && !suggestionContainer.contains(event.target)) {
        suggestionContainer.innerHTML = '';
        activeIndex = -1;
    }
});

// Add enhanced CSS for better visual feedback
const dynamicStyles = document.createElement('style');
dynamicStyles.textContent = `
    .suggestedText2.active2 {
        background-color: #dadada !important;
        color: #1a73e8;
    }
`;
document.head.appendChild(dynamicStyles);

// Load data when the page initializes
loadData();
