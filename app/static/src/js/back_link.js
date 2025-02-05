document.addEventListener('DOMContentLoaded', () => {
    const backButton = document.getElementById('backLink');
    
    backButton.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Check if we can go back
        if (window.history.length > 1) {
            window.history.back();
        } else {
            // Fallback to homepage if no history
            window.location.href = '/';
        }
    });
});