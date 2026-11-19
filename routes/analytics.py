from flask import Blueprint, jsonify, request

from src.analytics.world_cup_analytics import (
    get_overview,
    get_team_statistics,
    get_team_details,
    get_head_to_head,
    get_tournament_history,
)

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.get("/overview")
def overview():
    try:
        return jsonify(get_overview(request.args.get("format", "ALL")))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@analytics_bp.get("/teams")
def teams():
    try:
        return jsonify({
            "teams": get_team_statistics(request.args.get("format", "ALL"))
        })
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@analytics_bp.get("/team/<path:team>")
def team_details(team):
    try:
        return jsonify(
            get_team_details(team, request.args.get("format", "ALL"))
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 404


@analytics_bp.get("/head-to-head")
def head_to_head():
    try:
        team1 = request.args.get("team1", "")
        team2 = request.args.get("team2", "")

        if not team1 or not team2:
            return jsonify({"error": "Both team1 and team2 are required."}), 400

        return jsonify(get_head_to_head(
            team1, team2, request.args.get("format", "ALL")
        ))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@analytics_bp.get("/tournaments")
def tournaments():
    try:
        return jsonify({
            "tournaments": get_tournament_history(
                request.args.get("format", "ALL")
            )
        })
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
