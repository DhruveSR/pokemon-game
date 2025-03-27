import random
import pickle
from re import L
import numpy as np

# Import your existing modules
from pokemon import Pokemon
from trainer import Trainer
from battle_logic import calculate_damage, perform_move
import battle_ai  # Baseline AI from your battle_ai.py
import typeRelation

# -------------------- Q-LEARNING HYPERPARAMETERS -------------------- #
ALPHA = 0.1      # Learning rate
GAMMA = 0.9      # Discount factor
EPSILON = 0.1    # Exploration rate

# Global Q-table: key = (state, action), value = Q-value
Q_table = {}

# -------------------- UTILITY FUNCTIONS -------------------- #
def get_Q(state, action):
    """Retrieve Q-value for a given state-action pair (defaulting to 0)."""
    return Q_table.get((state, action), 0)

def update_Q(state, action, reward, next_state, moves):
    """Update Q-value for the state-action pair using the Q-learning formula."""
    max_future_q = max([get_Q(next_state, m) for m in moves], default=0)
    current_q = get_Q(state, action)
    Q_table[(state, action)] = current_q + ALPHA * (reward + GAMMA * max_future_q - current_q)

def save_Q_table(filename="q_table.pkl"):
    """Persist the Q-table to disk."""
    with open(filename, "wb") as f:
        pickle.dump(Q_table, f)

def load_Q_table(filename="q_table.pkl"):
    """Load the Q-table from disk."""
    global Q_table
    try:
        with open(filename, "rb") as f:
            Q_table = pickle.load(f)
    except FileNotFoundError:
        print("No Q-table found, starting fresh.")

def encode_state(attacker, defender):
    """
    Encode the battle state as a tuple.
    State includes: attacker HP, defender HP, attacker types, defender types, attacker status, defender status.
    """
    return (
        attacker.hp,
        defender.hp,
        tuple(attacker.typing),
        tuple(defender.typing),
        attacker.status,
        defender.status
    )

def choose_move_RL(state, attacker, last_move):
    """
    Choose a move based on an ε-greedy policy:
      - With probability EPSILON, select a random move.
      - Otherwise, select the move with the highest Q-value.
    """
    if last_move and attacker.item["name"] in ["choice-band", "choice-scarf", "choice-specs"]:
        return last_move

    moves = list(attacker.moves.keys())
    if random.uniform(0, 1) < EPSILON:
        chosen = random.choice(moves)
        print(f"[RL] Exploration: Randomly selected move '{chosen}'")
        return chosen
    else:
        chosen = max(moves, key=lambda m: get_Q(state, m))
        print(f"[RL] Exploitation: Selected best move '{chosen}' with Q-value {get_Q(state, chosen):.2f}")
        return chosen

def calculate_reward(attacker, defender, move, estimated_damage):
    """
    Calculate a reward based on the move's effectiveness.
    Rewards:
      - KO move: +50
      - STAB bonus: +10
      - Super effective: +30 per multiplier
      - Not very effective: -20 per factor
      - No effect: -50
      - Bonus for status or healing moves similar to baseline evaluation.
    """
    reward = 0
    # If move can KO the opponent, bonus reward
    if estimated_damage >= defender.hp:
        reward += 50

    # STAB bonus
    if move["type"] in attacker.typing:
        reward += 10

    effectiveness = 1
    # Type effectiveness evaluation
    for d_type in defender.typing:
        effectiveness *= typeRelation.type_relation[move["type"]].get(d_type, 1)
        
    if effectiveness == 4:
        reward += 40
    elif effectiveness == 2:
        reward += 20
    elif effectiveness == 0.5:
        reward -= 20
    elif effectiveness == 0.25:
        reward -= 40
    elif effectiveness == 0:
        reward -= 100

    # Reward status moves if applicable
    if move["statusChange"] and defender.status is None:
        status_effect = move["statusChange"][0]
        if status_effect == "paralyze" and defender.current_stats["speed"] > attacker.current_stats["speed"]:
            reward += 20
        elif status_effect == "burn" and defender.current_stats["attack"] > defender.current_stats["sp_attack"]:
            reward += 20
        elif status_effect == "toxic":
            reward += 25

    if move["statusChange"] and defender.status is not None:
        reward -= 100

    # Reward healing if HP is low
    if move["heals"] and attacker.hp <= attacker.max_hp * 0.5:
        reward += 40

    print(f"[Reward] Move '{move['name']}' generated reward: {reward}")
    return reward

# -------------------- RL-BASED BATTLE AI FUNCTION -------------------- #
def battleAI_RL(attacker, defender, last_move):
    """
    Reinforcement Learning-based move selection.
    1. Encode current state.
    2. Choose a move using the ε-greedy policy.
    3. Estimate damage and calculate reward.
    4. Update Q-table based on the transition.
    5. Return the chosen move.
    """
    state = encode_state(attacker, defender)
    move_name = choose_move_RL(state, attacker, last_move)
    move = attacker.moves[move_name]

    # Estimate damage (for reward calculation) but note that perform_move will change the state
    estimated_damage = calculate_damage(attacker, defender, move)
    print(f"[RL] Estimated damage by '{move['name']}': {estimated_damage}")

    # Execute the move and log the outcome
    perform_move(attacker, defender, move)

    # Calculate reward based on move outcome
    reward = calculate_reward(attacker, defender, move, estimated_damage)

    # Get new state after executing the move
    next_state = encode_state(attacker, defender)
    
    # Update Q-table using the attacker's available moves
    update_Q(state, move_name, reward, next_state, list(attacker.moves.keys()))
    
    print(f"[RL] Updated Q-value for state {state} and action '{move_name}': {get_Q(state, move_name):.2f}")
    return move_name

# -------------------- SIMULATION LOOP -------------------- #
def simulate_battle_RL(rl_trainer, opp_trainer):
    """
    Simulate a simplified battle between two trainers with alternating roles.
    On odd turns, the RL-controlled trainer (e.g., Charizard) attacks first.
    On even turns, the opponent (e.g., Blastoise) attacks first.
    Logs are printed for each battle and move, including updated HP after each move.
    Note: For training, this simulation assumes no switching.
    """
    print("\n" + "="*40)
    print("Starting new battle simulation")
    print("="*40)

    # Reset active Pokémon to full HP
    agent = rl_trainer.get_active_pokemon()
    opp = opp_trainer.get_active_pokemon()
    agent.hp = agent.max_hp
    opp.hp = opp.max_hp

    turn = 1
    lastmove1 = None
    lastmove2 = None
    # Run battle loop until one Pokémon faints
    while not agent.is_fainted() and not opp.is_fainted():
        if turn >=10:
            break
        print(f"\n--- Turn {turn} ---")
        print(f"{agent.name} HP: {agent.hp}/{agent.max_hp}")
        print(f"{opp.name} HP: {opp.hp}/{opp.max_hp}")
        
        if turn % 2 == 1:
            # Odd turn: RL agent attacks first
            print(f"[Turn Order] {agent.name} (RL Agent) attacks first.")
            if agent.item["name"] in ["choice-band", "choice-scarf", "choice-specs"] and lastmove1:
                move_rl = lastmove1
            else:
                move_rl = battleAI_RL(agent, opp, lastmove1)
                lastmove1 = move_rl

            print(f"{agent.name} (RL Agent) used '{move_rl}'.")
            print(f"After move, {opp.name} HP: {opp.hp}/{opp.max_hp}")
            if opp.is_fainted():
                print(f"{opp.name} fainted!")
                break

            # Opponent selects and executes its move
            move_opp = battle_ai.battleAI(opp, agent, lastmove2)
            lastmove2 = move_opp
            
            # Execute opponent's move
            perform_move(opp, agent, opp.moves[move_opp])
            print(f"{opp.name} (Opponent) used '{move_opp}'.")
            print(f"After move, {agent.name} HP: {agent.hp}/{agent.max_hp}")
            if agent.is_fainted():
                print(f"{agent.name} fainted!")
                break
        else:
            # Even turn: Opponent attacks first
            print(f"[Turn Order] {opp.name} (Opponent) attacks first.")
            move_opp = battle_ai.battleAI(opp, agent, lastmove2)
            lastmove2 = move_opp
            perform_move(opp, agent, opp.moves[move_opp])
            print(f"{opp.name} (Opponent) used '{move_opp}'.")
            print(f"After move, {agent.name} HP: {agent.hp}/{agent.max_hp}")
            if agent.is_fainted():
                print(f"{agent.name} fainted!")
                break

            move_rl = battleAI_RL(agent, opp, lastmove1)
            lastmove1 = move_rl
            print(f"{agent.name} (RL Agent) used '{move_rl}'.")
            print(f"After move, {opp.name} HP: {opp.hp}/{opp.max_hp}")
            if opp.is_fainted():
                print(f"{opp.name} fainted!")
                break

        turn += 1

    # Terminal reward: bonus or penalty based on battle outcome
    if opp.is_fainted():
        final_reward = 100
        print(f"\nBattle result: {agent.name} wins!")
    else:
        final_reward = -100
        print(f"\nBattle result: {opp.name} wins!")
    
    # Update Q for terminal state (using the last RL move)
    final_state = encode_state(agent, opp)
    update_Q(final_state, move_rl, final_reward, final_state, list(agent.moves.keys()))
    print(f"[Final Update] Terminal reward applied. Final Q-value for move '{move_rl}': {get_Q(final_state, move_rl):.2f}")
    
    print("="*40 + "\n")
    # Return outcome: True if RL agent wins
    return not agent.is_fainted()

# -------------------- TRAINING LOOP -------------------- #
from battle_test import charizard, blastoise, venusaur, pikachu, snorlax, alakazam, gengar, dragonite, mewtwo, tauros, mew, gyarados
def train_RL_agent(episodes=50):
    """
    Train the RL agent by simulating multiple battles.
    Logs are printed for each battle.
    Adjust the number of episodes as needed.
    """
    load_Q_table()
    pokemons = [charizard, blastoise, venusaur, pikachu, snorlax, alakazam, gengar, dragonite, mewtwo, tauros, mew, gyarados]
    for rl_agent in pokemons:
        for base_poke in pokemons:
            wins = 0
            for episode in range(episodes):
                # For training, create new trainers with fresh copies of Pokémon.
                # Using helper functions to generate new instances.
                rl_trainer = Trainer("RL_Agent", [rl_agent_pokemon(rl_agent)])
                opp_trainer = Trainer("Baseline", [baseline_pokemon(base_poke)])
                
                print(f"=== Episode {episode+1} ===")
                result = simulate_battle_RL(rl_trainer, opp_trainer)
                if result:
                    wins += 1
                
                print(f"Episode {episode+1} complete. Cumulative win rate: {wins / (episode+1):.2f}\n")
    
    save_Q_table()
    print("Training complete. Q-table saved.")

# -------------------- HELPER FUNCTIONS TO GENERATE POKÉMON -------------------- #
def rl_agent_pokemon(rl_agent):
    """
    Returns a fresh instance of a Pokémon for the RL agent.
    Adjust to choose your preferred Pokémon.
    """
    from pokemon import Pokemon
    from battle_test import copy_pokemon # Assuming charizard is defined in battle_test.py
    return copy_pokemon(rl_agent)

def baseline_pokemon(base_poke):
    """
    Returns a fresh instance of a Pokémon for the baseline opponent.
    Adjust this function as necessary.
    """
    from pokemon import Pokemon
    from battle_test import copy_pokemon  # Assuming blastoise is defined in battle_test.py
    return copy_pokemon(base_poke)

# -------------------- MAIN ENTRY POINT -------------------- #
if __name__ == "__main__":
    # Set the number of training episodes as desired.
    train_RL_agent(episodes=10000)
