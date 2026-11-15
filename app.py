from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

attendees = []
next_id = 1

PH_TZ = timezone(timedelta(hours=8))


def compute_status(a):
    if a["arrival"] is None:
        return "registered"
    suffix = "completed" if a["out"] else "exit_unverified"
    return f'{a["arrival"]}_{suffix}'


# ---------------------------------------------------------------
# GET /attendees and GET /attendees/summary  -> Sarmiento
# (their routes go here once their branches are merged)
# ---------------------------------------------------------------

# GET /attendees/<int:id>  -> Belmonte
@app.route("/attendees/<int:id>", methods=["GET"])
def get_specific_attendee(id):
    attendee = next((a for a in attendees if a["id"] == id), None)
    if attendee is None:
        return jsonify({"error": "Attendee not found"}), 404
    return jsonify(attendee), 200

# POST /attendees  -> Pecson
@app.route("/attendees", methods=["POST"])
def register_attendee():
    global next_id

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    student_id = data.get("student_id")
    name = data.get("name")

    if not isinstance(student_id, str) or not student_id.strip():
        return jsonify({"error": "student_id is required"}), 400
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name is required"}), 400

    student_id = student_id.strip()
    name = name.strip()

    if any(a["student_id"] == student_id for a in attendees):
        return jsonify({"error": "student_id already registered"}), 409

    attendee = {
        "id": next_id,
        "student_id": student_id,
        "name": name,
        "arrival": None,
        "check_in_time": None,
        "out": False,
        "check_out_time": None,
        "status": "registered"
    }
    attendees.append(attendee)
    next_id += 1

    return jsonify(attendee), 201


# PATCH /attendees/<int:id>  -> Laxamana
@app.route("/attendees/<int:id>", methods=["PATCH"])
def update_attendee(id):
    attendee = next((a for a in attendees if a["id"] == id), None)
    if attendee is None:
        return jsonify({"error": "Attendee not found"}), 404

    data = request.get_json(silent=True) or {}
    phase = str(data.get("phase", "")).upper()
    now = datetime.now(PH_TZ).isoformat(timespec="seconds")

    if phase in ("ON_TIME", "LATE"):
        if attendee["arrival"] is not None:
            return jsonify({"error": "Arrival already recorded"}), 409
        attendee["arrival"] = phase.lower()
        attendee["check_in_time"] = now
    elif phase == "OUT":
        if attendee["arrival"] is None:
            return jsonify({"error": "Cannot check out without an arrival"}), 409
        if attendee["out"]:
            return jsonify({"error": "Exit already recorded"}), 409
        attendee["out"] = True
        attendee["check_out_time"] = now
    else:
        return jsonify({"error": "phase must be ON_TIME, LATE, or OUT"}), 400

    attendee["status"] = compute_status(attendee)
    return jsonify(attendee), 200


if __name__ == "__main__":
    app.run(debug=True)
