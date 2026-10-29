import secrets
import string
import threading
import time
from datetime import datetime

from flask import jsonify, request

from models.database.redirect import Redirect
from web import WebManager

web = WebManager()

_RETRIES_PER_IPS = {}
_MAX_RETRIES_PER_IP = 5
_MAX_RETRY_TIMEOUT_IN_SECONDS = 60


def __generate_new_tag():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(Redirect.MAXIMUM_TAG_LENGTH))


def __clear_visitor_retries(visitor_address: str):
    time.sleep(_MAX_RETRY_TIMEOUT_IN_SECONDS)
    _RETRIES_PER_IPS[visitor_address] = 0


@web.route("/add_redirect", methods=["POST"])
def on_redirect_added():
    visitor_retries = _RETRIES_PER_IPS.get(request.remote_addr)
    max_allowed_retries_per_check = _MAX_RETRIES_PER_IP - 1
    if visitor_retries and (visitor_retries >= max_allowed_retries_per_check):
        if visitor_retries == max_allowed_retries_per_check:
            # Users will be limited to a certain amount of retries per minute
            _RETRIES_PER_IPS[request.remote_addr] = visitor_retries + 1
            threading.Thread(target=__clear_visitor_retries, args=(request.remote_addr,)).start()
        return jsonify({"status": "error", "message": "Quota exceeded. Please try again in a few minutes."}), 403
    date_added = datetime.now()
    assigned_tag = __generate_new_tag()
    reference = WebManager.get_param_and_sanitize("reference")
    new_redirect = Redirect(date_added=date_added, assigned_tag=assigned_tag, reference=reference)
    if not web.add_and_commit(new_redirect):
        return jsonify({"status": "error", "message": "There is an error adding the requested link. Please try again."}), 500
    # Successfully generating the tag and saving the attempt
    if visitor_retries:
        _RETRIES_PER_IPS[request.remote_addr] = visitor_retries + 1
    else:
        _RETRIES_PER_IPS[request.remote_addr] = 1
    return jsonify({"status": "success", "assigned_tag": f"https://lty.ie/{assigned_tag}"})
