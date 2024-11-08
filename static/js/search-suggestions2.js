// Get DOM elements
const inputField1 = document.getElementById('searchBox1');
const inputField = document.getElementById('searchBox20');
const suggestionContainer = document.getElementById('suggestions2');
const formWrapper = document.getElementById('lowerSearchBox');
let currentIndex = -1;
let dataCollection = []; // Store all data
let searchResults = []; // Store filtered results

// Function to shorten text to 48 characters
function shortenText(text) {
    if (text.length > 48) {
        return text.substring(0, 45) + '...';
    }
    return text;
}

// Function to search data
function searchInData(value) {
    if (!value) return [];
    const searchText = value.toLowerCase();
    return dataCollection.filter(item => 
        item.toLowerCase().includes(searchText)
    );
}

// Function to display suggestions
function displaySuggestions(value) {
    if (!value) {
        suggestionContainer.innerHTML = '';
        currentIndex = -1;
        return;
    }

    searchResults = searchInData(value);
    suggestionContainer.innerHTML = '';
    
    searchResults.forEach((item) => {
        const div = document.createElement('div');
        div.className = 'suggestedText';
        div.textContent = shortenText(item);
        
        // Add click event
        div.addEventListener('click', () => {
            inputField.value = item; // Use full text when clicking
            inputField1.value = item; 
            suggestionContainer.innerHTML = '';
            currentIndex = -1;
        });
        
        suggestionContainer.appendChild(div);
    });
}

// Fetch initial data when page loads
async function loadData() {
    try {
        const response = await fetch('http://127.0.0.1:8000/accounts/search-suggestions');
        dataCollection = await response.json();
    } catch (error) {
        console.error('Error fetching initial data:', error);
        dataCollection = []; // Set empty array if fetch fails
    }
}

// Add input event listener
inputField.addEventListener('input', (e) => {
    displaySuggestions(e.target.value);
});

// Prevent form submission on enter
formWrapper.querySelector('form').addEventListener('submit', (e) => {
    if (currentIndex >= 0 && searchResults.length > 0) {
        e.preventDefault();
    }
});

// Keyboard navigation
inputField.addEventListener('keydown', (e) => {
    const suggestions = suggestionContainer.getElementsByClassName('suggestedText');
    
    if (suggestions.length === 0) return;
    
    // Remove active class from current selection
    if (currentIndex >= 0 && currentIndex < suggestions.length) {
        suggestions[currentIndex].classList.remove('active');
    }
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            currentIndex++;
            if (currentIndex >= suggestions.length) currentIndex = 0;
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            currentIndex--;
            if (currentIndex < 0) currentIndex = suggestions.length - 1;
            break;
            
        case 'Enter':
            if (currentIndex >= 0 && currentIndex < suggestions.length) {
                e.preventDefault();
                inputField.value = searchResults[currentIndex];
                inputField1.value = searchResults[currentIndex];  // Use full text from filtered data
                suggestionContainer.innerHTML = '';
                currentIndex = -1;
            }
            break;
            
        case 'Escape':
            suggestionContainer.innerHTML = '';
            currentIndex = -1;
            break;
            
        default:
            return;
    }
    
    // Add active class to new selection
    if (currentIndex >= 0 && currentIndex < suggestions.length) {
        suggestions[currentIndex].classList.add('active');
        // Scroll suggestion into view if needed
        suggestions[currentIndex].scrollIntoView({ 
            behavior: 'auto',
            block: 'nearest'
        });
    }
});

// Close suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!formWrapper.contains(e.target)) {
        suggestionContainer.innerHTML = '';
        currentIndex = -1;
    }
});

// Initialize by fetching data when the page loads
loadData();
