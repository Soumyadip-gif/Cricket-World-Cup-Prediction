
from flask import Flask, jsonify, request, render_template
from datetime import date
from src.prediction.predict_match import predict_match
from routes.analytics import analytics_bp

app = Flask(__name__)
app.register_blueprint(analytics_bp)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    team1 = data.get("team1")
    team2 = data.get("team2")
    match_format = data.get("format")

    if not all(isinstance(value, str) and value.strip()
               for value in [team1, team2, match_format]):
        return jsonify({
            "error": "Team 1, Team 2 and match format are required."
        }), 400

    team1 = team1.strip()
    team2 = team2.strip()
    match_format = match_format.strip().upper()

    if team1.casefold() == team2.casefold():
        return jsonify({"error": "Select two different teams"}), 400

    if match_format not in ["ODI", "T20I"]:
        return jsonify({"error": "Format must be ODI or T20I."}), 400

    try:
        result = predict_match(
            team1,
            team2,
            match_format,
            date.today().year,
            "Unknown"
        )
        return jsonify(result)

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400

if __name__ == "__main__":
    app.run(debug=True)
