# Portal (Rebuild)

Drop-in Flask app with:
- Auto-discovered modules (`portal/modules/*/module.py` with `META` and `blueprint`).
- Re-orderable *Portal Items* with full field editing.
- Module enable/disable, menu visibility, label, and order.
- Unified base template and complete static files.
- Absolute-safe imports; run using `python app.py` (no `-m` required).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000/

## Adding a Module

Create a folder: `portal/modules/yourmod/module.py` and define:

```python
from flask import Blueprint, render_template
META = {"label":"Your Mod","description":"...","icon":"box"}
blueprint = Blueprint("yourmod", __name__, template_folder="templates")

@blueprint.route("/")
def index():
    return render_template("modules/yourmod/index.html", title="Your Mod")
```

Add a template at `portal/templates/modules/yourmod/index.html`:

```jinja2
{% extends "base.html" %}
{% block content %}<h2>Your Mod</h2>{% endblock %}
```

The module will be discovered automatically at startup.


## Modules

- `demo`: original demonstration module.
- `status`: system/app health example.
- `notes`: in-memory notes sample.
- `vm_manager`: **skeleton** UI + backend stubs that follow the VM management project memo.
