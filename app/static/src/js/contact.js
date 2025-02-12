
document.addEventListener("DOMContentLoaded", function () {
    let daySelect = document.getElementById("call_another_day");
    let timeSelect = document.getElementById("call_another_time");
    let timeSlotsData = JSON.parse(daySelect.dataset.timeSlots);

    daySelect.addEventListener("change", function () {
        let selectedDay = daySelect.value;

        timeSelect.innerHTML = '<option value="">Select time:</option>';

        let times = timeSlotsData[selectedDay];

        if (times) {
            for (let time in times) {
                let option = document.createElement("option");
                option.value = times[time][0];
                option.text = times[time][1];
                timeSelect.appendChild(option);
            }
        }
    });

});
