from morkbmt.extension import (ExtensionCommandBuilder, Converter)
from morkbmt.core import registry
from morkato.attack import AttackFlags
from morkato.utils import NoNullDict
from morkato.attack import Attack
from morkato.types import ArtType
from morkato.art import Art
from discord.interactions import Interaction
from app.extension import BaseExtension
from typing_extensions import Self
from typing import (Optional, ClassVar)
import discord.ext.commands
from enum import Enum
import app.errors
import app.embeds

class AttackChoiceIntent(Enum):
  UNAVOIDABLE = AttackFlags.UNAVOIDABLE
  INDEFENSIBLE = AttackFlags.INDEFENSIBLE
  AREA = AttackFlags.AREA
  NOT_COUNTER_ATTACKABLE = AttackFlags.NOT_COUNTER_ATTACKABLE
  COUNTER_ATTACKABLE = AttackFlags.COUNTER_ATTACKABLE
  DEFENSIVE = AttackFlags.DEFENSIVE
@registry
class RPGArtsAttacksExtension(BaseExtension):
  LANGUAGE: ClassVar[str]
  toattack: Converter[Attack]
  toart: Converter[Art]
  async def setup(self, commands: ExtensionCommandBuilder[Self]) -> None:
    self.manage_guild_perms = discord.ext.commands.has_guild_permissions(manage_guild=True)
    self.LANGUAGE = self.msgbuilder.PT_BR
    art_create = commands.app_command("art-create", self.art_create, description="[RPG Utilitários] Cria uma nova arte.")
    art_update = commands.app_command("art-update", self.art_update, description="[RPG Utilitários] Atualiza uma arte já existente.")
    attack_create = commands.app_command("attack-create", self.attack_create, description="[RPG Utilitários] Cria um novo ataque.")
    attack_update = commands.app_command("attack-update", self.attack_update, description="[RPG Utilitários] Atualiza um ataque já existente.")
    attack_delete = commands.app_command("attack-delete", self.attack_delete, description="[RPG Utilitários] Excluí um ataque.")
    attack_set_intent = commands.app_command("attack-set-intent", self.attack_set_intent, description="[RPG Utilitários] Manipula as intenções de um ataque.")
    attack_reset_intents = commands.app_command("attack-reset-intent", self.attack_reset_intents, description="[RPG Utilitários] Volta as intenções de um ataque para padrão.")
    
    commands.guild_only(art_create)
    commands.guild_only(art_update)
    commands.guild_only(attack_create)
    commands.guild_only(attack_update)
    commands.guild_only(attack_delete)
    commands.guild_only(attack_set_intent)
    commands.guild_only(attack_reset_intents)

    commands.rename(art_update, art_query="art")
    commands.rename(attack_create, art_query="art")
    commands.rename(attack_update, attack_query="attack")
    commands.rename(attack_delete, attack_query="attack")
    commands.rename(attack_set_intent, attack_query="attack")
    commands.rename(attack_reset_intents, attack_query="attack")
    
    commands.check(art_create, self.manage_guild_perms)
    commands.check(art_update, self.manage_guild_perms)
    commands.check(attack_create, self.manage_guild_perms)
    commands.check(attack_update, self.manage_guild_perms)
    commands.check(attack_delete, self.manage_guild_perms)
    commands.check(attack_set_intent, self.manage_guild_perms)
    commands.check(attack_reset_intents, self.manage_guild_perms)
  async def art_create(
    self, interaction: Interaction, /, *,
    name: str,
    type: ArtType,
    energy: Optional[int],
    life: Optional[int],
    breath: Optional[int],
    blood: Optional[int],
    description: Optional[str],
    banner: Optional[str]
  ) -> None:
    await interaction.response.defer()
    guild = await self.get_morkato_guild(interaction.guild)
    art = await guild.create_art(
      name = name,
      type = type,
      energy = energy,
      life = life,
      breath = breath,
      blood = blood,
      description = description,
      banner = banner
    )
    builder = app.embeds.ArtCreatedBuilder(art)
    await self.send_embed(interaction, builder, resolve_all=True)
  async def art_update(
    self, interaction: Interaction, /, *,
    art_query: str,
    name: Optional[str],
    type: Optional[ArtType],
    energy: Optional[int],
    life: Optional[int],
    breath: Optional[int],
    blood: Optional[int],
    description: Optional[str],
    banner: Optional[str]
  ) -> None:
    await interaction.response.defer()
    kwargs = NoNullDict(
      name = name,
      type = type,
      energy = energy,
      life = life,
      breath = breath,
      blood = blood,
      description = description,
      banner = banner
    )
    if not kwargs:
      raise app.errors.AppError("commandKwargsIsEmpty")
    guild = await self.get_morkato_guild(interaction.guild)
    art = await self.toart(art_query, arts=guild.arts)
    await art.update(**kwargs)
    builder = app.embeds.ArtUpdatedBuilder(art)
    await self.send_embed(interaction, builder, resolve_all=True)
  async def attack_create(
    self, interaction: Interaction, /, *,
    art_query: str,
    name: str,
    prefix: Optional[str],
    description: Optional[str],
    banner: Optional[str],
    wisteria_turn: Optional[int],
    poison_turn: Optional[int],
    burn_turn: Optional[int],
    bleed_turn: Optional[int],
    wisteria: Optional[int],
    poison: Optional[int],
    burn: Optional[int],
    bleed: Optional[int],
    stun: Optional[int],
    damage: Optional[int],
    breath: Optional[int],
    blood: Optional[int]
  ) -> None:
    await interaction.response.defer()
    guild = await self.get_morkato_guild(interaction.guild)
    art = await self.toart(art_query, arts=guild.arts)
    attack = await art.create_attack(
      name = name,
      name_prefix_art = prefix,
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
    builder = app.embeds.AttackCreatedBuilder(attack)
    await self.send_embed(interaction, builder, resolve_all=True)
  async def attack_update(
    self, interaction: Interaction, /, *,
    attack_query: str,
    name: Optional[str],
    prefix: Optional[str],
    description: Optional[str],
    banner: Optional[str],
    wisteria_turn: Optional[int],
    poison_turn: Optional[int],
    burn_turn: Optional[int],
    bleed_turn: Optional[int],
    wisteria: Optional[int],
    poison: Optional[int],
    burn: Optional[int],
    bleed: Optional[int],
    stun: Optional[int],
    damage: Optional[int],
    breath: Optional[int],
    blood: Optional[int]
  ) -> None:
    await interaction.response.defer()
    kwargs = NoNullDict(
      name = name,
      name_prefix_art = prefix,
      description = description,
      wisteria_turn = wisteria_turn,
      poison_turn = poison_turn,
      burn_turn = burn_turn,
      bleed_turn = bleed_turn,
      wisteria = wisteria,
      poison = poison,
      burn = burn,
      bleed = bleed,
      stun = stun,
      banner = banner,
      damage = damage,
      breath = breath,
      blood = blood
    )
    if not kwargs:
      raise app.errors.AppError("commandKwargsIsEmpty")
    guild = await self.get_morkato_guild(interaction.guild)
    attack = await self.toattack(attack_query, arts=guild.arts, attacks=guild._attacks, to_art=self.toart)
    await attack.update(**kwargs)
    builder = app.embeds.AttackUpdatedBuilder(attack)
    await self.send_embed(interaction, builder, resolve_all=True)
  async def attack_delete(self, interaction: Interaction, attack_query: str) -> None:
    await interaction.response.defer()
    guild = await self.get_morkato_guild(interaction.guild)
    attack = await self.toattack(attack_query, arts=guild.arts, attacks=guild._attacks, to_art=self.toart)
    confirm = await self.send_confirmation(interaction, content=self.msgbuilder.get_content(self.LANGUAGE, "beforeDeleteAttack", attack=attack))
    if not confirm:
      return
    await attack.delete()
    await interaction.edit_original_response(
      content=self.msgbuilder.get_content(self.LANGUAGE, "attackDelete", attack=attack),
      view=None
    )
  async def attack_set_intent(self, interaction: Interaction, attack_query: str, intent: AttackChoiceIntent) -> None:
    await interaction.response.defer()
    guild = await self.get_morkato_guild(interaction.guild)
    attack = await self.toattack(attack_query, arts=guild.arts, attacks=guild._attacks, to_art=self.toart)
    if attack.flags.hasflag(intent.value):
      raise app.errors.AppError("attackAlreadyHasIntent")
    new_flags = attack.flags.copy()
    new_flags.set(intent.value)
    await attack.update(flags=new_flags)
    builder = app.embeds.AttackUpdatedBuilder(attack)
    await self.send_embed(interaction, builder, resolve_all=True)
  async def attack_reset_intents(self, interaction: Interaction, /, *, attack_query: str) -> None:
    await interaction.response.defer()
    guild = await self.get_morkato_guild(interaction.guild)
    attack = await self.toattack(attack_query, arts=guild.arts, attacks=guild._attacks, to_art=self.toart)
    if attack.flags.isempty():
      raise app.errors.AppError("attackIntentsIsEmpty")
    await attack.update(flags=AttackFlags(0))
    builder = app.embeds.AttackUpdatedBuilder(attack)
    await self.send_embed(interaction, builder, resolve_all=True)