from urllib.parse import quote
from .utils import NoNullDict
from .errors import (
  MorkatoServerError,
  UserNotFoundError,
  HTTPException,
  NotFoundError,
  ModelType
)
from typing_extensions import Self
from typing import (
  Optional,
  ClassVar,
  SupportsInt,
  Union,
  Dict,
  List,
  Any
)
from .types import (
  Ability as AbilityPayload,
  Family as FamilyPayload,
  Attack as AttackPayload,
  Guild as GuildPayload,
  User as UserPayload,
  Art as ArtPayload,
  ArtWithAttacks,
  UserType,
  ArtType
)

import logging
import asyncio
import aiohttp
import orjson
import sys
import re
import os

logger = logging.getLogger(__name__)

async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
  text = await response.text(encoding='utf-8')
  try:
    type = response.headers['Content-Type'].split(';', 1)[0]
    if type == 'application/json':
      return orjson.loads(text)
  except KeyError:
    pass
  return text
class Route:
  BASE: ClassVar[str] = os.getenv("URL", "http://localhost:5500")
  CDN_URL: ClassVar[str] = os.getenv("CDN_URL", "http://localhost:5050")
  def __init__(self, method: str, path: str, **parameters):
    self.path: str = path
    self.method: str = method
    url = self.BASE + self.path
    if parameters:
      url = url.format_map({k: quote(v) if isinstance(v, str) else v for k, v in parameters.items()})
    self.url: str = url
  @classmethod
  def from_cdn(cls, query: str, /) -> str:
    matcher = re.match(r'^cdn://([0,9]{15,30})/([^:0-9\s\/]{0,32})$', query, re.IGNORECASE)
    author_id = matcher.group(1)
    name = matcher.group(2)
    return cls.CDN_URL + "/%s/%s" % (author_id, name)
class HTTPClient:
  def __init__(
    self,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    connector: Optional[aiohttp.BaseConnector] = None
  ) -> None:
    self.loop = loop
    self.connector = connector
    self.__session: aiohttp.ClientSession = None # type: ignore
    user_agent = 'morkato (https://github.com/morkato/morkato-Bot {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
    self.user_agent: str = user_agent.format(1.0, sys.version_info, aiohttp.__version__)
  async def __aenter__(self) -> Self:
    return self
  async def __aexit__(self, *args) -> None:
    await self.close()
  async def ws_connect(self, url: str) -> aiohttp.ClientWebSocketResponse:
    kwargs = {
      'max_msg_size': 0,
      'timeout': 30.0,
      'headers': {
          'User-Agent': self.user_agent
      },
      'autoping': False
    }
    return await self.__session.ws_connect(url, **kwargs)
  async def static_login(self) -> None:
    if self.loop is None:
      self.loop = asyncio.get_running_loop()
    if self.connector is None:
      self.connector = aiohttp.TCPConnector(limit=0)
    self.__session = aiohttp.ClientSession(
      connector=self.connector
    )
  async def close(self) -> None:
    if self.__session is not None:
      await self.__session.close()
      self.__session = None # type: ignore
  async def request(self, route: Route, **kwargs) -> Any:
    if not self.__session:
      raise NotImplementedError
    headers: Dict[str, Union[str, int]] = {
      "User-Agent": self.user_agent
    }
    if "json" in kwargs:
      headers["Content-Type"] = "application/json; charset=utf-8"
      json = kwargs.pop("json")
      kwargs["data"] = orjson.dumps(json)
    kwargs["headers"] = headers
    method = route.method
    url = route.url
    for tries in range(5):
      try:
        async with self.__session.request(method, url, **kwargs) as response:
          status = response.status
          data = await json_or_text(response)
          logger.debug("%s %s retornou: %s", method, url, status)
          if status in range(200, 300):
            return data
          logger.debug("Response Data: %s", data)
          extra = data.get("extra", {})
          if status == 404:
            model_name = data["model"]
            model = ModelType[model_name]
            if model == ModelType.USER:
              raise UserNotFoundError(response, extra)
            raise NotFoundError(response, model, extra)
          elif status >= 500:
            raise MorkatoServerError(response, extra)
          raise HTTPException(response, extra)
      except OSError as err:
        if tries < 4 and err.errno in (54, 10054):
          await asyncio.sleep(1 + tries * 2)
          continue
        raise
  async def fetch_guild(self, id: int) -> GuildPayload:
    route = Route("GET", "/guilds/{id}", id=id)
    return await self.request(route)
  async def fetch_arts(self, guild_id: int) -> List[Union[ArtWithAttacks, ArtPayload]]:
    route = Route("GET", "/arts/{gid}", gid=guild_id)
    payload = await self.request(route)
    return payload
  async def fetch_user(self, guild_id: int, id: int) -> UserPayload:
    route = Route("GET", "/users/{guild_id}/{id}", guild_id=guild_id, id=id)
    return await self.request(route)
  async def fetch_families(self, guild_id: int) -> List[FamilyPayload]:
    route = Route("GET", "/families/{guild_id}", guild_id=guild_id)
    return await self.request(route)
  async def fetch_abilities(self, guild_id: int) -> List[AbilityPayload]:
    route = Route("GET", "/abilities/{guild_id}", guild_id=guild_id)
    return await self.request(route)
  async def create_art(
    self, guild_id: int, *,
    name: str,
    type: ArtType,
    energy: Optional[int] = None,
    life: Optional[int] = None,
    breath: Optional[int] = None,
    blood: Optional[int] = None,
    description: Optional[str] = None,
    banner: Optional[str] = None
  ) -> ArtPayload:
    route = Route("POST", "/arts/{gid}", gid=guild_id)
    payload = NoNullDict(
      name = name,
      type = type,
      energy = energy,
      life = life,
      breath = breath,
      blood = blood,
      description = description,
      banner = banner
    )
    return await self.request(route, json=payload)
  async def update_art(
    self, guild_id: int, id: int, *,
    name: Optional[str] = None,
    type: Optional[ArtType] = None,
    energy: Optional[int] = None,
    life: Optional[int] = None,
    breath: Optional[int] = None,
    blood: Optional[int] = None,
    description: Optional[str] = None,
    banner: Optional[str] = None
  ) -> Union[ArtPayload, ArtWithAttacks]:
    route = Route("PUT", "/arts/{guild_id}/{id}", guild_id=guild_id, id=id)
    payload = NoNullDict(
      name = name,
      type = type,
      energy = energy,
      life = life,
      breath = breath,
      blood = blood,
      description = description,
      banner = banner
    )
    payload = await self.request(route, json=payload)
    return payload
  async def delete_art(self, guild_id: int, id: int) -> Union[ArtWithAttacks, ArtPayload]:
    route = Route("DELETE", "/arts/{guild_id}/{id}", guild_id=guild_id, id=id)
    return await self.request(route)
  async def create_attack(
    self, guild_id: int, art_id: int, *,
    name: str,
    name_prefix_art: Optional[str] = None,
    description: Optional[str] = None,
    banner: Optional[str] = None,
    wisteria_turn: Optional[str] = None,
    poison_turn: Optional[int] = None,
    burn_turn: Optional[int] = None,
    bleed_turn: Optional[int] = None,
    wisteria: Optional[int] = None,
    poison: Optional[int] = None,
    burn: Optional[int] = None,
    bleed: Optional[int] = None,
    stun: Optional[int] = None,
    damage: Optional[int] = None,
    breath: Optional[int] = None,
    blood: Optional[int] = None,
    flags: Optional[SupportsInt] = None
  ) -> AttackPayload:
    route = Route("POST", "/attacks/{guild_id}/{art_id}", guild_id=guild_id, art_id=art_id)
    payload = NoNullDict(
      name = name,
      name_prefix_art = name_prefix_art,
      description = description,
      banner = banner,
      wisteria_turn = wisteria_turn,
      poison_turn = poison_turn,
      burn_turn = burn_turn,
      bleed_turn = bleed_turn,
      wisteria = wisteria,
      poison = poison,
      burn = burn,
      bleed = bleed,
      stun = stun,
      damage = damage,
      breath = breath,
      blood = blood
    )
    if flags is not None:
      payload.update(flags=int(flags))
    return await self.request(route, json=payload)
  async def update_attack(
    self, guild_id: int, id: int, *,
    name: Optional[str] = None,
    name_prefix_art: Optional[str] = None,
    description: Optional[str] = None,
    banner: Optional[str] = None,
    wisteria_turn: Optional[int] = None,
    poison_turn: Optional[int] = None,
    burn_turn: Optional[int] = None,
    bleed_turn: Optional[int] = None,
    wisteria: Optional[int] = None,
    poison: Optional[int] = None,
    burn: Optional[int] = None,
    bleed: Optional[int] = None,
    stun: Optional[int] = None,
    damage: Optional[int] = None,
    breath: Optional[int] = None,
    blood: Optional[int] = None,
    flags: Optional[SupportsInt] = None
  ) -> AttackPayload:
    route = Route("PUT", "/attacks/{guild_id}/{id}", guild_id=guild_id, id=id)
    payload = NoNullDict(
      name = name,
      name_prefix_art = name_prefix_art,
      description = description,
      banner = banner,
      wisteria_turn = wisteria_turn,
      poison_turn = poison_turn,
      burn_turn = burn_turn,
      bleed_turn = bleed_turn,
      wisteria = wisteria,
      poison = poison,
      burn = burn,
      bleed = bleed,
      stun = stun,
      damage = damage,
      breath = breath,
      blood = blood
    )
    if flags is not None:
      payload.update(flags=int(flags))
    return await self.request(route, json=payload)
  async def delete_attack(self, guild_id: int, id: int) -> AttackPayload:
    route = Route("DELETE", "/attacks/{guild_id}/{id}", guild_id=guild_id, id=id)
    return await self.request(route)
  async def create_user(
    self, guild_id: int, id: int, *,
    type: UserType,
    flags: Optional[int] = None,
    ability_roll: Optional[int] = None,
    family_roll: Optional[int] = None,
    prodigy_roll: Optional[int] = None,
    mark_roll: Optional[int] = None,
    berserk_roll: Optional[int] = None
  ) -> UserPayload:
    route = Route("POST", "/users/{guild_id}/{id}", guild_id=guild_id, id=id)
    payload = NoNullDict(
      type = type,
      flags = flags,
      ability_roll = ability_roll,
      family_roll = family_roll,
      prodigy_roll = prodigy_roll,
      mark_roll = mark_roll,
      berserk_roll = berserk_roll
    )
    return await self.request(route, json=payload)
  async def update_user(
    self, guild_id: int, id: int, *,
    flags: Optional[int] = None,
    ability_roll: Optional[int] = None,
    family_roll: Optional[int] = None,
    prodigy_roll: Optional[int] = None,
    mark_roll: Optional[int] = None,
    berserk_roll: Optional[int] = None
  ) -> UserPayload:
    route = Route("PUT", "/users/{guild_id}/{id}", guild_id=guild_id, id=id)
    payload = NoNullDict(
      flags = flags,
      ability_roll = ability_roll,
      family_roll = family_roll,
      prodigy_roll = prodigy_roll,
      mark_roll = mark_roll,
      berserk_roll = berserk_roll
    )
    return await self.request(route, json=payload)
  async def delete_user(self, guild_id: int, id: int) -> UserPayload:
    route = Route("DELETE", "/users/{guild_id}/{id}", guild_id=guild_id, id=id)
    return await self.request(route)
  async def create_ability(
    self, guild_id: int, *,
    name: str,
    percent: Optional[int],
    user_type: Optional[SupportsInt],
    description: Optional[str] = None,
    banner: Optional[str] = None
  ) -> AbilityPayload:
    route = Route("POST", "/abilities/{guild_id}", guild_id=guild_id)
    payload = NoNullDict(
      name = name,
      percent = percent,
      user_type = int(user_type) if user_type is not None else None,
      description = description,
      banner = banner
    )
    return await self.request(route, json=payload)
  async def update_ability(
    self, guild_id: int, id: int, *,
    name: Optional[str] = None,
    percent: Optional[int] = None,
    user_type: Optional[SupportsInt] = None,
    description: Optional[str] = None,
    banner: Optional[str] = None
  ) -> AbilityPayload:
    route = Route("PUT", "/abilities/{guild_id}/{id}", guild_id=guild_id, id=id)
    payload = NoNullDict(
      name = name,
      percent = percent,
      description = description,
      banner = banner
    )
    if user_type is not None:
      payload.update(user_type=int(user_type))
    return await self.request(route, json=payload)
  async def delete_ability(self, guild_id: int, id: int) -> AbilityPayload:
    route = Route("DELETE", "/abilities/{guild_id}/{id}", guild_id=guild_id, id=id)
    return await self.request(route)
  async def create_family(
    self, guild_id: int, *,
    name: str,
    percent: Optional[int] = None,
    user_type: Optional[SupportsInt] = None,
    description: Optional[str] = None,
    banner: Optional[str] = None
  ) -> FamilyPayload:
    route = Route("POST", "/families/{guild_id}", guild_id=guild_id)
    payload = NoNullDict(
      name = name,
      percent = percent,
      description = description,
      banner = banner
    )
    if user_type is not None:
      payload.update(user_type=int(user_type))
    return await self.request(route, json=payload)
  async def update_family(
    self, guild_id: int, id: int, *,
    name: Optional[str] = None,
    user_type: Optional[SupportsInt] = None,
    percent: Optional[int] = None,
    description: Optional[str] = None,
    banner: Optional[str] = None
  ) -> FamilyPayload:
    route = Route("PUT", "/families/{guild_id}/{id}", guild_id=guild_id, id=id)
    payload = NoNullDict(
      name = name,
      percent = percent,
      description = description,
      banner = banner
    )
    if user_type is not None:
      payload.update(user_type=int(user_type))
    return await self.request(route, json=payload)
  async def delete_family(self, guild_id: int, id: int) -> FamilyPayload:
    route = Route("DELETE", "/families/{guild_id}/{id}", guild_id=guild_id, id=id)
    return await self.request(route)
  async def upload_image(
    self, image: bytes, *,
    author_id: int,
    name: str
  ) -> None:
    route = Route("POST", "/cdn/upload")
    headers = bytes()
    headers += author_id.to_bytes(8, byteorder='big')
    headers += len(name).to_bytes(4, byteorder='big')
    headers += name.encode('utf8')
    content = headers + image
    await self.request(route, data=content)
  async def registry_user_ability(self, guild_id: int, user_id: int, ability_id: int) -> UserPayload:
    route = Route("POST", "/users/{guild_id}/{user_id}/abilities/{ability_id}", guild_id=guild_id, user_id=user_id, ability_id=ability_id)
    return await self.request(route)
  async def registry_user_family(self, guild_id: int, user_id: int, family_id: int) -> UserPayload:
    route = Route("POST", "/users/{guild_id}/{user_id}/families/{family_id}", guild_id=guild_id, user_id=user_id, family_id=family_id)
    return await self.request(route)