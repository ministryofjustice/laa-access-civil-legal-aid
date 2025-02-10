const FALLBACK_PAGE = "/session-expired"

document.addEventListener('DOMContentLoaded', () => {
    const backButton = document.getElementById('backLink');

    if (!backButton) {
        return;
    }
    
    backButton.addEventListener('click', (e) => {
        e.preventDefault();

        try {
            const referrerUrl = new URL(document.referrer);

            // Only go back if the previous page is from the same origin
            if (referrerUrl.origin !== window.location.origin) {
                window.location.href = FALLBACK_PAGE;
                return;
            }

        } catch (error) {
            window.location.href = FALLBACK_PAGE;
            return;
        }

        if (window.history.length <= 1) {
            window.location.href = FALLBACK_PAGE;
            return;
        }
        window.history.back();
    });
});
