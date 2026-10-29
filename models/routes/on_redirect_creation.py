from flask.templating import render_template

from web import WebManager

web = WebManager()


@web.route("/create", methods=["GET"])
def on_redirect_creation():
    return render_template("create.html")
