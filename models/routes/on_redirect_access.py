from flask.templating import render_template

from models.database.redirect import Redirect
from web import WebManager

web = WebManager()


@web.route("/<path:path>", methods=["GET"])
def on_redirect_access(path):
    matched_redirect = web.query(Redirect, assigned_tag=path)
    if not matched_redirect:
        return render_template("misc/error.html", message="The short link you tried to open doesn’t exist or was typed incorrectly.")
    return render_template("loading.html", reference=matched_redirect[0].reference)
