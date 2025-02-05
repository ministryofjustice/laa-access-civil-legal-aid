fallback_page = "/session-expired"

document.addEventListener('DOMContentLoaded', () => {
    const backButton = document.getElementById('backLink');

    if (!backButton) {
        return;
    }
    
    backButton.addEventListener('click', (e) => {
        e.preventDefault();

        if (document.referrer === '') {
            window.location.href = fallback_page;
            return;
        }

        const referrerUrl = new URL(document.referrer);

        // Only go back if the previous page is from the same origin
        if (referrerUrl.origin !== window.location.origin) {
            window.location.href = fallback_page;
            return;
        }
        
        // Check if we can go back
        if (window.history.length > 1) {
            window.history.back();
        } else {
            window.location.href = fallback_page;
        }
    });
});