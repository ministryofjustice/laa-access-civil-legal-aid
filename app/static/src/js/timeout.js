document.addEventListener("DOMContentLoaded", () => {
  // Check if we're on the /session-expired page
  if (window.location.pathname === "/session-expired") {
      return; // Don't run the timeout logic if we're on the session expired page
  }

  const dialog = document.getElementById("timeout-dialog");
  const idleTimeout = parseInt(dialog.dataset.idleTimeout, 10) * 600; // Convert minutes to milliseconds
  const visibleTime = parseInt(dialog.dataset.visibleTime, 10) * 600; // Convert minutes to milliseconds
  const redirectUrl = dialog.dataset.redirectUrl;

  let timeoutId;
  let visibleId;

  // Function to reset the idle timer
  const resetIdleTimer = () => {
      // Only reset if the dialog is not currently showing
      if (!dialog.open) {
          clearTimeout(timeoutId);
          clearInterval(visibleId);
          startIdleTimer(); // Restart the idle timer whenever there's user activity (unless dialog is open)
      }
  };

  // Show the session timeout dialog
  const showDialog = () => {
      dialog.showModal();
      updateTimeoutMessage(visibleTime / 1000); // Start updating the timeout message
      let remainingSeconds = visibleTime / 1000;

      visibleId = setInterval(() => {
          remainingSeconds -= 1;
          updateTimeoutMessage(remainingSeconds); // Update minutes and seconds on each interval

          if (remainingSeconds <= 0) {
              clearInterval(visibleId);
              window.location.href = redirectUrl; // Redirect when time is up
          }
      }, 1000);
  };

  // Extend the session when the user clicks on the extend session button
  const extendSession = () => {
      clearTimeout(timeoutId);
      clearInterval(visibleId);
      dialog.close();
      startIdleTimer(); // Restart the timer
  };

  // Start the idle timer
  const startIdleTimer = () => {
      timeoutId = setTimeout(showDialog, idleTimeout - visibleTime);
  };

  // Update the timeout message with remaining time in MM:SS format
  const updateTimeoutMessage = (remainingSeconds) => {
      const remainingMinutesSpan = document.getElementById("remaining-minutes");
      const remainingSecondsSpan = document.getElementById("remaining-seconds");

      const minutesLeft = Math.floor(remainingSeconds / 60); // Get full minutes
      const secondsLeft = remainingSeconds % 60; // Get remaining seconds

      // Update the display in "MM:SS" format
      if (remainingMinutesSpan) {
          remainingMinutesSpan.textContent = minutesLeft;
      }
      if (remainingSecondsSpan) {
          // Format seconds to always show two digits (e.g., 09 instead of 9)
          remainingSecondsSpan.textContent = secondsLeft < 10 ? `0${secondsLeft}` : secondsLeft;
      }
  };

  // Event listeners
  dialog.querySelector(".js-extend-session").addEventListener("click", extendSession);

  // Listen for scroll events and reset the idle timer when the user scrolls
  window.addEventListener("scroll", resetIdleTimer);

  // Start the idle timer
  startIdleTimer();
});