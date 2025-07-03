(function() {
  'use strict';
  
  const calendarDayClass = 'visits-calendar__day';
  const calendarDaySelectedClass = 'visits-calendar__day--selected';
  const calendarDayGroupClass = 'visits-calendar__day-group';
  const calendarDayGroupActiveClass = 'visits-calendar__day-group--active';

  function handleSelectDate(event) {
    event.preventDefault();
    const clickedElement = event.target.closest('a');
    const dayElement = clickedElement.closest(`.${calendarDayClass}`);
    const dateToShow = dayElement.dataset.date;

    // Remove previous selections
    const previousSelected = document.querySelector(`.${calendarDaySelectedClass}`);
    if (previousSelected) {
      previousSelected.classList.remove(calendarDaySelectedClass);
    }

    const previousActiveGroup = document.querySelector(`.${calendarDayGroupActiveClass}`);
    if (previousActiveGroup) {
      previousActiveGroup.classList.remove(calendarDayGroupActiveClass);
      previousActiveGroup.style.display = 'none';
    }

    // Add new selections
    dayElement.classList.add(calendarDaySelectedClass);

    const selectedFormGroup = document.getElementById('day-group-' + dateToShow);
    if (selectedFormGroup) {
      selectedFormGroup.classList.add(calendarDayGroupActiveClass);
      selectedFormGroup.style.display = 'block';

      // Focus on first radio button in the group
      const firstRadio = selectedFormGroup.querySelector('input[type="radio"]');
      if (firstRadio) {
        // Check if the first radio button is not in viewport
        const rect = firstRadio.getBoundingClientRect();
        const isInViewport = rect.top >= 0 && rect.bottom <= window.innerHeight;
        
        if (!isInViewport) {
          selectedFormGroup.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        // Small delay to ensure scroll completes before focusing
        setTimeout(() => {
          firstRadio.focus();
        }, 300);
      }
    }
  }

  function initializeCalendar() {
    if (!document.body.classList.contains('govuk-frontend-supported')) {
      return;
    }

    // Handle clicks on calendar days
    document.querySelectorAll(`.${calendarDayClass} a`).forEach(dayLink => {
      dayLink.addEventListener('click', handleSelectDate);
    });

    // Set default selected day on load if there's a pre-selected value
    const checkedRadio = document.querySelector('.visits-calendar input[type="radio"]:checked');
    if (checkedRadio) {
      const dateValue = checkedRadio.value.split('_')[0]; // Extract date from "YYYY-MM-DD_HH:MM" format
      const dayElement = document.querySelector(`.${calendarDayClass}[data-date="${dateValue}"]`);
      const dayGroup = document.getElementById('day-group-' + dateValue);
      
      if (dayElement && dayGroup) {
        dayElement.classList.add(calendarDaySelectedClass);
        dayGroup.classList.add(calendarDayGroupActiveClass);
        dayGroup.style.display = 'block';
      }
    }

    // Handle keyboard navigation
    document.querySelectorAll(`.${calendarDayClass} a`).forEach(dayLink => {
      dayLink.addEventListener('keydown', function(event) {
        // Handle Enter key
        if (event.key === 'Enter') {
          event.preventDefault();
          handleSelectDate(event);
        }
      });
    });

    // Handle radio button changes to update calendar selection
    document.querySelectorAll('.visits-calendar input[type="radio"]').forEach(radio => {
      radio.addEventListener('change', function() {
        if (this.checked) {
          const dateValue = this.value.split('_')[0];
          const dayElement = document.querySelector(`.${calendarDayClass}[data-date="${dateValue}"]`);
          
          // Remove previous calendar selection
          const previousSelected = document.querySelector(`.${calendarDaySelectedClass}`);
          if (previousSelected) {
            previousSelected.classList.remove(calendarDaySelectedClass);
          }
          
          // Add calendar selection for current radio
          if (dayElement) {
            dayElement.classList.add(calendarDaySelectedClass);
          }
        }
      });
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCalendar);
  } else {
    initializeCalendar();
  }
})();