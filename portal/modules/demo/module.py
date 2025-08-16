from flask import Blueprint, render_template

META = {
    "label": "Demo",
    "description": "Example module blueprint to show auto-discovery.",
    "icon": "flask",
}

blueprint = Blueprint("demo", __name__, template_folder="templates")

@blueprint.route("/")
def index():
    return render_template("modules/demo/index.html", title="Demo Module")
