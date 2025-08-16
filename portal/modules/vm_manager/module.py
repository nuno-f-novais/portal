from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from . import k8s  # local skeleton lib

META = {
    "label": "VM Manager",
    "description": "Skeleton UI for creating and managing VMs on OpenShift/KubeVirt (per project memo).",
    "icon": "server",
}

blueprint = Blueprint("vm_manager", __name__, template_folder="templates")

@blueprint.route("/")
def index():
    # Placeholder: list VMs (stubbed for now)
    vms = [{"name": "example-win", "os": "Windows"}, {"name": "example-linux", "os": "Linux"}]
    return render_template("modules/vm_manager/index.html", title="VM Manager", vms=vms)

@blueprint.route("/create", methods=["POST"])
def create_vm():
    payload = {
        "name": request.form.get("name"),
        "os_type": request.form.get("os_type", "linux").lower(),
        "namespace": request.form.get("namespace", "poc-vms"),
        "source_pvc": request.form.get("source_pvc") or None,
    }
    try:
        status = k8s.create_vm_with_templates(**payload)
        flash(f"Create VM returned status: {status.name}", "info")
        return redirect(url_for("vm_manager.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("vm_manager.index"))

@blueprint.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})
