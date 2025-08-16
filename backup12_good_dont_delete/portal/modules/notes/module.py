from flask import Blueprint, render_template, request, redirect, url_for, flash

META = {
    "label": "Notes",
    "description": "Tiny example CRUD-ish module (in-memory).",
    "icon": "sticky-note",
}

blueprint = Blueprint("notes", __name__, template_folder="templates")

_NOTES = []

@blueprint.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        txt = (request.form.get("text") or "").strip()
        if txt:
            _NOTES.append(txt)
            flash("Note added!", "success")
        else:
            flash("Cannot add an empty note.", "warning")
        return redirect(url_for("notes.index"))
    return render_template("modules/notes/index.html", notes=list(_NOTES), title="Notes")
