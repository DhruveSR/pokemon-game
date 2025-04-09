from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
import sqlite3
import json

def create_move(move_name: str):
    """Fetches a move from the SQLite database and returns a Move object."""
    
    db_path = "database/move.db"  # Replace with your actual database path

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, info, move_type, category, power, ignores_accuracy, accuracy, pp, makes_contact, 
                   move_target, priority, multi_hit, stat_modifiers, status_change, heals, 
                   damage_heals
            FROM moves
            WHERE name = ?
        """, (move_name,))
        
        move_data = cursor.fetchone()  # Fetch one record

    if move_data is None:
        raise ValueError(f"Move '{move_name}' not found in database.")

    # Map database fields to Move class
    return Move(
        name=move_data[0],
        info=move_data[1],
        move_type=move_data[2],
        category=move_data[3],
        power=move_data[4],
        ignores_accuracy=bool(move_data[5]),
        accuracy=move_data[6],
        pp=move_data[7],
        makes_contact=bool(move_data[8]),
        move_target=move_data[9],
        priority=move_data[10],
        multi_hit=json.loads(move_data[11]) if move_data[11] else [],
        stat_change=json.loads(move_data[12]) if move_data[12] else {},
        status_change=move_data[13],
        heals=move_data[14],
        damage_heals=move_data[15],
    )

@dataclass
class Move:
    name: str
    info: str
    move_type: str
    category: str
    power: Optional[int] = None 
    ignores_accuracy: bool = False
    accuracy: Optional[int]
    pp: int
    makes_contact: bool
    move_target: str
    priority: int = 0 
    multi_hit: Optional[List[Tuple[int, float]]] = field(default_factory=list)  # Hit count mapped to probability
    stat_change: Optional[Dict[str, Dict[str, int]]] = field(default_factory=dict) # Changes stats of target/user
    status_change: Optional[str] = None 
    heals: Optional[int] = None 
    damage_heals: Optional[float] = None
    
    def __str__(self):
        """Return a string representation of the move."""
        move_info = f"{self.name} ({self.move_type} Move)\n"
        move_info += f"Info: {self.info}\n"
        if self.power is not None:
            move_info += f"Power: {self.power}, "
        move_info += f"Accuracy: {self.accuracy}%, Priority: {self.priority}\n"

        return move_info.strip()

