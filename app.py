from flask import Flask, render_template, jsonify, request, session
from game_engine import GameState
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

game_store = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/new_game", methods=["POST"])
def new_game():
    data = request.json
    num_cpu = int(data.get("num_cpu", 3))
    game_id = "game1"
    game_store[game_id] = GameState(num_cpu=num_cpu)
    session["game_id"] = game_id
    return jsonify({"ok": True, "state": game_store[game_id].to_dict()})

@app.route("/api/state")
def get_state():
    gid = session.get("game_id")
    if not gid or gid not in game_store:
        return jsonify({"ok": False, "msg": "No game"})
    return jsonify({"ok": True, "state": game_store[gid].to_dict()})

@app.route("/api/reinforce", methods=["POST"])
def reinforce():
    gid = session.get("game_id")
    if not gid or gid not in game_store:
        return jsonify({"ok": False, "msg": "No game"})
    data = request.json
    result = game_store[gid].place_reinforcement(data["territory"], data["count"])
    result["state"] = game_store[gid].to_dict()
    return jsonify(result)

@app.route("/api/attack", methods=["POST"])
def attack():
    gid = session.get("game_id")
    if not gid or gid not in game_store:
        return jsonify({"ok": False, "msg": "No game"})
    data = request.json
    result = game_store[gid].attack(data["from"], data["to"], data.get("attackers", 3))
    result["state"] = game_store[gid].to_dict()
    return jsonify(result)

@app.route("/api/fortify", methods=["POST"])
def fortify():
    gid = session.get("game_id")
    if not gid or gid not in game_store:
        return jsonify({"ok": False, "msg": "No game"})
    data = request.json
    result = game_store[gid].fortify(data["from"], data["to"], data["count"])
    result["state"] = game_store[gid].to_dict()
    return jsonify(result)

@app.route("/api/end_turn", methods=["POST"])
def end_turn():
    gid = session.get("game_id")
    if not gid or gid not in game_store:
        return jsonify({"ok": False, "msg": "No game"})
    g = game_store[gid]
    if g.phase == "reinforcement" and g.pending_reinforcements > 0:
        return jsonify({"ok": False, "msg": f"Place your {g.pending_reinforcements} troops first"})
    g.end_turn()
    return jsonify({"ok": True, "state": g.to_dict()})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
