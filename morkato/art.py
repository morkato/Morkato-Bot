from __future__ import annotations
from .utils import NoNullDict, extract_datetime_from_snowflake
from .attack import AttackIntents, Attack
from typing_extensions import Self
from datetime import datetime
from .types import (
  Art as ArtPayload,
  RespirationType,
  KekkijutsuType,
  FightingStyleType,
  ArtType
)
from typing import (
  TYPE_CHECKING,
  Optional,
  Dict,
  List
)
if TYPE_CHECKING:
  from .state import MorkatoConnectionState
  from .guild import Guild

class Art:
  RESPIRATION: RespirationType = "RESPIRATION"
  KEKKIJUTSU: KekkijutsuType = "KEKKIJUTSU"
  FIGHTING_STYLE: FightingStyleType = "FIGHTING_STYLE"
  def __init__(self, state: MorkatoConnectionState, guild: Guild, payload: ArtPayload) -> None:
    self.state = state
    self.guild = guild
    self.id = int(payload["id"])
    self.from_payload(payload)
    self.clear()
  def from_payload(self, payload: ArtPayload) -> None:
    self.name = payload["name"]
    self.type = payload["type"]
    self.description = payload["description"]
    self.banner = payload["banner"]
  def clear(self) -> None:
    self._attacks: Dict[int, Attack] = {}
  @property
  def created_at(self) -> datetime:
    return extract_datetime_from_snowflake(self)
  @property
  def updated_at(self) -> Optional[datetime]:
    if self._updated_at is not None:
      return datetime.fromtimestamp(self._updated_at / 1000.0)
    return None
  @property
  def attacks(self) -> List[Attack]:
    return sorted(self._attacks.values(), key=lambda attack: attack.id)
  def _add_attack(self, attack: Attack) -> None:
    self._attacks[attack.id] = attack
    self.guild._attacks[attack.id] = attack
  def _del_attack(self, attack: Attack) -> None:
    self._attacks.pop(attack.id, None)
    self.guild._attacks.pop(attack.id, None)
  def get_attack(self, id: int) -> Optional[Attack]:
    return self._attacks.get(id)
  async def edit(self, *, name: Optional[str] = None, type: Optional[ArtType] = None, description: Optional[str] = None, banner: Optional[str] = None) -> Self:
    kwargs = NoNullDict(
      name=name,
      type=type,
      description=description,
      banner=banner
    )
    if kwargs:
      payload = await self.state.update_art(self.guild.id, self.id, **kwargs)
      self.from_payload(payload)
    return self
  async def delete(self) -> Self:
    payload = await self.state.delete_art(self.guild.id, self.id)
    self.from_payload(payload)
    self.guild._del_art(self)
    return self
  async def create_attack(self,
    name: str, *,
    name_prefix_art: Optional[str] = None,
    description: Optional[str] = None,
    resume_description: Optional[str] = None,
    banner: Optional[str] = None,
    damage: Optional[int] = None,
    breath: Optional[int] = None,
    blood: Optional[int] = None,
    intents: Optional[AttackIntents] = None
  ) -> Attack:
    payload = await self.state.create_attack(
      self.guild.id,
      self.id,
      name=name,
      name_prefix_art=name_prefix_art,
      description=description,
      resume_description=resume_description,
      banner=banner,
      damage=damage,
      breath=breath,
      blood=blood,
      intents=intents
    )
    attack = Attack(self.state, self.guild, self, payload)
    self._add_attack(attack)
    return attack