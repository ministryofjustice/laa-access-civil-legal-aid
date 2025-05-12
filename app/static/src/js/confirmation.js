document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".confirmation-email-form");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const response = await fetch(window.location.href, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData,
        });

        const content = await response.json();

        const errorContainer = document.getElementById("email-error");
        const errorTextSpan = errorContainer.querySelector(".error-text");
        const formGroup = document.getElementById("email-form-group");
        const confirmationMessage = document.getElementById("confirmation-message");
        const confirmedEmail = document.getElementById("confirmed-email");

        // Get translated label from the hidden span
        const label = document.getElementById("email-sent-label")?.dataset.translate || "Your reference number was sent to";

        // Reset previous errors
        errorContainer.style.display = "none";
        errorTextSpan.textContent = "";
        formGroup.classList.remove("govuk-form-group--error");

        if (response.ok && content.success) {
            // Hide form after successful submission
            form.style.display = "none";

            // Update the confirmation message with the translated label
            confirmationMessage.innerHTML = `${label} <strong>${content.email}.</strong>`;
            confirmationMessage.style.display = "block";  // Ensure message is visible
        } else {
            const errorText = content.errors?.email?.[0];
            if (errorText) {
                formGroup.classList.add("govuk-form-group--error");
                errorTextSpan.textContent = errorText;
                errorContainer.style.display = "block";
            }
        }
    });
});
