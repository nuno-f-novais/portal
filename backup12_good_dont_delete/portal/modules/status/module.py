from flask import Blueprint, render_template, current_app, request
import platform, os, time

META = {
    "internal": False,
    "label": "Status",
    "description": "Lightweight system & app health page.",
    "icon": "activity",
}

blueprint = Blueprint("status", __name__, template_folder="templates")

@blueprint.route("/")
def index():
    info = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "pid": os.getpid(),
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "debug": current_app.debug,
        "remote_addr": request.remote_addr,
    }
    return render_template("modules/status/index.html", info=info, title="Status")
