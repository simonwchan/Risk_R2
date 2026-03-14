import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, session
from engine import Game

app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))
app.secret_key = "risk-global-2024"

_games = {}

def _game():
    gid = session.get("gid")
    return _games.get(gid)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/game")
def game_page():
    return render_template("game.html")

@app.route("/api/new", methods=["POST"])
def api_new():
    num_ai = max(1, min(10, int(request.json.get("num_ai", 3))))
    g = Game(num_ai)
    gid = str(id(g))
    _games[gid] = g
    session["gid"] = gid
    return jsonify({"ok": True, "state": g.state()})

@app.route("/api/state")
def api_state():
    g = _game()
    if not g:
        return jsonify({"error": "no game"}), 404
    return jsonify(g.state())

@app.route("/api/reinforce", methods=["POST"])
def api_reinforce():
    g = _game()
    if not g: return jsonify({"error": "no game"}), 404
    d = request.json
    r = g.reinforce(d["territory"], int(d["armies"]))
    if "ok" in r:
        r["state"] = g.state()
    return jsonify(r)

@app.route("/api/end_reinforce", methods=["POST"])
def api_end_reinforce():
    g = _game()
    if not g: return jsonify({"error": "no game"}), 404
    r = g.end_reinforce()
    if "ok" in r:
        r["state"] = g.state()
    return jsonify(r)

@app.route("/api/attack", methods=["POST"])
def api_attack():
    g = _game()
    if not g: return jsonify({"error": "no game"}), 404
    d = request.json
    r = g.attack(d["from"], d["to"], int(d.get("dice", 3)))
    if "ok" in r:
        r["state"] = g.state()
    return jsonify(r)

@app.route("/api/end_attack", methods=["POST"])
def api_end_attack():
    g = _game()
    if not g: return jsonify({"error": "no game"}), 404
    r = g.end_attack()
    if "ok" in r:
        r["state"] = g.state()
    return jsonify(r)

@app.route("/api/fortify", methods=["POST"])
def api_fortify():
    g = _game()
    if not g: return jsonify({"error": "no game"}), 404
    d = request.json
    r = g.fortify(d["from"], d["to"], int(d["armies"]))
    if "ok" in r:
        r["state"] = g.state()
    return jsonify(r)

@app.route("/api/skip_fortify", methods=["POST"])
def api_skip_fortify():
    g = _game()
    if not g: return jsonify({"error": "no game"}), 404
    r = g.skip_fortify()
    if "ok" in r:
        r["state"] = g.state()
    return jsonify(r)

@app.route("/api/trade_cards", methods=["POST"])
def api_trade_cards():
    g = _game()
    if not g: return jsonify({"error": "no game"}), 404
    r = g.trade_cards(request.json["indices"])
    if "ok" in r:
        r["state"] = g.state()
    return jsonify(r)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
