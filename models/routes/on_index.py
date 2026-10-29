from flask.templating import render_template

from web import WebManager

web = WebManager()


@web.route("/", methods=["GET"])
def on_index():
    return render_template("index.html", reference="https://leatyon.org")
