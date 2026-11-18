
from flask import Flask, jsonify, request, render_template
from src.prediction.predict_match import predict_match

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    required = ["team1", "team2", "format", "year", "venue"]

    if not all(data.get(key) for key in required):
        return jsonify({"error": "All fields are required"}), 400

    if data["team1"].strip().lower() == data["team2"].strip().lower():
        return jsonify({"error": "Select two different teams"}), 400

    try:
        result = predict_match(
            data["team1"].strip(),
            data["team2"].strip(),
            data["format"].upper(),
            int(data["year"]),
            data["venue"]
        )
        return jsonify(result)

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True)
