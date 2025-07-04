from datetime import datetime

from flask.views import View, MethodView
from flask import session, url_for, redirect, render_template, request
from app.contact.forms.booking import BookingForm
from app.contact.forms.choose_an_option import OptionForm
from app.contact.forms.choose_time_slot import ChooseTimeSlotForm
from app.main.filters import format_callback_time_slot


class ContactView(View):
    forms = {
        "booking": BookingForm,
        "choose_an_option": OptionForm,
        "choose_time_slot": ChooseTimeSlotForm,
    }

    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def dispatch_request(self):
        contact_forms = session["contact"].forms
        form_data = contact_forms.get(self.current_name, {})
        form = self.form_class(formdata=request.form or None, data=form_data)

        if form.validate_on_submit():
            session["contact"].add(self.current_name, form.data)
            next_page = url_for(f"contact_us.{self.get_next_page(self.current_name)}")

            return redirect(next_page)

        return self.render_form(form)

    def render_form(self, form):
        template_vars = {"form": form}

        # Add calendar data for time slot form
        if hasattr(form, "get_calendar_data"):
            calendar_info = form.get_calendar_data()
            template_vars["calendar_data"] = calendar_info.get("calendar_data", {})
            template_vars["has_sunday_slots"] = calendar_info.get("has_sunday_slots", False)

        return render_template(self.form_class.template, **template_vars)

    def get_next_page(self, current_key):
        keys = list(self.forms.keys())  # Convert to list for easier indexing
        try:
            current_index = keys.index(current_key)
            # Look through remaining pages
            for next_key in keys[current_index + 1 :]:
                if self.forms[next_key].should_show():
                    return next_key
            return "review"  # No more valid pages found
        except ValueError:  # current_key not found
            return "review"


class CheckYourAnswersView(MethodView):
    def __init__(self, form_class):
        self.form_class = form_class

    def get(self):
        form = self.form_class()
        users_answers = []

        callback_time: datetime = session["contact"].callback_time
        if callback_time:
            day_name = callback_time.strftime("%a")  # Abbreviated weekday (Mon, Tue, Wed, etc.)
            date_part = callback_time.strftime("%-d %b")  # Day and abbreviated month (12 May)
            time_part = format_callback_time_slot(callback_time.strftime("%H:%M"))
            formatted_callback = f"We'll call you:<br>{day_name} {date_part}<br>between {time_part}"
            users_answers.append(
                {
                    "key": {"text": "Callback time"},
                    "value": {"html": formatted_callback},
                    "actions": {"items": [{"href": url_for("contact_us.choose_an_option"), "text": "Change"}]},
                }
            )

        return render_template(self.form_class.template, form=form, users_answers=users_answers)
