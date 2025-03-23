from collections import defaultdict

# Default to 1x effectiveness if type matchup is missing
type_relation = defaultdict(lambda: defaultdict(lambda: 1.0))

# Add known type matchups
type_relation.update({
    "normal": defaultdict(lambda: 1.0, {"rock": 0.5, "steel": 0.5, "ghost": 0}),
    "fighting": defaultdict(lambda: 1.0, {"normal": 2, "rock": 2, "steel": 2, "ghost": 0, "dark": 2, "fairy": 0.5, "poison": 0.5, "flying": 0.5, "bug": 0.5, "psychic": 0.5, "ice": 2}),
    "flying": defaultdict(lambda: 1.0, {"rock": 0.5, "steel": 0.5, "fighting": 2, "bug": 2, "grass": 2, "electric": 0.5}),
    "poison": defaultdict(lambda: 1.0, {"rock": 0.5, "steel": 0, "ghost": 0.5, "poison": 0.5, "fairy": 2, "grass": 2, "ground": 0.5}),
    "ground": defaultdict(lambda: 1.0, {"rock": 2, "steel": 2, "flying": 0, "poison": 2, "grass": 0.5, "bug": 0.5, "fire": 2, "electric": 2}),
    "rock": defaultdict(lambda: 1.0, {"fighting": 0.5, "steel": 0.5, "flying": 2, "fire": 2, "ice": 2, "ground": 0.5, "bug": 2}),
    "bug": defaultdict(lambda: 1.0, {"rock": 0.5, "steel": 0.5, "fire": 0.5, "flying": 0.5, "fighting": 0.5, "ghost": 0.5, "fairy": 0.5, "grass": 2, "psychic": 2, "dark": 2}),
    "ghost": defaultdict(lambda: 1.0, {"normal": 0, "dark": 0.5, "ghost": 2, "psychic": 2}),
    "steel": defaultdict(lambda: 1.0, {"rock": 2, "steel": 0.5, "fire": 0.5, "water": 0.5, "electric": 0.5, "fairy": 2, "ice": 2}),
    "fire": defaultdict(lambda: 1.0, {"rock": 0.5, "steel": 2, "water": 0.5, "dragon": 0.5, "grass": 2, "bug": 2, "ice": 2, "fire": 0.5}),
    "water": defaultdict(lambda: 1.0, {"rock": 2, "fire": 2, "ground": 2, "grass": 0.5, "dragon": 0.5, "water": 0.5}),
    "grass": defaultdict(lambda: 1.0, {"grass": 0.5, "steel": 0.5, "fire": 0.5, "flying": 0.5, "dragon": 0.5, "poison": 0.5, "bug": 0.5, "rock": 2, "ground": 2, "water": 2}),
    "electric": defaultdict(lambda: 1.0, {"electric": 0.5, "dragon": 0.5, "ground": 0, "flying": 2, "water": 2, "grass": 0.5}),
    "psychic": defaultdict(lambda: 1.0, {"psychic": 0.5, "steel": 0.5, "dark": 0, "poison": 2, "fighting": 2}),
    "ice": defaultdict(lambda: 1.0, {"rock": 0.5, "steel": 0.5, "ice": 0.5, "fire": 0.5, "flying": 2, "grass": 2, "dragon": 2, "ground": 2}),
    "dragon": defaultdict(lambda: 1.0, {"steel": 0.5, "fairy": 0, "dragon": 2}),
    "fairy": defaultdict(lambda: 1.0, {"fire": 0.5, "steel": 0.5, "poison": 0.5, "dragon": 2, "fighting": 2, "dark": 2}),
    "dark": defaultdict(lambda: 1.0, {"fighting": 0.5, "fairy": 0.5, "dark": 0.5, "psychic": 2, "ghost": 2})
})


STATUS_IMMUNITIES = {
    "fire": ["burn"],        # Fire-types cannot be burned
    "electric": ["paralyze"], # Electric-types cannot be paralyzed
    "poison": ["poison", "badly poison"], # Poison-types are immune to poison
    "steel": ["poison", "badly poison"],  # Steel-types are also immune to poison
    "ice": ["freeze"]         # Ice-types cannot be frozen
}

