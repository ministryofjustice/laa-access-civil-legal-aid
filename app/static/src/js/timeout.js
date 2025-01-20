document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname === "/session-expired") {
      return;
  }

  const dialog = document.getElementById("timeout-dialog");
  const idleTimeout = parseInt(dialog.dataset.idleTimeout, 10) * 60 * 1000;
  const visibleTime = parseInt(dialog.dataset.visibleTime, 10) * 60 * 1000;
  const redirectUrl = dialog.dataset.redirectUrl;

  let checkIntervalId;
  let lastActivityTime = Date.now();
  let dialogShowTime = null;

  const resetIdleTimer = () => {
      if (!dialog.open) {
          lastActivityTime = Date.now();
      }
  };

  const showDialog = () => {
      dialog.showModal();
      dialogShowTime = Date.now();
      updateTimeoutMessage();
  };

  const extendSession = () => {
      dialog.close();
      dialogShowTime = null;
      lastActivityTime = Date.now();
  };

  const checkTime = () => {
      const now = Date.now();

      if (dialog.open) {
          // Check if we should redirect
          if (now - dialogShowTime >= visibleTime) {
              clearInterval(checkIntervalId);
              window.location.href = redirectUrl;
          } else {
              updateTimeoutMessage();
          }
      } else {
          // Check if we should show dialog
          if (now - lastActivityTime >= (idleTimeout - visibleTime)) {
              showDialog();
          }
      }
  };

  const updateTimeoutMessage = () => {
      const remainingTimeSpan = document.getElementById("remaining-time");
      if (!remainingTimeSpan) return;

      const now = Date.now();
      const remainingMilliseconds = visibleTime - (now - dialogShowTime);
      const remainingSeconds = Math.ceil(remainingMilliseconds / 1000);

      if (remainingSeconds <= 0) return;

      const minutesLeft = Math.floor(remainingSeconds / 60);
      const secondsLeft = remainingSeconds % 60;

      if (minutesLeft > 0) {
          remainingTimeSpan.textContent = `${minutesLeft} minute${minutesLeft > 1 ? 's' : ''} and ${secondsLeft} second${secondsLeft !== 1 ? 's' : ''}`;
      } else {
          remainingTimeSpan.textContent = `${secondsLeft} second${secondsLeft !== 1 ? 's' : ''}`;
      }
  };

  // Event listeners
  dialog.querySelector(".js-extend-session").addEventListener("click", extendSession);
  window.addEventListener("scroll", resetIdleTimer);
  window.addEventListener("mousemove", resetIdleTimer);
  window.addEventListener("mousedown", resetIdleTimer);
  window.addEventListener("click", resetIdleTimer);
  window.addEventListener("keydown", resetIdleTimer);
  window.addEventListener("keyup", resetIdleTimer);

  // Start checking time every second
  checkIntervalId = setInterval(checkTime, 1000);
  lastActivityTime = Date.now();
});