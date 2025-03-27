from battle_logic import apply_status_damage, perform_move, select_order, reset_toxic_counter
from battle_ai import battleAI

# ---------------------- POKEMON BATTLE ---------------------- #

def pokemon_battle(trainer1, trainer2):
    """Simulate a Pokémon battle between two trainers."""
    
    print(f"Battle Start! {trainer1.name} vs {trainer2.name}\n")
    pokemon1_known_moves = set()  # Track moves used by Pokémon 1 for AI predictions

    # Get each trainer’s active Pokémon
    pokemon1, pokemon2 = trainer1.get_active_pokemon(), trainer2.get_active_pokemon()
    
    # Check if any items activate upon switching in
    pokemon1.check_item_use(pokemon2, "switch")
    pokemon1.check_ability_use(pokemon2, "switch")
    pokemon2.check_item_use(pokemon1, "switch")
    pokemon2.check_ability_use(pokemon1, "switch")

    last_move1 = None  # Track Pokémon 1's last move (for Choice items)
    last_move2 = None  # Track Pokémon 2's last move (for Choice items)

    # Battle loop continues while both trainers have usable Pokémon
    while trainer1.has_pokemon_left() and trainer2.has_pokemon_left():
        
        pokemon1, pokemon2 = trainer1.get_active_pokemon(), trainer2.get_active_pokemon()

        # AI selects an action for Pokémon 2
        action2 = battleAI(pokemon2, pokemon1, last_move2)
        last_move2 = action2
        
        # Display the current state of the battle
        print(f"{trainer1.name}'s {pokemon1}\n{trainer2.name}'s {pokemon2}\n")
        print(f"{trainer1.name}, choose an action: {', '.join(pokemon1.moves)}, Switch")

        # Player selects an action
        while True:
            action1 = input("Enter action: ").strip().lower()

            if action1 == "switch":
                if trainer1.active_pokemon_count() == 1:
                    print("You only have one Pokémon left! You can't switch.")
                    continue

                priority1 = 10  # Switching has a high priority
                break

            elif action1 in pokemon1.moves:
                # Handle Choice Band/Scarf/Specs restriction (must repeat the same move)
                if pokemon1.item and pokemon1.item in ["choice band", "choice scarf", "choice specs"]:
                    if last_move1 and last_move1 != action1:
                        print(f"{trainer1.name}, you cannot choose another move due to your item!")
                        continue
                
                priority1 = pokemon1.moves[action1]["priority"]  # Get move priority
                last_move1 = action1  # Store move for Choice item enforcement
                break

            else:
                print("Invalid choice. Please choose a correct option.")

        priority2 = pokemon2.moves[action2]["priority"]  # Get move priority for Pokémon 2

        # Determine move order based on priority, speed, and Quick Claw
        order = select_order(priority1, priority2, pokemon1.current_stats["speed"], 
                             pokemon2.current_stats["speed"], pokemon1.item, pokemon2.item)
        
        # Execute moves in determined order
        for turn in order:
            if turn == 1:
                if action1 == "switch":
                    # Handle Pokémon switching
                    while True:
                        try:
                            idx = int(input("Enter index of Pokémon to switch: "))
                            if trainer1.switch_pokemon(idx):
                                pokemon1 = trainer1.get_active_pokemon()
                                pokemon1.current_stats = pokemon1.calc_initial_stats()
                                if pokemon1.status == "paralyze":
                                    pokemon1.current_stats["speed"] = pokemon1.current_stats["speed"]//2
                                pokemon1.check_item_use(pokemon2, "switch")
                                pokemon1.check_ability_use(pokemon2, "switch")
                                reset_toxic_counter(pokemon1)  # Reset toxic counter on switch
                                last_move1 = None  # Reset last move
                                break
                        except ValueError:
                            print("Please enter a valid number.")
                else:
                    # Execute the move
                    perform_move(pokemon1, pokemon2, pokemon1.moves[action1])
                    pokemon1.check_item_use(pokemon2, "attack")
                    pokemon2.check_item_use(pokemon1, "defend")
                    pokemon2.check_ability_use(pokemon1, "defend")
                    pokemon1_known_moves.add(action1)  # Track known moves for AI

                # Check if Pokémon 2 fainted
                if pokemon2.is_fainted():
                    if not trainer2.switch_pokemon(trainer2.active_pokemon + 1):
                        print(f"{trainer1.name} has won the battle!")
                        return
                    else:
                        pokemon2 = trainer2.get_active_pokemon()
                        pokemon2.current_stats = pokemon2.calc_initial_stats()
                        if pokemon2.status == "paralyze":
                            pokemon2.current_stats["speed"] = pokemon2.current_stats["speed"]//2
                        pokemon2.check_item_use(pokemon1, "switch")
                        pokemon2.check_ability_use(pokemon1, "switch")
                        reset_toxic_counter(pokemon2)
                    break
            else:
                # Pokémon 2's turn
                perform_move(pokemon2, pokemon1, pokemon2.moves[action2])
                pokemon1.check_item_use(pokemon2, "defend")
                pokemon1.check_ability_use(pokemon2, "defend")
                pokemon2.check_item_use(pokemon1, "attack")
                
                # Check if Pokémon 1 fainted
                if pokemon1.is_fainted():
                    if trainer1.has_pokemon_left():
                        while True:
                            try:
                                idx = int(input("Enter index of Pokémon to switch: "))
                                if trainer1.switch_pokemon(idx):
                                    pokemon1 = trainer1.get_active_pokemon()
                                    pokemon1.current_stats = pokemon1.calc_initial_stats()
                                    if pokemon1.status == "paralyze":
                                        pokemon1.current_stats["speed"] = pokemon1.current_stats["speed"]//2 
                                    pokemon1.check_item_use(pokemon2, "switch")
                                    pokemon1.check_ability_use(pokemon2, "switch")
                                    reset_toxic_counter(pokemon1)
                                    last_move1 = None
                                    break
                            except ValueError:
                                print("Please enter a valid number.")
                        break
                    else:
                        print(f"{trainer2.name} has won the battle!")
                        return

        # End-of-turn item checks
        pokemon1.check_item_use(pokemon2, "end")
        pokemon1.check_ability_use(pokemon2, "end")
        pokemon2.check_item_use(pokemon1, "end")
        pokemon2.check_ability_use(pokemon1, "end")
        
        # Apply status damage from burn, poison, or badly poisoned effects
        apply_status_damage(pokemon1)
        apply_status_damage(pokemon2)

        # Check if Pokémon 1 fainted
        if pokemon1.is_fainted():
            if trainer1.has_pokemon_left():
                while True:
                    try:
                        idx = int(input("Enter index of Pokémon to switch: "))
                        if trainer1.switch_pokemon(idx):
                            pokemon1 = trainer1.get_active_pokemon()
                            pokemon1.current_stats = pokemon1.calc_initial_stats()
                            if pokemon1.status == "paralyze":
                                pokemon1.current_stats["speed"] = pokemon1.current_stats["speed"]//2 
                            pokemon1.check_item_use(pokemon2, "switch")
                            pokemon1.check_ability_use(pokemon2, "switch")
                            reset_toxic_counter(pokemon1)
                            last_move1 = None
                            break
                    except ValueError:
                        print("Please enter a valid number.")
            else:
                print(f"{trainer2.name} has won the battle!")
                return
        
        # Check if Pokémon 2 fainted
        if pokemon2.is_fainted():
            if not trainer2.switch_pokemon(trainer2.active_pokemon + 1):
                print(f"{trainer1.name} has won the battle!")
                return
            else:
                pokemon2 = trainer2.get_active_pokemon()
                pokemon2.current_stats = pokemon2.calc_initial_stats()
                if pokemon2.status == "paralyze":
                    pokemon2.current_stats["speed"] = pokemon2.current_stats["speed"]//2
                pokemon2.check_item_use(pokemon1, "switch")
                pokemon2.check_ability_use(pokemon1, "switch")
                reset_toxic_counter(pokemon2)

        print("\n---\n")  # Separate turns for readability
