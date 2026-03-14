import random
from data import CONTINENTS, TERRITORIES, ADJACENCY, ALL_TERRITORIES

PLAYER_COLORS = ["#E74C3C","#3498DB","#2ECC71","#F39C12","#9B59B6",
                 "#1ABC9C","#E67E22","#2980B9","#27AE60","#C0392B","#8E44AD"]

AI_NAMES = ["General Chen","Commander Volkov","Admiral Okafor","Marshal Santos",
            "General Müller","Commander Ito","Admiral Patel","Marshal Al-Rashid",
            "General Osei","Commander Torres"]

CARD_BONUS = [4, 6, 8, 10, 12, 15]


class Game:
    def __init__(self, num_ai):
        num_ai = max(1, min(10, num_ai))
        total = num_ai + 1  # human + AI

        # --- Players ---
        self.players = {}
        self.players[0] = {
            "id": 0, "name": "You", "color": PLAYER_COLORS[0],
            "human": True, "eliminated": False, "cards": []
        }
        ai_names = random.sample(AI_NAMES, min(num_ai, len(AI_NAMES)))
        for i in range(num_ai):
            self.players[i+1] = {
                "id": i+1, "name": ai_names[i], "color": PLAYER_COLORS[i+1],
                "human": False, "eliminated": False, "cards": []
            }

        # --- Territories ---
        self.board = {}
        for t in ALL_TERRITORIES:
            self.board[t] = {"owner": None, "armies": 0}

        # --- Distribute territories randomly ---
        shuffled = ALL_TERRITORIES[:]
        random.shuffle(shuffled)
        for i, t in enumerate(shuffled):
            pid = i % total
            self.board[t]["owner"] = pid
            self.board[t]["armies"] = 1

        # --- Distribute starting bonus armies ---
        # Classic Risk: 40 armies for 2p, 35 for 3p, 30 for 4p, etc. (down to 20 for 6+)
        base = max(20, 40 - (total - 2) * 5)
        for pid in self.players:
            owned = [t for t, d in self.board.items() if d["owner"] == pid]
            extra = base - len(owned)
            for _ in range(extra):
                random.choice(owned)
                self.board[random.choice(owned)]["armies"] += 1

        # --- Game state ---
        self.turn = 1
        self.phase = "reinforce"   # reinforce | attack | fortify
        self.current = 0           # current player id (always starts with human)
        self.cards_traded = 0
        self.conquered_this_turn = False
        self.log = []

        # Pre-compute human's first pool
        self.pool = self._calc_pool(0)

    # ------------------------------------------------------------------
    # PUBLIC: calculate reinforcement armies for a player
    # ------------------------------------------------------------------
    def _calc_pool(self, pid):
        owned = [t for t, d in self.board.items() if d["owner"] == pid]
        n = max(3, len(owned) // 3)
        for cont, cdata in CONTINENTS.items():
            terrs = [t for t, cont_name in TERRITORIES.items() if cont_name == cont]
            if all(self.board[t]["owner"] == pid for t in terrs):
                n += cdata["bonus"]
        return n

    # ------------------------------------------------------------------
    # PUBLIC: get full serialisable state
    # ------------------------------------------------------------------
    def state(self):
        player_list = []
        for pid, p in self.players.items():
            owned = [t for t, d in self.board.items() if d["owner"] == pid]
            player_list.append({
                "id": pid,
                "name": p["name"],
                "color": p["color"],
                "human": p["human"],
                "eliminated": p["eliminated"],
                "cards": p["cards"],
                "territories": len(owned),
                "armies": sum(self.board[t]["armies"] for t in owned),
            })
        return {
            "board": self.board,
            "players": player_list,
            "current": self.current,
            "phase": self.phase,
            "turn": self.turn,
            "pool": self.pool,
            "winner": self._winner(),
            "log": self.log[-12:],
            "continents": CONTINENTS,
            "adjacency": ADJACENCY,
            "cards_traded": self.cards_traded,
        }

    def _winner(self):
        alive = [pid for pid, p in self.players.items() if not p["eliminated"]]
        return alive[0] if len(alive) == 1 else None

    # ------------------------------------------------------------------
    # PHASE: reinforce
    # ------------------------------------------------------------------
    def reinforce(self, territory, armies):
        """Place armies on a territory during reinforce phase."""
        err = self._check_phase("reinforce")
        if err: return err
        if self.board[territory]["owner"] != self.current:
            return {"error": "You don't own that territory"}
        if self.pool <= 0:
            return {"error": "No armies left to place"}
        armies = max(1, min(armies, self.pool))
        self.board[territory]["armies"] += armies
        self.pool -= armies
        self.log.append(f"You placed {armies} on {territory}  (pool left: {self.pool})")
        return {"ok": True, "pool": self.pool}

    def end_reinforce(self):
        """Advance from reinforce → attack (human calls this when done placing)."""
        err = self._check_phase("reinforce")
        if err: return err
        if self.pool > 0:
            return {"error": f"You still have {self.pool} armies to place"}
        self.phase = "attack"
        return {"ok": True}

    # ------------------------------------------------------------------
    # PHASE: attack
    # ------------------------------------------------------------------
    def attack(self, from_t, to_t, dice):
        """Attack from_t → to_t with 1-3 dice."""
        err = self._check_phase("attack")
        if err: return err
        if self.board[from_t]["owner"] != self.current:
            return {"error": "You don't own the attacking territory"}
        if self.board[to_t]["owner"] == self.current:
            return {"error": "Can't attack your own territory"}
        if to_t not in ADJACENCY.get(from_t, []):
            return {"error": "Territories are not adjacent"}
        if self.board[from_t]["armies"] < 2:
            return {"error": "Need at least 2 armies to attack"}

        atk_dice = min(dice, self.board[from_t]["armies"] - 1, 3)
        def_dice = min(2, self.board[to_t]["armies"])

        atk_rolls = sorted([random.randint(1,6) for _ in range(atk_dice)], reverse=True)
        def_rolls = sorted([random.randint(1,6) for _ in range(def_dice)], reverse=True)

        atk_loss = def_loss = 0
        for a, d in zip(atk_rolls, def_rolls):
            if a > d: def_loss += 1
            else:     atk_loss += 1

        self.board[from_t]["armies"] -= atk_loss
        self.board[to_t]["armies"]   -= def_loss

        result = {
            "ok": True,
            "atk_rolls": atk_rolls, "def_rolls": def_rolls,
            "atk_loss": atk_loss,   "def_loss": def_loss,
            "from": from_t, "to": to_t,
            "conquered": False,
        }

        msg = f"You attacked {to_t} from {from_t}  [{','.join(map(str,atk_rolls))}] vs [{','.join(map(str,def_rolls))}]"

        if self.board[to_t]["armies"] <= 0:
            old_owner = self.board[to_t]["owner"]
            moved = max(1, atk_dice - atk_loss)
            self.board[to_t]["owner"]  = self.current
            self.board[to_t]["armies"] = moved
            self.board[from_t]["armies"] -= moved  # armies move forward
            # ensure attacker has at least 1
            if self.board[from_t]["armies"] < 1:
                self.board[from_t]["armies"] = 1
                self.board[to_t]["armies"] = max(1, moved - 1)

            result["conquered"] = True
            result["moved"] = self.board[to_t]["armies"]
            self.conquered_this_turn = True
            msg += "  → CONQUERED!"

            # Draw a card
            card = random.choice(["infantry","cavalry","artillery","wild"])
            self.players[self.current]["cards"].append(card)

            # Check elimination
            defender_terrs = [t for t,d in self.board.items() if d["owner"] == old_owner]
            if not defender_terrs:
                self.players[old_owner]["eliminated"] = True
                # Attacker takes all defender's cards
                self.players[self.current]["cards"].extend(self.players[old_owner]["cards"])
                self.players[old_owner]["cards"] = []
                msg += f"  {self.players[old_owner]['name']} ELIMINATED!"
                result["eliminated"] = self.players[old_owner]["name"]

            w = self._winner()
            if w is not None:
                result["winner"] = self.players[w]["name"]

        self.log.append(msg)
        result["log"] = msg
        return result

    def end_attack(self):
        """Advance from attack → fortify."""
        err = self._check_phase("attack")
        if err: return err
        self.phase = "fortify"
        return {"ok": True}

    # ------------------------------------------------------------------
    # PHASE: fortify
    # ------------------------------------------------------------------
    def fortify(self, from_t, to_t, armies):
        """Move armies between connected owned territories."""
        err = self._check_phase("fortify")
        if err: return err
        if self.board[from_t]["owner"] != self.current:
            return {"error": "You don't own the source territory"}
        if self.board[to_t]["owner"] != self.current:
            return {"error": "You don't own the destination territory"}
        if self.board[from_t]["armies"] - armies < 1:
            return {"error": "Must leave at least 1 army behind"}
        if not self._path(from_t, to_t, self.current):
            return {"error": "No connected path through your territories"}
        self.board[from_t]["armies"] -= armies
        self.board[to_t]["armies"]   += armies
        self.log.append(f"You moved {armies} from {from_t} → {to_t}")
        self._end_turn()
        return {"ok": True}

    def skip_fortify(self):
        """Skip fortify and end turn."""
        err = self._check_phase("fortify")
        if err: return err
        self._end_turn()
        return {"ok": True}

    # ------------------------------------------------------------------
    # CARDS
    # ------------------------------------------------------------------
    def trade_cards(self, indices):
        """Trade 3 cards for bonus armies (added to current pool)."""
        if self.phase != "reinforce":
            return {"error": "Can only trade cards during reinforce phase"}
        if self.players[self.current]["owner"] if False else self.current != 0:
            return {"error": "Not your turn"}
        cards = self.players[self.current]["cards"]
        if len(indices) != 3:
            return {"error": "Select exactly 3 cards"}
        if max(indices) >= len(cards):
            return {"error": "Invalid card selection"}
        selected = [cards[i] for i in indices]
        types = [c for c in selected if c != "wild"]
        unique = set(types)
        wilds = selected.count("wild")
        valid = (wilds >= 1) or (len(unique) == 1) or (len(unique) == 3)
        if not valid:
            return {"error": "Invalid set — need all same, all different, or include a wild"}
        for i in sorted(indices, reverse=True):
            cards.pop(i)
        self.cards_traded += 1
        n = self.cards_traded
        bonus = CARD_BONUS[n-1] if n <= 6 else 15 + (n-6)*5
        self.pool += bonus
        self.log.append(f"You traded cards for {bonus} bonus armies")
        return {"ok": True, "bonus": bonus, "pool": self.pool}

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------
    def _check_phase(self, expected):
        if self.phase != expected:
            return {"error": f"Wrong phase (current: {self.phase})"}
        if self.current != 0:
            return {"error": "Not your turn"}
        return None

    def _end_turn(self):
        """End human turn, run all AI turns, then start next human turn."""
        self.conquered_this_turn = False
        alive = [pid for pid, p in self.players.items() if not p["eliminated"]]
        idx = alive.index(self.current)
        # Cycle through AI players
        for step in range(1, len(alive)):
            nxt = alive[(idx + step) % len(alive)]
            if not self.players[nxt]["eliminated"]:
                if not self.players[nxt]["human"]:
                    self._ai_turn(nxt)
                    if self._winner() is not None:
                        return
                else:
                    # Next human turn
                    self.current = nxt
                    self.turn += 1
                    self.phase = "reinforce"
                    self.pool = self._calc_pool(self.current)
                    self.log.append(f"--- Turn {self.turn}: Your turn ({self.pool} armies to place) ---")
                    return
        # Fallback (only 1 player left, already handled by winner check)
        self.current = alive[0]
        self.phase = "reinforce"
        self.pool = self._calc_pool(self.current)

    def _ai_turn(self, pid):
        """Simple AI: reinforce strongest border, attack weaker neighbors, skip fortify."""
        # Reinforce
        n = self._calc_pool(pid)
        owned = [t for t,d in self.board.items() if d["owner"] == pid]
        if not owned:
            return
        # Pick the territory with the most enemy neighbours
        frontier = sorted(owned,
            key=lambda t: sum(1 for n in ADJACENCY.get(t,[]) if self.board[n]["owner"] != pid),
            reverse=True)
        self.board[frontier[0]]["armies"] += n
        self.log.append(f"{self.players[pid]['name']} reinforced {frontier[0]} (+{n})")

        # Attack up to 8 times
        for _ in range(8):
            options = []
            for t in [t for t,d in self.board.items() if d["owner"]==pid and d["armies"]>=2]:
                for nb in ADJACENCY.get(t,[]):
                    if self.board[nb]["owner"] != pid:
                        options.append((t, nb))
            if not options:
                break
            # Pick attack where attacker has most advantage
            options.sort(key=lambda x: self.board[x[0]]["armies"] - self.board[x[1]]["armies"], reverse=True)
            fr, to = options[0]
            if self.board[fr]["armies"] <= self.board[to]["armies"]:
                break  # AI won't attack if not favoured
            atk_dice = min(3, self.board[fr]["armies"] - 1)
            def_dice = min(2, self.board[to]["armies"])
            atk_rolls = sorted([random.randint(1,6) for _ in range(atk_dice)], reverse=True)
            def_rolls = sorted([random.randint(1,6) for _ in range(def_dice)], reverse=True)
            atk_loss = def_loss = 0
            for a, d in zip(atk_rolls, def_rolls):
                if a > d: def_loss += 1
                else:     atk_loss += 1
            self.board[fr]["armies"] -= atk_loss
            self.board[to]["armies"] -= def_loss
            if self.board[to]["armies"] <= 0:
                old = self.board[to]["owner"]
                moved = max(1, atk_dice - atk_loss)
                self.board[to]["owner"] = pid
                self.board[to]["armies"] = moved
                self.board[fr]["armies"] = max(1, self.board[fr]["armies"] - moved)
                card = random.choice(["infantry","cavalry","artillery","wild"])
                self.players[pid]["cards"].append(card)
                if not [t for t,d in self.board.items() if d["owner"]==old]:
                    self.players[old]["eliminated"] = True
                    self.players[pid]["cards"].extend(self.players[old]["cards"])
                    self.players[old]["cards"] = []
                    self.log.append(f"{self.players[pid]['name']} eliminated {self.players[old]['name']}")
                if self._winner() is not None:
                    return

    def _path(self, src, dst, pid):
        """BFS: is dst reachable from src through pid-owned territories?"""
        visited, queue = {src}, [src]
        while queue:
            cur = queue.pop(0)
            if cur == dst:
                return True
            for nb in ADJACENCY.get(cur, []):
                if nb not in visited and self.board[nb]["owner"] == pid:
                    visited.add(nb)
                    queue.append(nb)
        return False
