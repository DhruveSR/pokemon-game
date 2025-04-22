import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from models.pokemon.pokemon_inbattle import PokemonInBattle
from models.pokemon.move import Move, create_move

@dataclass
class BattleState:
    """Manages the state of a Pokémon battle, including turn order, effects, and battle progression."""

    trainer_pokemon: List[PokemonInBattle]  # Pokémon for the player's side
    opponent_pokemon: List[PokemonInBattle]  # Pokémon for the opponent's side
    weather: Optional[str] = None  # Current weather condition (Rain, Sun, etc.)
    terrain: Optional[str] = None  # Current battlefield terrain (Grassy, Misty, etc.)
    field_effects: Dict[str, int] = field(default_factory=dict)  # Ongoing field effects (turn counters)
    turn_count: int = 0  # Tracks the number of turns elapsed
    battle_over: bool = False  # Flag to indicate if the battle is over

    def apply_field_effect(self, effect: str, duration: int):
        """Apply a field effect like Trick Room, Tailwind, or Screens."""
        self.field_effects[effect] = duration

    def decrement_field_effects(self):
        """Reduce the turn counters for field effects and remove expired effects."""
        expired_effects = [effect for effect, turns in self.field_effects.items() if turns <= 1]
        for effect in expired_effects:
            del self.field_effects[effect]
        for effect in self.field_effects:
            self.field_effects[effect] -= 1

    
    def get_move_priority(self, move_name, user: PokemonInBattle):
        move = create_move(move_name)
        priority = move.priority
        if user.pokemon.ability == "prankster" and move.category == "status":
            priority +=1
        if user.pokemon.ability == "triage" and (move.heals or move.damage_heals):
            priority +=1
        if user.pokemon.ability == "stall":
            priority -=7

        return priority


    def get_turn_order(self, move_choices: Dict[PokemonInBattle, str]):
        """
        Determine the turn order based on move priority, Speed, Trick Room,
        Quick Draw, Quick Claw, and Custap Berry.

        :param move_choices: Dictionary mapping each Pokémon to their selected move.
        :return: List of Pokémon in the order they will act.
        """
        all_pokemon = self.trainer_pokemon + self.opponent_pokemon

        # Get priority levels for each Pokémon based on their selected move
        priority_map = {
            pkmn: self.get_move_priority(move_choices.get(pkmn, "Struggle"), pkmn) 
            for pkmn in all_pokemon
        }

        # Determine if Quick Draw, Quick Claw, or Custap Berry activates
        quick_effects = {}
        for pkmn in all_pokemon:
            move = create_move(move_choices.get(pkmn, "Struggle"))
            is_damaging = move.category != "status"

            # Check Quick Draw first (supersedes other effects)
            quick_draw_activated = (
                is_damaging and 
                pkmn.pokemon.ability == "quick-draw" and 
                random.random() <= 0.3
            )

            # Only check other effects if Quick Draw didn't activate
            if not quick_draw_activated:
                # Check Custap Berry before Quick Claw (consumed at turn start)
                custap_activated = (
                    pkmn.pokemon.item == "custap-berry" and
                    (pkmn.pokemon.current_hp / pkmn.pokemon.actual_stats["hp"] <= 
                    (0.5 if pkmn.pokemon.ability == "gluttony" else 0.25))
                )
                # Quick Claw only checked if Custap didn't activate
                quick_claw_activated = (
                    not custap_activated and
                    pkmn.pokemon.item == "quick-claw" and
                    random.random() <= 0.2
                )
            else:
                custap_activated = quick_claw_activated = False

            # Store effect priority (2: Quick Draw, 1: Custap/Quick Claw, 0: none)
            quick_effects[pkmn] = (
                2 if quick_draw_activated else
                1 if custap_activated or quick_claw_activated else
                0
            )

            # Consume Custap Berry if activated
            if custap_activated:
                pkmn.pokemon.item = None

        # Sort by priority first, then by Quick effects, then Speed (adjusted for Trick Room)
        def sort_key(pkmn: PokemonInBattle):
            return (
                priority_map[pkmn],  # Primary sort: Move priority
                quick_effects[pkmn],  # Secondary sort: Quick effects
                -pkmn.current_stats["Spe"] if "trick-room" in self.field_effects 
                    else pkmn.current_stats["Spe"],  # Trick Room handling
                random.random()  # Random tiebreaker
            )

        return sorted(all_pokemon, key=sort_key, reverse=True)


    def execute_turn(self, move_choices: Dict[PokemonInBattle, str]):
        """
        Execute a battle turn, where each Pokémon uses a selected move.

        :param move_choices: Dictionary mapping each Pokémon to their selected move.
        """
        if self.battle_over:
            return

        self.turn_count += 1
        turn_order = self.get_turn_order()

        for pokemon in turn_order:
            if pokemon.pokemon.current_hp > 0:  # Only active Pokémon can act
                move_name = move_choices.get(pokemon, "Struggle")  # Default to Struggle if no move selected
                print(f"{pokemon.pokemon.name} used {move_name}!")
                # TODO: Implement actual move execution logic

        # Apply end-of-turn effects (e.g., weather damage, status conditions)
        self.end_of_turn_effects()

        # Check for win condition
        self.check_win_condition()

    def end_of_turn_effects(self):
        """Handle end-of-turn effects like weather damage, status conditions, and field durations."""
        # Decrement field effects
        self.decrement_field_effects()

        # Apply weather damage (Sandstorm/Hail)
        if self.weather in ["sandstorm", "hail"]:
            for pokemon in self.trainer_pokemon + self.opponent_pokemon:
                if pokemon.pokemon.current_hp > 0 and not pokemon.pokemon.immune_to_weather(self.weather):
                    pokemon.take_damage(max(1, pokemon.pokemon.actual_stats["HP"] // 16))
                    print(f"{pokemon.pokemon.pokemon_dex_info.name} took damage from {self.weather}!")

        # Apply status damage (Burn, Poison)
        for pokemon in self.trainer_pokemon + self.opponent_pokemon:
            if pokemon.pokemon.status == "burn":
                pokemon.take_damage(max(1, pokemon.pokemon.actual_stats["HP"] // 16))
                print(f"{pokemon.pokemon.pokemon_dex_info.name} is hurt by its burn!")
            elif pokemon.pokemon.status == "poison":
                pokemon.take_damage(max(1, pokemon.pokemon.actual_stats["HP"] // 8))
                print(f"{pokemon.pokemon.pokemon_dex_info.name} is hurt by poison!")

    def check_win_condition(self):
        """Check if either team has won the battle."""
        trainer_alive = any(p.pokemon.current_hp > 0 for p in self.trainer_pokemon)
        opponent_alive = any(p.pokemon.current_hp > 0 for p in self.opponent_pokemon)

        if not trainer_alive:
            print("The player has lost the battle!")
            self.battle_over = True

        elif not opponent_alive:
            print("The opponent has no Pokémon left! The player wins!")
            self.battle_over = True
