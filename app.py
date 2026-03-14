from flask import Flask, render_template, request, jsonify, session
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_logic import Game
from game_data import CONTINENTS, ALL_TERRITORIES, ADJACENCIES

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))
app.secret_key = "risk_global_secret_2024"

games = {}

def get_game():
    game_id = session.get("game_id")
    if not game_id or game_id not in games:
        return None
    return games[game_id]

def state_response(g):
    """Return full state with reinforce_pool always included."""
    s = g.get_state()
    # reinforce_pool is already in the state from get_state()
    return s

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/game")
def game_page():
    return render_template("game.html")

@app.route("/api/new_game", methods=["POST"])
def new_game():
    data = request.json
    num_ai = max(1, min(10, int(data.get("num_ai", 2))))
    game_id = "game_" + str(id({}))
    games[game_id] = Game(num_ai)
    session["game_id"] = game_id
    return jsonify({"game_id": game_id, "state": state_response(games[game_id])})

@app.route("/api/state")
def get_state():
    g = get_game()
    if not g:
        return jsonify({"error": "No game"}), 404
    return jsonify(state_response(g))

@app.route("/api/reinforce", methods=["POST"])
def reinforce():
    g = get_game()
    if not g:
        return jsonify({"error": "No game"}), 404
    data = request.json
    result = g.reinforce(0, data["territory"], int(data["armies"]))
    if "error" not in result:
        result["state"] = state_response(g)
    return jsonify(result)

@app.route("/api/attack", methods=["POST"])
def attack():
    g = get_game()
    if not g:
        return jsonify({"error": "No game"}), 404
    data = request.json
    result = g.attack(0, data["from"], data["to"], int(data.get("dice", 3)))
    if "error" not in result:
        result["state"] = state_response(g)
    return jsonify(result)

@app.route("/api/end_attack", methods=["POST"])
def end_attack():
    g = get_game()
    if not g:
        return jsonify({"error": "No game"}), 404
    result = g.end_attack(0)
    if "error" not in result:
        result["state"] = state_response(g)
    return jsonify(result)

@app.route("/api/fortify", methods=["POST"])
def fortify():
    g = get_game()
    if not g:
        return jsonify({"error": "No game"}), 404
    data = request.json
    result = g.fortify(0, data["from"], data["to"], int(data["armies"]))
    if "error" not in result:
        result["state"] = state_response(g)
    return jsonify(result)

@app.route("/api/skip_fortify", methods=["POST"])
def skip_fortify():
    g = get_game()
    if not g:
        return jsonify({"error": "No game"}), 404
    result = g.skip_fortify(0)
    if "error" not in result:
        result["state"] = state_response(g)
    return jsonify(result)

@app.route("/api/trade_cards", methods=["POST"])
def trade_cards():
    g = get_game()
    if not g:
        return jsonify({"error": "No game"}), 404
    data = request.json
    result = g.trade_cards(0, data["card_indices"])
    if "error" not in result:
        result["state"] = state_response(g)
    return jsonify(result)

@app.route("/api/map_data")
def map_data():
    return jsonify({
        "territories": ALL_TERRITORIES,
        "continents": CONTINENTS,
        "adjacencies": ADJACENCIES
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
