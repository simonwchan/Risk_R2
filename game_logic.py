import random
from game_data import (CONTINENTS, ALL_TERRITORIES, TERRITORY_TO_CONTINENT,
                       ADJACENCIES, PLAYER_COLORS, AI_NAMES)

class Territory:
    def __init__(self, name):
        self.name = name
        self.owner = None
        self.armies = 0
        self.continent = TERRITORY_TO_CONTINENT[name]

class Player:
    def __init__(self, pid, name, color, is_human=False):
        self.id = pid
        self.name = name
        self.color = color
        self.is_human = is_human
        self.cards = []
        self.eliminated = False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "is_human": self.is_human,
            "cards": self.cards,
            "eliminated": self.eliminated
        }

class Game:
    CARD_SETS_TRADED = 0
    CARD_VALUES = [4, 6, 8, 10, 12, 15]

    def __init__(self, num_ai_players):
        self.territories = {name: Territory(name) for name in ALL_TERRITORIES}
        self.players = []
        self.current_player_idx = 0
        self.phase = "setup"  # setup, reinforce, attack, fortify
        self.turn_number = 0
        self.winner = None
        self.attack_log = []
        self.cards_traded_count = 0
        self.pending_territory_bonus = 0  # armies gained from conquering this turn
        self.conquered_this_turn = False
        self._setup_players(num_ai_players)
        self._distribute_territories()

    def _setup_players(self, num_ai):
        # Human player first
        human = Player(0, "You", PLAYER_COLORS[0], is_human=True)
        self.players.append(human)
        ai_names = random.sample(AI_NAMES, min(num_ai, len(AI_NAMES)))
        for i in range(num_ai):
            ai = Player(i+1, ai_names[i % len(ai_names)], PLAYER_COLORS[i+1])
            self.players.append(ai)

    def _distribute_territories(self):
        terr_list = list(ALL_TERRITORIES)
        random.shuffle(terr_list)
        total_players = len(self.players)
        # Starting armies based on player count
        starting_armies = max(20, 50 - (total_players * 5))

        for idx, name in enumerate(terr_list):
            player = self.players[idx % total_players]
            self.territories[name].owner = player.id
            self.territories[name].armies = 1

        # Distribute remaining armies
        for player in self.players:
            my_terrs = [t for t in self.territories.values() if t.owner == player.id]
            extra = starting_armies - len(my_terrs)
            for _ in range(extra):
                t = random.choice(my_terrs)
                t.armies += 1

        self.phase = "reinforce"
        self.turn_number = 1

    def get_state(self):
        terr_data = {}
        for name, t in self.territories.items():
            terr_data[name] = {
                "owner": t.owner,
                "armies": t.armies,
                "continent": t.continent
            }

        player_data = [p.to_dict() for p in self.players]

        # Count territories per player
        for p in player_data:
            p["territory_count"] = sum(1 for t in self.territories.values() if t.owner == p["id"])
            p["army_count"] = sum(t.armies for t in self.territories.values() if t.owner == p["id"])

        return {
            "territories": terr_data,
            "players": player_data,
            "current_player": self.current_player_idx,
            "phase": self.phase,
            "turn": self.turn_number,
            "winner": self.winner,
            "attack_log": self.attack_log[-10:],
            "continents": {k: {"bonus": v["bonus"], "color": v["color"]} for k, v in CONTINENTS.items()},
            "adjacencies": ADJACENCIES,
            "cards_traded_count": self.cards_traded_count,
            "conquered_this_turn": self.conquered_this_turn,
        }

    def calculate_reinforcements(self, player_id):
        my_terrs = [t for t in self.territories.values() if t.owner == player_id]
        armies = max(3, len(my_terrs) // 3)
        # Continent bonuses
        for cont, data in CONTINENTS.items():
            if all(self.territories[t].owner == player_id for t in data["territories"]):
                armies += data["bonus"]
        return armies

    def reinforce(self, player_id, territory, armies):
        if self.phase != "reinforce":
            return {"error": "Not reinforce phase"}
        if self.players[self.current_player_idx].id != player_id:
            return {"error": "Not your turn"}
        t = self.territories.get(territory)
        if not t or t.owner != player_id:
            return {"error": "Invalid territory"}

        t.armies += armies
        self.attack_log.append(f"{self.players[self.current_player_idx].name} reinforced {territory} with {armies} armies")
        self.phase = "attack"
        return {"success": True}

    def attack(self, attacker_id, from_terr, to_terr, num_dice):
        if self.phase != "attack":
            return {"error": "Not attack phase"}
        if self.players[self.current_player_idx].id != attacker_id:
            return {"error": "Not your turn"}

        ft = self.territories.get(from_terr)
        tt = self.territories.get(to_terr)

        if not ft or not tt:
            return {"error": "Invalid territory"}
        if ft.owner != attacker_id:
            return {"error": "You don't own attack territory"}
        if tt.owner == attacker_id:
            return {"error": "Can't attack own territory"}
        if to_terr not in ADJACENCIES.get(from_terr, []):
            return {"error": "Territories not adjacent"}
        if ft.armies < 2:
            return {"error": "Need at least 2 armies to attack"}

        # Cap dice
        atk_dice = min(num_dice, ft.armies - 1, 3)
        def_dice = min(2, tt.armies)

        atk_rolls = sorted([random.randint(1, 6) for _ in range(atk_dice)], reverse=True)
        def_rolls = sorted([random.randint(1, 6) for _ in range(def_dice)], reverse=True)

        atk_losses = 0
        def_losses = 0
        for a, d in zip(atk_rolls, def_rolls):
            if a > d:
                def_losses += 1
            else:
                atk_losses += 1

        ft.armies -= atk_losses
        tt.armies -= def_losses

        result = {
            "atk_rolls": atk_rolls,
            "def_rolls": def_rolls,
            "atk_losses": atk_losses,
            "def_losses": def_losses,
            "conquered": False,
            "attacker_name": self.players[self.current_player_idx].name,
            "from": from_terr,
            "to": to_terr,
        }

        log_line = f"{self.players[self.current_player_idx].name} attacked {to_terr} from {from_terr}: [{','.join(map(str,atk_rolls))}] vs [{','.join(map(str,def_rolls))}]"

        if tt.armies <= 0:
            # Conquered!
            defender_id = tt.owner
            tt.owner = attacker_id
            tt.armies = atk_dice - atk_losses  # move attacking dice worth of armies
            if tt.armies < 1:
                tt.armies = 1
            result["conquered"] = True
            result["moved_armies"] = tt.armies
            self.conquered_this_turn = True
            log_line += f" → CONQUERED!"

            # Give attacker a card
            card = random.choice(["infantry", "cavalry", "artillery", "wild"])
            self.players[self.current_player_idx].cards.append(card)

            # Check elimination
            defender_terrs = [t for t in self.territories.values() if t.owner == defender_id]
            if not defender_terrs:
                self.players[defender_id].eliminated = True
                log_line += f" {self._player_name(defender_id)} eliminated!"
                result["eliminated"] = self._player_name(defender_id)
                # Winner takes their cards
                self.players[self.current_player_idx].cards.extend(self.players[defender_id].cards)
                self.players[defender_id].cards = []

            # Check win condition
            active = [p for p in self.players if not p.eliminated]
            if len(active) == 1:
                self.winner = active[0].id
                result["winner"] = active[0].name

        self.attack_log.append(log_line)
        result["log"] = log_line
        return result

    def end_attack(self, player_id):
        if self.players[self.current_player_idx].id != player_id:
            return {"error": "Not your turn"}
        self.phase = "fortify"
        return {"success": True}

    def fortify(self, player_id, from_terr, to_terr, armies):
        if self.phase != "fortify":
            return {"error": "Not fortify phase"}
        if self.players[self.current_player_idx].id != player_id:
            return {"error": "Not your turn"}

        ft = self.territories.get(from_terr)
        tt = self.territories.get(to_terr)

        if not ft or not tt:
            return {"error": "Invalid territory"}
        if ft.owner != player_id or tt.owner != player_id:
            return {"error": "Must own both territories"}
        if ft.armies <= armies:
            return {"error": "Not enough armies"}
        if not self._connected(from_terr, to_terr, player_id):
            return {"error": "Territories not connected through your own"}

        ft.armies -= armies
        tt.armies += armies
        self.attack_log.append(f"{self.players[self.current_player_idx].name} fortified {to_terr} from {from_terr} with {armies}")
        self._end_turn()
        return {"success": True}

    def skip_fortify(self, player_id):
        if self.players[self.current_player_idx].id != player_id:
            return {"error": "Not your turn"}
        self._end_turn()
        return {"success": True}

    def trade_cards(self, player_id, card_indices):
        player = self.players[player_id]
        if len(card_indices) != 3:
            return {"error": "Must trade exactly 3 cards"}

        cards = [player.cards[i] for i in sorted(card_indices, reverse=True)]
        # Validate set: all same or all different or has wild
        types = set(c for c in cards if c != "wild")
        wilds = sum(1 for c in cards if c == "wild")

        valid = False
        if wilds >= 1:
            valid = True
        elif len(types) == 3:  # all different
            valid = True
        elif len(types) == 1:  # all same
            valid = True

        if not valid:
            return {"error": "Invalid card combination"}

        for i in sorted(card_indices, reverse=True):
            player.cards.pop(i)

        self.cards_traded_count += 1
        n = self.cards_traded_count
        if n <= 6:
            bonus = [4, 6, 8, 10, 12, 15][n-1]
        else:
            bonus = 15 + (n - 6) * 5

        return {"success": True, "bonus_armies": bonus}

    def _end_turn(self):
        active = [p for p in self.players if not p.eliminated]
        idx_in_active = next(i for i, p in enumerate(active) if p.id == self.players[self.current_player_idx].id)
        next_active = active[(idx_in_active + 1) % len(active)]
        self.current_player_idx = next_active.id
        self.phase = "reinforce"
        self.conquered_this_turn = False
        self.turn_number += 1

        # If next player is AI, do AI turn
        if not next_active.is_human and not self.winner:
            self._do_ai_turn(next_active)

    def _do_ai_turn(self, player):
        # AI Reinforce
        reinforce_count = self.calculate_reinforcements(player.id)
        my_terrs = [t for t in self.territories.values() if t.owner == player.id]
        if not my_terrs:
            return

        # Reinforce territory with most neighbors
        best = max(my_terrs, key=lambda t: len([
            n for n in ADJACENCIES.get(t.name, [])
            if self.territories[n].owner != player.id
        ]))
        best.armies += reinforce_count
        self.attack_log.append(f"{player.name} reinforced {best.name} with {reinforce_count}")
        self.phase = "attack"

        # AI Attack
        for _ in range(random.randint(3, 10)):
            my_terrs = [t for t in self.territories.values() if t.owner == player.id and t.armies >= 2]
            if not my_terrs:
                break
            attacker = random.choice(my_terrs)
            neighbors = [
                self.territories[n] for n in ADJACENCIES.get(attacker.name, [])
                if self.territories[n].owner != player.id
            ]
            if not neighbors:
                continue
            target = min(neighbors, key=lambda t: t.armies)
            if attacker.armies > target.armies + 1:
                result = self.attack(player.id, attacker.name, target.name, 3)
                if self.winner:
                    return

        self.phase = "fortify"

        # AI Fortify - simple: move armies toward frontier
        self._end_turn()

    def _connected(self, from_t, to_t, player_id):
        visited = set()
        stack = [from_t]
        while stack:
            curr = stack.pop()
            if curr == to_t:
                return True
            visited.add(curr)
            for n in ADJACENCIES.get(curr, []):
                if n not in visited and self.territories[n].owner == player_id:
                    stack.append(n)
        return False

    def _player_name(self, pid):
        for p in self.players:
            if p.id == pid:
                return p.name
        return "Unknown"
