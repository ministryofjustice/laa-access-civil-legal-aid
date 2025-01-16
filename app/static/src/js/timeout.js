
document.addEventListener("DOMContentLoaded", () => {
    const dialog = document.getElementById("timeout-dialog");
    const idleTimeout = parseInt(dialog.dataset.idleTimeout, 10) * 60; // Convert minutes to milliseconds
    const visibleTime = parseInt(dialog.dataset.visibleTime, 10) * 60; // Convert minutes to milliseconds
    const redirectUrl = dialog.dataset.redirectUrl;

    let timeoutId;
    let visibleId;

    const showDialog = () => {
        dialog.showModal();
        const accessibleTimer = document.getElementById("accessible-timer");
        let remainingSeconds = visibleTime / 1000;
    };

    const extendSession = () => {
        clearTimeout(timeoutId);
        clearInterval(visibleId);
        dialog.close();
      startIdleTimer(); // Restart the timer
    };

    const startIdleTimer = () => {
        timeoutId = setTimeout(showDialog, idleTimeout - visibleTime);
    };

    // Event listeners
    dialog.querySelector(".js-extend-session").addEventListener("click", extendSession);

    // Start the idle timer
    startIdleTimer();
  });