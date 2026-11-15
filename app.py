from flask import Flask, jsonify

app = Flask(__name__)

attendees = []

@app.route("/attendees", methods=["GET"])
def get_all_attendees():
    return jsonify({"attendees": attendees}), 200


if __name__ == "__main__":
    app.run(debug=True)