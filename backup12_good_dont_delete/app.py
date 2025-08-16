from portal import create_app
from portal.core.bootstrap import wipe_and_seed
from portal.core import nav_middleware

app = create_app()
with app.app_context():
    wipe_and_seed(app)
app.before_request(nav_middleware.before_request)

if __name__ == "__main__":
    # Explicit host/port so it's easy to run locally
    app.run(host="0.0.0.0", port=5000, debug=True)
