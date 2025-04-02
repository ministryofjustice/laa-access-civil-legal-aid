import logging
from flask import session, redirect, url_for

logger = logging.getLogger(__name__)


class InScopeMixin:
    def dispatch_request(self):
        response = self.ensure_in_scope()
        if not response:
            response = super().dispatch_request()

        return response

    def ensure_in_scope(self):
        if not session.in_scope:
            logger.info("FAILED ensuring in scope check")
            return redirect(url_for("main.session_expired"))

        return None
