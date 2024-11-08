// Get DOM elements
const searchBox = document.getElementById('searchBox1');
const searchBox20 = document.getElementById('searchBox20');
const suggestionsBox = document.getElementById('suggestions');
let currentFocus = -1;
let allData = []; // Store all data
let filteredData = []; // Store filtered results

// Function to trim text to 48 characters
function trimText(text) {
    if (text.length > 48) {
        return text.substring(0, 45) + '...';
    }
    return text;
}

// Function to filter data
function filterData(value) {
    if (!value) return [];
    const searchTerm = value.toLowerCase();
    return allData.filter(item => 
        item.toLowerCase().includes(searchTerm)
    );
}

// Function to show suggestions
function showSuggestions(value) {
    if (!value) {
        suggestionsBox.innerHTML = '';
        currentFocus = -1;
        return;
    }

    filteredData = filterData(value);
    suggestionsBox.innerHTML = '';
    
    filteredData.forEach((item) => {
        const div = document.createElement('div');
        div.className = 'suggestedText';
        div.textContent = trimText(item);
        
        // Add click event
        div.addEventListener('click', () => {
            searchBox.value = item;
            searchBox20.value = item; // Use full text when clicking
            suggestionsBox.innerHTML = '';
            currentFocus = -1;
        });
        
        suggestionsBox.appendChild(div);
    });
}

// Fetch initial data when page loads
async function fetchInitialData() {
    try {
        const response = await fetch('http://127.0.0.1:8000/accounts/search-suggestions');
        allData = await response.json();
    } catch (error) {
        console.error('Error fetching initial data:', error);
        allData = []; // Set empty array if fetch fails
    }
}

// Add input event listener
searchBox.addEventListener('input', (e) => {
    showSuggestions(e.target.value);
});

// Keyboard navigation
searchBox.addEventListener('keydown', (e) => {
    const suggestions = suggestionsBox.getElementsByClassName('suggestedText');
    
    if (suggestions.length === 0) return;
    
    // Remove active class from current selection
    if (currentFocus >= 0 && currentFocus < suggestions.length) {
        suggestions[currentFocus].classList.remove('active');
    }
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            currentFocus++;
            if (currentFocus >= suggestions.length) currentFocus = 0;
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            currentFocus--;
            if (currentFocus < 0) currentFocus = suggestions.length - 1;
            break;
            
        case 'Enter':
            e.preventDefault();
            if (currentFocus >= 0 && currentFocus < suggestions.length) {
                searchBox.value = filteredData[currentFocus];
                searchBox20.value = filteredData[currentFocus]; // Use full text from filtered data
                suggestionsBox.innerHTML = '';
                currentFocus = -1;
            }
            break;
            
        case 'Escape':
            suggestionsBox.innerHTML = '';
            currentFocus = -1;
            break;
            
        default:
            return;
    }
    
    // Add active class to new selection
    if (currentFocus >= 0 && currentFocus < suggestions.length) {
        suggestions[currentFocus].classList.add('active');
        // Scroll suggestion into view if needed
        suggestions[currentFocus].scrollIntoView({ 
            behavior: 'auto',
            block: 'nearest'
        });
    }
});

// Close suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!searchBox.contains(e.target) && !suggestionsBox.contains(e.target)) {
        suggestionsBox.innerHTML = '';
        currentFocus = -1;
    }
});

// Add enhanced CSS for better visual feedback
const style = document.createElement('style');
style.textContent = `
    .suggestedText.active {
        background-color: #71BF39 !important;
        color: #1a73e8;
    }
`;
document.head.appendChild(style);

// Initialize by fetching data when the page loads
fetchInitialData();