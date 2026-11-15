from flask import Flask, request, jsonify

app = Flask(__name__)

attendees = []
next_id = 1

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

if __name__ == "__main__":
    app.run(debug=True)