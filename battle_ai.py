import random
import typeRelation
from battle_logic import calculate_damage

def battleAI(attacker, defender, last_move):
    """
    Decision-making for selecting the best move in battle.
    - Prioritizes moves that deal the most damage.
    - Uses status moves strategically.
    - Prefers healing moves when HP is low.
    """

    if attacker.item["name"] in ["choice-band", "choice-scarf", "choice-specs"] and last_move:
        return last_move

    move_scores = {}

    for move_name, move in attacker.moves.items():
        score = 0

        # Check Type Effectiveness
        effectiveness = 1
        for defender_type in defender.typing:
            effectiveness *= typeRelation.type_relation[move["type"]].get(defender_type, 1)

            if effectiveness > 1:
                score += 30 * effectiveness  # Higher score for super-effective moves
            elif effectiveness == 0:
                score -= 50  # Penalize moves that have no effect
            elif effectiveness < 1:
                score -= 20 * (1 / effectiveness)  # Further reduce score for resisted moves

        # Check if Move Can KO the Opponent
        estimated_damage = calculate_damage(attacker, defender, move)
        if estimated_damage >= defender.hp:
            score += 50  # Prioritize KO moves

        # Check STAB (Same-Type Attack Bonus)
        if move["type"] in attacker.typing:
            score += 10  # Small boost for STAB moves

        # Check if Move Has High Power
        if move["power"]:
            score += move["power"] // 2  # Higher power gets a boost

        # Check Status Moves
        if move["statusChange"][0] and defender.status is None:
            status_effect = move["statusChange"][1]

            # Prefer paralysis against fast Pokémon
            if status_effect == "paralyze" and defender.current_stats["speed"] > attacker.current_stats["speed"]:
                score += 20  

            # Prefer burn against physical attackers
            elif status_effect == "burn" and defender.current_stats["attack"] > defender.current_stats["sp_attack"]:
                score += 20  

            # Toxic for stalling strategies
            elif status_effect == "toxic":
                score += 25  

        # Check Healing Moves
        if move["heals"][0] and attacker.hp <= attacker.max_hp * 0.5:
            score += 40  # Healing is more important when HP is low

        move_scores[move_name] = score

    # **Choose the Best Move**
    best_move = max(move_scores, key=move_scores.get, default=random.choice(list(attacker.moves.keys())))
    
    return best_move
