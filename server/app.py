from flask import Flask, jsonify, request, send_from_directory, session, make_response

app = Flask(__name__, static_folder="static")

# Flask uses SECRET_KEY to sign session cookies.
# TODO: Replace this classroom value with a safer secret in a real application.
app.config["SECRET_KEY"] = "change-this-secret-key-for-class-demo"


# In-memory data for this practical.
# NOTE: Restarting the Flask server resets this list.
study_sessions = [
    {"id": 1, "topic": "Understand GET requests", "minutes": 25, "completed": False},
    {"id": 2, "topic": "Practice Flask routes", "minutes": 30, "completed": False},
]


def find_study_session(session_id):
    """Helper supplied for students: find one study sprint by its id."""
    for item in study_sessions:
        if item["id"] == session_id:
            return item
    return None


# -----------------------------------------------------------------------------
# STARTING ROUTES PROVIDED TO STUDENTS
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the supplied client-side application."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/study-sessions", methods=["GET"])
def get_study_sessions():
    """READ: Return all study sprints as JSON."""
    return jsonify(study_sessions), 200


# -----------------------------------------------------------------------------
# STUDENT TODO AREA
# Build the routes below yourself. Read README.md and static/js/app.js first.
# The comments intentionally give hints without giving the solutions.
# -----------------------------------------------------------------------------

# TODO 1 - SESSION + COOKIE READ
# Endpoint: GET /api/me
@app.route("/api/me", methods=["GET"])
# Goal:
#   - Read the learner's username from Flask session storage.
def get_me():
    username = session.get("username")
    #   - Keep a session-based visit counter and increase it on each request.
    visits = session.get("visits", 0)
    visits += 1
    session["visits"] = visits
    #   - Read the non-sensitive "focus_mode" cookie from the incoming request.
    focus_mode = request.cookies.get("focus_mode", "standard")
    #   - Return username, visits, and focus_mode as JSON.
    return jsonify({"username": username, "visits": visits, "focus_mode": focus_mode}), 200
# Hint: session.get(...) and request.cookies.get(...) may help.


# TODO 2 - LOGIN
# Endpoint: POST /api/login
@app.route("/api/login", methods=["POST"])
def login():
    # Goal:
    #   - Read JSON sent by the client: {"username": "Amina"}
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    #   - Validate that username is not empty.
    if not username:
        return jsonify({"error": "Username is required."}), 400
    #   - Store the username in Flask's session.
    session["username"] = username
    #   - Initialise/reset the visit counter.
    session["visits"] = 0
    #   - Return useful JSON and the correct status code.
    return jsonify({"message": "Login successful", "username": username}), 201
# Hint: request.get_json() and session[...] may help.


# TODO 3 - LOGOUT
# Endpoint: POST /api/logout
@app.route("/api/logout", methods=["POST"])
# Goal:
#   - Clear the current Flask session.
def logout():
    session.clear()
    #   - Return a success message as JSON.
    return jsonify({"message": "Session cleared. You are logged out."}), 200
# Hint: Flask session has a method that clears all stored session values.


# TODO 4 - CREATE
# Endpoint: POST /api/study-sessions
@app.route("/api/study-sessions", methods=["POST"])
def create_study_session():
    # Goal:
    #   - Read JSON containing topic and minutes.
    data = request.get_json(silent=True) or {}
    topic = str(data.get("topic", "")).strip()
    if not topic:
        return jsonify({"error": "Topic is required."}), 400
    try:
        minutes = int(data.get("minutes"))
    except (TypeError, ValueError):
        return jsonify({"error": "Minutes must be a number."}), 400
    #   - Create a unique integer id.
    new_id = max((item["id"] for item in study_sessions), default=0) + 1
    #   - Set completed to False for a new sprint.
    new_session = {"id": new_id, "topic": topic, "minutes": minutes, "completed": False}
    #   - Append the new item to study_sessions.
    study_sessions.append(new_session)
    #   - Return the created item as JSON.
    return jsonify(new_session), 201
# Hint: inspect the JavaScript request body in static/js/app.js.


# TODO 5 - UPDATE
# Endpoint: PATCH /api/study-sessions/<int:session_id>
@app.route("/api/study-sessions/<int:session_id>", methods=["PATCH"])
def complete_study_session(session_id):
    # Goal:
    #   - Find the requested sprint using find_study_session(...).
    study_session = find_study_session(session_id)
    #   - Return a 404 JSON error when the id does not exist.
    if study_session is None:
        return jsonify({"error": "Study session not found."}), 404
    #   - Mark the sprint as completed.
    study_session["completed"] = True
    #   - Return the updated sprint as JSON.
    return jsonify(study_session), 200


# TODO 6 - DELETE
# Endpoint: DELETE /api/study-sessions/<int:session_id>
@app.route("/api/study-sessions/<int:session_id>", methods=["DELETE"])
def delete_study_session(session_id):
    # Goal:
    #   - Find the requested sprint.
    study_session = find_study_session(session_id)
    #   - Return a 404 JSON error when the id does not exist.
    if study_session is None:
        return jsonify({"error": "Study session not found."}), 404
    #   - Remove it from study_sessions.
    study_sessions.remove(study_session)
    #   - Return a useful JSON confirmation.
    return jsonify({"message": "Study session deleted.", "deleted": study_session}), 200


# TODO 7 - MANUAL COOKIE
# Endpoint: POST /api/focus-mode
@app.route("/api/focus-mode", methods=["POST"])
def set_focus_mode():
    # Goal:
    #   - Read JSON such as {"mode": "deep"}.
    data = request.get_json(silent=True) or {}
    mode = str(data.get("mode", "")).strip().lower()
    #   - Accept only: standard, deep, revision, practice.
    allowed_modes = {"standard", "deep", "revision", "practice"}
    if mode not in allowed_modes:
        #   - Return a 400 JSON error for another value.
        return jsonify({"error": "Invalid focus mode."}), 400
    #   - Create a Flask response and set a cookie named "focus_mode".
    response = make_response(jsonify({"message": "Focus mode saved.", "focus_mode": mode}), 200)
    seven_days = 60 * 60 * 24 * 7
    response.set_cookie("focus_mode", mode, max_age=seven_days, samesite="Lax")
    #   - Return a JSON success response.
    return response
# Hint: make_response(...) and response.set_cookie(...) may help.


if __name__ == "__main__":
    app.run(debug=True, port=5000)
