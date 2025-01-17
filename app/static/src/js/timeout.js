document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname === "/session-expired") {
      return; // Don't run the timeout logic if on the session expired page
  }

  const dialog = document.getElementById("timeout-dialog");
  const idleTimeout = parseInt(dialog.dataset.idleTimeout, 10) * 60 * 1000;
  const visibleTime = parseInt(dialog.dataset.visibleTime, 10) * 60 * 1000;
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

  // Extend session button
  const extendSession = () => {
      clearTimeout(timeoutId);
      clearInterval(visibleId);
      dialog.close();
      startIdleTimer(); // Restart the timer
  };

  const startIdleTimer = () => {
      timeoutId = setTimeout(showDialog, idleTimeout - visibleTime);
  };

    const updateTimeoutMessage = (remainingSeconds) => {
      const remainingTimeSpan = document.getElementById("remaining-time");

      const minutesLeft = Math.floor(remainingSeconds / 60); // Get full minutes
      const secondsLeft = remainingSeconds % 60; // Get remaining seconds

      // Update the display message based on the time left
      if (remainingTimeSpan) {
          if (minutesLeft > 0) {
              // Display minutes and seconds
              remainingTimeSpan.textContent = `${minutesLeft} minute${minutesLeft > 1 ? 's' : ''} and ${secondsLeft} second${secondsLeft !== 1 ? 's' : ''}`;
          } else {
              // Only display seconds when minutesLeft is 0
              remainingTimeSpan.textContent = `${secondsLeft} second${secondsLeft !== 1 ? 's' : ''}`;
          }
      }
  };

  // Event listeners
  dialog.querySelector(".js-extend-session").addEventListener("click", extendSession);
  window.addEventListener("scroll", resetIdleTimer);       // Resets timer on scroll
  window.addEventListener("mousemove", resetIdleTimer);    // Resets timer on mouse move
  window.addEventListener("mousedown", resetIdleTimer);    // Resets timer on mouse down (touchpad click)
  window.addEventListener("click", resetIdleTimer);        // Resets timer on click
  window.addEventListener("keydown", resetIdleTimer);      // Resets timer on key press
  window.addEventListener("keyup", resetIdleTimer);        // Resets timer on key release (useful for Android)

  startIdleTimer();
});
