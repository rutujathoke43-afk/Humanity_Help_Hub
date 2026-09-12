from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Session साठी secret key
app.secret_key = "humanity-help-hub-secret-key"

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "humanity_help.db"
)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS help_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            category TEXT NOT NULL,
            problem TEXT NOT NULL,
            location TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS help_offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            helper_name TEXT NOT NULL,
            helper_phone TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ================= HOME =================

@app.route("/")
def home():
    return render_template("index.html")


# ================= REQUEST HELP =================

@app.route("/request-help")
def request_help():
    return render_template("request_help.html")


@app.route("/api/request-help", methods=["POST"])
def save_help_request():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "message": "No data received."
            }), 400

        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        category = data.get("category", "").strip()
        problem = data.get("problem", "").strip()
        location = data.get("location", "").strip()

        if not name:
            return jsonify({
                "message": "Please enter your name."
            }), 400

        if not phone:
            return jsonify({
                "message": "Please enter your phone number."
            }), 400

        if not category:
            return jsonify({
                "message": "Please select a category."
            }), 400

        if not problem:
            return jsonify({
                "message": "Please describe your problem."
            }), 400

        if not location:
            return jsonify({
                "message": "Please enter your location."
            }), 400

        conn = get_db()

        conn.execute("""
            INSERT INTO help_requests
            (name, phone, category, problem, location)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            phone,
            category,
            problem,
            location
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Help request saved successfully!"
        }), 200

    except Exception as e:

        print("Error:", e)

        return jsonify({
            "message": "Database error occurred."
        }), 500


# ================= REQUESTS =================

@app.route("/requests")
def requests():
    return render_template("requests.html")


@app.route("/api/requests")
def get_requests():

    try:
        conn = get_db()

        rows = conn.execute("""
            SELECT
                id,
                name,
                phone,
                category,
                problem,
                location,
                created_at
            FROM help_requests
            ORDER BY id DESC
        """).fetchall()

        conn.close()

        requests_list = []

        for row in rows:

            requests_list.append({
                "id": row["id"],
                "name": row["name"],
                "phone": row["phone"],
                "category": row["category"],
                "problem": row["problem"],
                "location": row["location"],
                "created_at": row["created_at"]
            })

        return jsonify(requests_list), 200

    except Exception as e:

        print("Error:", e)

        return jsonify({
            "message": "Unable to load requests."
        }), 500


# ================= HELP OFFER =================

@app.route("/api/help-offer", methods=["POST"])
def save_help_offer():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "No data received."
            }), 400

        request_id = data.get("request_id")
        helper_name = data.get("helper_name", "").strip()
        helper_phone = data.get("helper_phone", "").strip()
        message = data.get("message", "").strip()

        if not request_id:
            return jsonify({
                "message": "Request ID is missing."
            }), 400

        if not helper_name:
            return jsonify({
                "message": "Please enter your name."
            }), 400

        if not helper_phone:
            return jsonify({
                "message": "Please enter your phone number."
            }), 400

        if not message:
            return jsonify({
                "message": "Please enter your message."
            }), 400

        conn = get_db()

        existing_request = conn.execute("""
            SELECT id
            FROM help_requests
            WHERE id = ?
        """, (request_id,)).fetchone()

        if existing_request is None:

            conn.close()

            return jsonify({
                "message": "Help request not found."
            }), 404

        conn.execute("""
            INSERT INTO help_offers
            (request_id, helper_name, helper_phone, message)
            VALUES (?, ?, ?, ?)
        """, (
            request_id,
            helper_name,
            helper_phone,
            message
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Help offer saved successfully!"
        }), 200

    except Exception as e:

        print("Error:", e)

        return jsonify({
            "message": "Database error occurred."
        }), 500


# ================= OFFERS =================

@app.route("/offers")
def offers():
    return render_template("offers.html")


@app.route("/api/offers")
def get_offers():

    try:

        conn = get_db()

        rows = conn.execute("""
            SELECT
                help_offers.id,
                help_offers.request_id,
                help_offers.helper_name,
                help_offers.helper_phone,
                help_offers.message,
                help_offers.created_at,
                help_requests.name AS requester_name,
                help_requests.category AS category,
                help_requests.location AS location
            FROM help_offers
            LEFT JOIN help_requests
            ON help_offers.request_id = help_requests.id
            ORDER BY help_offers.id DESC
        """).fetchall()

        conn.close()

        offers_list = []

        for row in rows:

            offers_list.append({
                "id": row["id"],
                "request_id": row["request_id"],
                "helper_name": row["helper_name"],
                "helper_phone": row["helper_phone"],
                "message": row["message"],
                "created_at": row["created_at"],
                "requester_name": row["requester_name"],
                "category": row["category"],
                "location": row["location"]
            })

        return jsonify(offers_list), 200

    except Exception as e:

        print("Error:", e)

        return jsonify({
            "message": "Unable to load offers."
        }), 500


# ================= DELETE REQUEST =================

@app.route("/api/delete-request/<int:request_id>", methods=["DELETE"])
def delete_request(request_id):

    try:

        conn = get_db()

        conn.execute("""
            DELETE FROM help_offers
            WHERE request_id = ?
        """, (request_id,))

        result = conn.execute("""
            DELETE FROM help_requests
            WHERE id = ?
        """, (request_id,))

        conn.commit()
        conn.close()

        if result.rowcount == 0:

            return jsonify({
                "message": "Request not found."
            }), 404

        return jsonify({
            "message": "Help request deleted successfully!"
        }), 200

    except Exception as e:

        print("Delete request error:", e)

        return jsonify({
            "message": "Unable to delete request."
        }), 500


# ================= DELETE OFFER =================

@app.route("/api/delete-offer/<int:offer_id>", methods=["DELETE"])
def delete_offer(offer_id):

    try:

        conn = get_db()

        result = conn.execute("""
            DELETE FROM help_offers
            WHERE id = ?
        """, (offer_id,))

        conn.commit()
        conn.close()

        if result.rowcount == 0:

            return jsonify({
                "message": "Offer not found."
            }), 404

        return jsonify({
            "message": "Help offer deleted successfully!"
        }), 200

    except Exception as e:

        print("Delete offer error:", e)

        return jsonify({
            "message": "Unable to delete offer."
        }), 500


# ================= ADMIN LOGIN =================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Login details
        if username == "admin" and password == "admin123":

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin")
            )

        return render_template(
            "login.html",
            error="Invalid username or password."
        )

    return render_template("login.html")


# ================= ADMIN DASHBOARD =================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )

    return render_template("admin.html")


# ================= ADMIN LOGOUT =================

@app.route("/admin-logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("admin_login")
    )


# ================= RUN =================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)