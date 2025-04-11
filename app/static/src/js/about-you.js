document.getElementById("has_partner-2").addEventListener("change", function() {
    const yesRadio = document.getElementById("in_dispute");
    const noRadio = document.getElementById("in_dispute-2");

    yesRadio.checked = false;
    noRadio.checked = false;

    // Trigger change event so data-controlled-by logic responds
    const event = new Event("change", { bubbles: false });
    yesRadio.dispatchEvent(event);
    noRadio.dispatchEvent(event);
});