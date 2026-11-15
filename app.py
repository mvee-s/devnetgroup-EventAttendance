
from flask import Flask, jsonify

app = Flask(__name__)

attendees = []


# GET all attendees
@app.route("/attendees", methods=["GET"])
def get_all_attendees():
    return jsonify({"attendees": attendees}), 200


# GET attendance summary
@app.route("/attendees/summary", methods=["GET"])
def get_attendance_summary():
    total_registered = len(attendees)

    on_time = sum(
        1 for a in attendees if a["arrival"] == "on_time"
    )

    late = sum(
        1 for a in attendees if a["arrival"] == "late"
    )

    no_arrival = sum(
        1 for a in attendees if a["arrival"] is None
    )

    completed = sum(
        1 for a in attendees if a["out"] is True
    )

    exit_unverified = sum(
        1 for a in attendees
        if a["arrival"] is not None and a["out"] is False
    )

    summary = {
        "total_registered": total_registered,
        "on_time": on_time,
        "late": late,
        "no_arrival": no_arrival,
        "completed": completed,
        "exit_unverified": exit_unverified
    }

    return jsonify(summary), 200


if __name__ == "__main__":
    app.run(debug=True)