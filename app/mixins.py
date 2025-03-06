from flask import session, url_for, redirect


class InScopeMixin:
    def dispatch_request(self):
        self.ensure_in_scope()

    def ensure_in_scope(self):
        if not session.in_scope:
            return redirect(url_for("main.session_expired"))
        return super().dispatch_request()
