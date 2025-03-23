class Trainer:
    def __init__(self, name, team):
        self.name = name
        self.team = team  # List of up to 6 Pokémon
        self.active_pokemon = 0  # Index of the currently active Pokémon

    def get_active_pokemon(self):
        """Returns the currently active Pokémon."""
        return self.team[self.active_pokemon]
    
    def switch_pokemon(self, index):
        """Switch to another Pokémon in the team."""
        if not (0 <= index < len(self.team)):
            print("Invalid switch! Choose a valid Pokémon index.")
            return False
        if index == self.active_pokemon:
            print(f"{self.name}, {self.team[index].name} is already active!")
            return False
        if self.team[index].is_fainted():
            print(f"{self.name} cannot switch to {self.team[index].name}, it has fainted!")
            return False

        self.active_pokemon = index
        print(f"{self.name} switched to {self.team[index].name}!")
        return True
    
    def has_pokemon_left(self):
        """Check if the trainer has at least one non-fainted Pokémon left."""
        return any(not p.is_fainted() for p in self.team)
    
    # Count only non-fainted Pokémon
    def active_pokemon_count(self):
        return sum(1 for pokemon in self.team if pokemon.hp > 0)

    def __str__(self):
        """Display Trainer name and their Pokémon team."""
        team_status = "\n".join(f"- {p.name} (HP: {p.hp}/{p.max_hp})" for p in self.team)
        return f"Trainer {self.name}:\n{team_status}"
