from app import create_app
from app.extensions import db
from app.utils.seed_admin import create_first_admin
import logging

app = create_app()

# --- Set up logging filter to hide debugger static requests ---
class DebugFilter(logging.Filter):
    def filter(self, record):
        return "__debugger__" not in record.getMessage()

log = logging.getLogger('werkzeug')
log.addFilter(DebugFilter())
log.setLevel(logging.INFO)  # keep other requests visible

# --- Database setup and admin seeding ---
with app.app_context():
    db.create_all()
    create_first_admin()

# --- Run app ---
if __name__ == "__main__":
    port = 5001
    app.run(debug=True, port=port)
