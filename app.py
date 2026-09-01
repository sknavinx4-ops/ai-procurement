"""
app.py
Entry point for the AI-Powered Procurement ERP (Flask backend).

Run with:
    python app.py
Then open http://127.0.0.1:5000
"""

from flask import Flask, render_template
from database import get_connection, init_db
from modules.vendors import vendors_bp
from modules.rfq import rfq_bp
from modules.quotes import quotes_bp
from modules.purchase_order import po_bp
from modules.inventory import inventory_bp
from modules.finance import finance_bp

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

# Register all modules (blueprints).
app.register_blueprint(vendors_bp)
app.register_blueprint(rfq_bp)
app.register_blueprint(quotes_bp)
app.register_blueprint(po_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(finance_bp)


@app.route("/")
def dashboard():
    conn = get_connection()
    stats = {
        "total_vendors": conn.execute("SELECT COUNT(*) AS c FROM vendors").fetchone()["c"],
        "active_rfqs": conn.execute(
            "SELECT COUNT(*) AS c FROM rfqs WHERE status = 'Open'"
        ).fetchone()["c"],
        "pending_quotes": conn.execute("SELECT COUNT(*) AS c FROM quotes").fetchone()["c"],
        "purchase_orders": conn.execute(
            "SELECT COUNT(*) AS c FROM purchase_orders"
        ).fetchone()["c"],
    }
    recent_vendors = conn.execute(
        "SELECT * FROM vendors ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return render_template(
        "dashboard.html", stats=stats, recent_vendors=recent_vendors, active="dashboard"
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
