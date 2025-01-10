from __future__ import annotations
from typing import (
  TypedDict,
  Optional,
  Literal,
  List
)
RespirationType = Literal["RESPIRATION"]
KekkijutsuType = Literal["KEKKIJUTSU"]
FightingStyleType = Literal["FIGHTING_STYLE"]
ArtType = Literal[RespirationType, KekkijutsuType, FightingStyleType]
HumanType = Literal["HUMAN"]
OniType = Literal["ONI"]
HybridType = Literal["HYBRID"]
UserType = Literal[HumanType, OniType, HybridType]
class Guild(TypedDict):
  human_initial_life: int
  oni_initial_life: int
  hybrid_initial_life: int
  breath_initial: int
  blood_initial: int
  family_roll: int
  ability_roll: int
  roll_category_id: Optional[str]
  off_category_id: Optional[str]
class Art(TypedDict):
  name: str
  guild_id: str
  id: str
  type: ArtType
  life: int
  breath: int
  blood: int
  energy: int
  description: Optional[str]
  banner: Optional[str]
class ArtWithAttacks(TypedDict):
  attacks: List[Attack]
class Attack(TypedDict):
  name: str
  guild_id: str
  id: str
  art_id: str
  name_prefix_art: Optional[str]
  description: Optional[str]
  banner: Optional[str]
  wisteria_turn: int
  poison_turn: int
  burn_turn: int
  bleed_turn: int
  wisteria: int
  poison: int
  burn: int
  bleed: int
  stun: int
  damage: int
  breath: int
  blood: int
  flags: int
class Ability(TypedDict):
  guild_id: str
  id: str
  name: str
  percent: int
  user_type: int
  description: Optional[str]
  banner: Optional[str]
class Family(TypedDict):
  guild_id: str
  id: str
  name: str
  percent: int
  user_type: int
  description: Optional[str]
  banner: Optional[str]
  abilities: List[str]
class User(TypedDict):
  guild_id: str
  id: str
  type: UserType
  flags: int
  ability_roll: int
  family_roll: int
  prodigy_roll: int
  mark_roll: int
  berserk_roll: int
  abilities: List[str]
  families: List[str]