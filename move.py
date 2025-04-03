from typing import Optional, Dict
from dataclasses import dataclass, field

@dataclass
class Move:
    name: str
    info: str
    move_type: str  # "type" is a Python keyword, so renamed to "move_type"
    power: Optional[int] = None  # Some moves don't have power (e.g., status moves)
    accuracy: Optional[int] = 100  # Default accuracy is 100%
    priority: int = 0  # Higher priority moves go first
    multi_hit: Optional[Dict[int, float]] = field(default_factory=dict)  # Hit count mapped to probability
    stat_change: Optional[Dict[str, Dict[str, int]]] = field(default_factory=dict)  # Changes stats of target/user
    status_change: Optional[str] = None  # Applies a status condition (e.g., "paralysis")
    effective_state: Optional[str] = None  # Unique state changes (e.g., "flinch", "confusion")
    heals: Optional[int] = None  # Amount of HP restored (e.g., "Recover" restores 50%)
    damage_heals: Optional[float] = None  # Percentage of damage dealt converted to healing (e.g., "Drain Punch" heals 50%)

    def __str__(self):
        """Return a string representation of the move."""
        move_info = f"{self.name} ({self.move_type} Move)\n"
        move_info += f"Info: {self.info}\n"
        if self.power is not None:
            move_info += f"Power: {self.power}, "
        move_info += f"Accuracy: {self.accuracy}%, Priority: {self.priority}\n"

        return move_info.strip()
