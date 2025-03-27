from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from pokemon import Pokemon
from trainer import Trainer
from battle_simulation import pokemon_battle
from battle_test import retrieve_and_format_moves

app = FastAPI()

# ---------------------- REQUEST MODELS ---------------------- #
class PokemonRequest(BaseModel):
    name: str
    typing: List[str]
    level: int
    base_stats: Dict[str, int]
    ability: str
    nature: str
    evs: Dict[str, int]
    ivs: Dict[str, int]
    item: Dict[str, str]
    moves: List[str]  # Just move names (we retrieve details in the backend)
    status: Optional[str] = None
    accuracy: float = 1.0
    evasion: float = 1.0
    critical_hit: int = 1

class TrainerRequest(BaseModel):
    name: str
    pokemon: List[PokemonRequest]

class BattleRequest(BaseModel):
    trainer1: TrainerRequest
    trainer2: TrainerRequest

# ---------------------- API ENDPOINT ---------------------- #
@app.post("/simulate_battle/")
def simulate_battle(request: BattleRequest):
    # Convert JSON request into actual Pokémon & Trainer objects
    trainer1_pokemon = []
    for poke in request.trainer1.pokemon:
        moves = {name: retrieve_and_format_moves(name) for name in poke.moves}
        trainer1_pokemon.append(Pokemon(**poke.dict(exclude={"moves"}), moves=moves))

    trainer2_pokemon = []
    for poke in request.trainer2.pokemon:
        moves = {name: retrieve_and_format_moves(name) for name in poke.moves}
        trainer2_pokemon.append(Pokemon(**poke.dict(exclude={"moves"}), moves=moves))

    trainer1 = Trainer(request.trainer1.name, trainer1_pokemon)
    trainer2 = Trainer(request.trainer2.name, trainer2_pokemon)

    # Run battle simulation
    result = pokemon_battle(trainer1, trainer2)

    return {"battle_result": result}
