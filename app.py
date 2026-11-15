from datetime import datetime, timezone, timedelta
from flask import request, jsonify

PH_TZ = timezone(timedelta(hours=8))

def compute_status(a):
    if a["arrival"] is None:
        return "registered"
    suffix = "completed" if a["out"] else "exit_unverified"
    return f'{a["arrival"]}_{suffix}'

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