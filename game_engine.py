import random
import json
from map_data import (
    ALL_TERRITORIES, CONTINENTS, TERRITORY_TO_CONTINENT,
    ADJACENCY, calculate_reinforcements
)

PLAYER_COLORS = [
    "#E63946",  # Red
    "#457B9D",  # Blue
    "#2D6A4F",  # Green
    "#E9C46A",  # Yellow
    "#9B5DE5",  # Purple
    "#F4A261",  # Orange
    "#06D6A0",  # Teal
    "#FB5607",  # Burnt Orange
    "#8338EC",  # Violet
    "#3A86FF",  # Sky Blue
]

CPU_NAMES = ["Atlas", "Xerxes", "Genghis", "Caesar", "Cleopatra",
             "Napoleon", "Saladin", "Ashoka", "Tokugawa", "Shaka"]

class GameState:
    def __init__(self, num_cpu=3):
        self.num_cpu = min(max(num_cpu, 2), 10)
        self.players = self._init_players()
        self.territories = {}  # territory -> {owner, troops}
        self.current_player_idx = 0
        self.phase = "reinforcement"  # reinforcement, attack, fortify
        self.pending_reinforcements = 0
        self.game_over = False
        self.winner = None
        self.turn = 1
        self.cards = self._init_cards()
        self.player_cards = {p["id"]: [] for p in self.players}
        self.card_sets_traded = 0
        self.attack_log = []
        self.conquered_this_turn = False
        self._distribute_territories()
        self._set_initial_reinforcements()

    def _init_players(self):
        players = [{"id": 0, "name": "You", "color": PLAYER_COLORS[0], "is_cpu": False, "alive": True}]
        for i in range(self.num_cpu):
            players.append({
                "id": i + 1,
                "name": CPU_NAMES[i],
                "color": PLAYER_COLORS[i + 1],
                "is_cpu": True,
                "alive": True
            })
        return players

    def _init_cards(self):
        cards = []
        types = ["infantry", "cavalry", "artillery"]
        for i, t in enumerate(ALL_TERRITORIES):
            cards.append({"territory": t, "type": types[i % 3]})
        cards.append({"territory": None, "type": "wild"})
        cards.append({"territory": None, "type": "wild"})
        random.shuffle(cards)
        return cards

    def _distribute_territories(self):
        shuffled = ALL_TERRITORIES.copy()
        random.shuffle(shuffled)
        num_players = len(self.players)
        for i, t in enumerate(shuffled):
            owner = i % num_players
            self.territories[t] = {"owner": owner, "troops": 1}

    def _set_initial_reinforcements(self):
        # Give extra troops based on territory count
        for pid in range(len(self.players)):
            owned = self.get_player_territories(pid)
            extra = max(0, 20 - len(owned))
            for t in random.sample(owned, min(extra, len(owned))):
                self.territories[t]["troops"] += random.randint(1, 2)
        self.pending_reinforcements = calculate_reinforcements(
            self.get_player_territories(0)
        )

    def get_player_territories(self, player_id):
        return [t for t, d in self.territories.items() if d["owner"] == player_id]

    def get_alive_players(self):
        return [p for p in self.players if p["alive"]]

    def current_player(self):
        return self.players[self.current_player_idx]

    def place_reinforcement(self, territory, count):
        """Human player places troops."""
        if self.phase != "reinforcement":
            return {"ok": False, "msg": "Not reinforcement phase"}
        t = self.territories.get(territory)
        if not t or t["owner"] != 0:
            return {"ok": False, "msg": "Not your territory"}
        if count > self.pending_reinforcements or count < 1:
            return {"ok": False, "msg": f"Invalid count (have {self.pending_reinforcements})"}
        self.territories[territory]["troops"] += count
        self.pending_reinforcements -= count
        if self.pending_reinforcements == 0:
            self.phase = "attack"
        return {"ok": True, "remaining": self.pending_reinforcements}

    def attack(self, from_t, to_t, num_attackers):
        """Perform one attack roll."""
        if self.phase != "attack":
            return {"ok": False, "msg": "Not attack phase"}
        ft = self.territories.get(from_t)
        tt = self.territories.get(to_t)
        if not ft or ft["owner"] != 0:
            return {"ok": False, "msg": "Not your territory"}
        if not tt or tt["owner"] == 0:
            return {"ok": False, "msg": "Invalid target"}
        if to_t not in ADJACENCY.get(from_t, []):
            return {"ok": False, "msg": "Not adjacent"}
        if ft["troops"] < 2:
            return {"ok": False, "msg": "Need at least 2 troops to attack"}
        num_attackers = min(num_attackers, ft["troops"] - 1, 3)
        num_defenders = min(tt["troops"], 2)

        a_dice = sorted([random.randint(1, 6) for _ in range(num_attackers)], reverse=True)
        d_dice = sorted([random.randint(1, 6) for _ in range(num_defenders)], reverse=True)

        a_losses = d_losses = 0
        for a, d in zip(a_dice, d_dice):
            if a > d:
                d_losses += 1
            else:
                a_losses += 1

        ft["troops"] -= a_losses
        tt["troops"] -= d_losses

        conquered = False
        if tt["troops"] <= 0:
            old_owner = tt["owner"]
            tt["owner"] = 0
            tt["troops"] = num_attackers - a_losses
            ft["troops"] -= (num_attackers - a_losses)
            conquered = True
            self.conquered_this_turn = True
            # Check if old owner is eliminated
            if not self.get_player_territories(old_owner):
                self.players[old_owner]["alive"] = False
                # Transfer cards
                self.player_cards[0].extend(self.player_cards[old_owner])
                self.player_cards[old_owner] = []

        self._check_win()
        log = {
            "from": from_t, "to": to_t,
            "a_dice": a_dice, "d_dice": d_dice,
            "a_losses": a_losses, "d_losses": d_losses,
            "conquered": conquered,
            "attacker_troops": ft["troops"],
            "defender_troops": tt["troops"] if not conquered else 0
        }
        self.attack_log = [log] + self.attack_log[:9]
        return {"ok": True, **log}

    def fortify(self, from_t, to_t, count):
        """Move troops between connected friendly territories."""
        if self.phase not in ("attack", "fortify"):
            return {"ok": False, "msg": "Wrong phase"}
        ft = self.territories.get(from_t)
        tt = self.territories.get(to_t)
        if not ft or ft["owner"] != 0:
            return {"ok": False, "msg": "Not your territory"}
        if not tt or tt["owner"] != 0:
            return {"ok": False, "msg": "Target not yours"}
        if not self._connected(from_t, to_t, 0):
            return {"ok": False, "msg": "Territories not connected"}
        if count >= ft["troops"] or count < 1:
            return {"ok": False, "msg": "Invalid troop count"}
        ft["troops"] -= count
        tt["troops"] += count
        self.end_turn()
        return {"ok": True}

    def _connected(self, start, end, player_id):
        """BFS to check if two territories are connected through owned land."""
        if start == end:
            return True
        visited = {start}
        queue = [start]
        while queue:
            curr = queue.pop(0)
            for nb in ADJACENCY.get(curr, []):
                if nb not in visited and self.territories.get(nb, {}).get("owner") == player_id:
                    if nb == end:
                        return True
                    visited.add(nb)
                    queue.append(nb)
        return False

    def end_turn(self):
        """End human player's turn and run all CPU turns."""
        if self.conquered_this_turn and self.cards:
            self.player_cards[0].append(self.cards.pop())
        self.conquered_this_turn = False

        # Advance to next alive player
        self._next_player()
        while self.current_player()["is_cpu"] and not self.game_over:
            self._run_cpu_turn(self.current_player_idx)
            if self.game_over:
                break
            self._next_player()
            if not self.current_player()["is_cpu"]:
                break

        if not self.game_over:
            self.phase = "reinforcement"
            self.pending_reinforcements = calculate_reinforcements(
                self.get_player_territories(0)
            )
            self.turn += 1

    def _next_player(self):
        n = len(self.players)
        for _ in range(n):
            self.current_player_idx = (self.current_player_idx + 1) % n
            if self.players[self.current_player_idx]["alive"]:
                return

    def _run_cpu_turn(self, pid):
        """Simple but decent CPU AI."""
        owned = self.get_player_territories(pid)
        if not owned:
            return

        # Reinforcement
        reinf = calculate_reinforcements(owned)
        # Place on border territories with enemies
        border = [t for t in owned if any(
            self.territories.get(nb, {}).get("owner") != pid
            for nb in ADJACENCY.get(t, [])
        )]
        if border:
            target = max(border, key=lambda t: self.territories[t]["troops"])
        else:
            target = random.choice(owned)
        self.territories[target]["troops"] += reinf

        # Attack phase - aggressive
        for _ in range(20):  # max 20 attacks per turn
            attacks = []
            for t in self.get_player_territories(pid):
                if self.territories[t]["troops"] < 2:
                    continue
                for nb in ADJACENCY.get(t, []):
                    nb_data = self.territories.get(nb)
                    if nb_data and nb_data["owner"] != pid:
                        ratio = self.territories[t]["troops"] / max(1, nb_data["troops"])
                        attacks.append((t, nb, ratio))
            if not attacks:
                break
            attacks.sort(key=lambda x: -x[2])
            best = attacks[0]
            if best[2] < 1.5:
                break  # Don't attack if odds are bad
            from_t, to_t, _ = best
            num_att = min(3, self.territories[from_t]["troops"] - 1)
            self._cpu_attack(pid, from_t, to_t, num_att)
            if self.game_over:
                return

        # Fortify - consolidate
        owned = self.get_player_territories(pid)
        if len(owned) > 1:
            interior = [t for t in owned if all(
                self.territories.get(nb, {}).get("owner") == pid
                for nb in ADJACENCY.get(t, []) if nb in self.territories
            )]
            for t in interior:
                if self.territories[t]["troops"] > 1:
                    border_nb = None
                    for nb in ADJACENCY.get(t, []):
                        if self.territories.get(nb, {}).get("owner") == pid:
                            nb_border = any(
                                self.territories.get(x, {}).get("owner") != pid
                                for x in ADJACENCY.get(nb, [])
                            )
                            if nb_border:
                                border_nb = nb
                                break
                    if border_nb:
                        move = self.territories[t]["troops"] - 1
                        self.territories[t]["troops"] -= move
                        self.territories[border_nb]["troops"] += move

        # Draw card
        if self.cards:
            self.player_cards[pid].append(self.cards.pop())

    def _cpu_attack(self, pid, from_t, to_t, num_att):
        ft = self.territories[from_t]
        tt = self.territories[to_t]
        num_att = min(num_att, ft["troops"] - 1, 3)
        num_def = min(tt["troops"], 2)
        a_dice = sorted([random.randint(1, 6) for _ in range(num_att)], reverse=True)
        d_dice = sorted([random.randint(1, 6) for _ in range(num_def)], reverse=True)
        for a, d in zip(a_dice, d_dice):
            if a > d:
                tt["troops"] -= 1
            else:
                ft["troops"] -= 1
        if tt["troops"] <= 0:
            old_owner = tt["owner"]
            tt["owner"] = pid
            tt["troops"] = max(1, ft["troops"] - 1)
            ft["troops"] = 1
            if not self.get_player_territories(old_owner):
                self.players[old_owner]["alive"] = False
            self._check_win()

    def _check_win(self):
        alive = self.get_alive_players()
        if len(alive) == 1:
            self.game_over = True
            self.winner = alive[0]
            self.phase = "game_over"

    def to_dict(self):
        return {
            "territories": self.territories,
            "players": self.players,
            "current_player_idx": self.current_player_idx,
            "phase": self.phase,
            "pending_reinforcements": self.pending_reinforcements,
            "game_over": self.game_over,
            "winner": self.winner,
            "turn": self.turn,
            "attack_log": self.attack_log,
            "player_cards": {str(k): v for k, v in self.player_cards.items()},
            "continents": {
                name: {
                    "bonus": data["bonus"],
                    "color": data["color"],
                    "territories": data["territories"]
                }
                for name, data in CONTINENTS.items()
            },
            "territory_continent": TERRITORY_TO_CONTINENT,
            "adjacency": ADJACENCY,
        }
