import random
import pickle

# Load Q-table from a file
Q_table = {}

def load_Q_table(filename="final_qtable/q_table.pkl"):
    """Load the Q-table from disk."""
    global Q_table
    try:
        with open(filename, "rb") as f:
            Q_table = pickle.load(f)
    except FileNotFoundError:
        print("No Q-table found, using default random strategy.")

load_Q_table()  # Load the Q-table when this module is imported

def get_Q(state, action):
    """Retrieve Q-value for a given state-action pair (defaulting to 0)."""
    return Q_table.get((state, action), 0)

def encode_state(attacker, defender):
    """Encode the battle state as a tuple for Q-table lookup."""
    return (
        attacker.hp,
        defender.hp,
        tuple(attacker.typing),
        tuple(defender.typing),
        attacker.status,
        defender.status
    )

def battleAI(attacker, defender, last_move):
    """
    Select the best move based on the learned Q-values without updating them.
    Uses an ε-greedy policy:
      - 10% of the time, select a random move (exploration).
      - 90% of the time, select the move with the highest Q-value (exploitation).
    """
    state = encode_state(attacker, defender)
    moves = list(attacker.moves.keys())

    if last_move and attacker.item["name"] in ["choice-band", "choice-scarf", "choice-specs"]:
        return last_move

    if random.uniform(0, 1) < 0.1:  # 10% exploration
        chosen_move = random.choice(moves)
    else:  # 90% exploitation
        chosen_move = max(moves, key=lambda m: get_Q(state, m))

    return chosen_move
