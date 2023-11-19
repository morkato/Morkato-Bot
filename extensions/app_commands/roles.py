from typing import Optional

from .views.manage_roles import MoveRoleView, colors

from random  import choice
from discord import app_commands
from morkato import (
  MorkatoBot,
  Cog,

  utils
)

import discord

class AppCommandManagerRoles(Cog):
  @app_commands.command(
    name="rinfo",
    description="[Utilitários] Mostra as informações de um certo cargo."
  )
  async def role_info(self,
    interaction: discord.Interaction,
    role:        discord.Role
  ) -> None:
    emd = discord.Embed(
      color=role.color.value
    )

    emd.add_field(name="Nome do Cargo", value=f"**`{role.name}`**", inline=False)
    emd.add_field(name="Cor do Cargo", value=f"**`rgb({role.color.r}, {role.color.g}, {role.color.b})`**", inline=False)
    emd.add_field(name="Criado em", value=f"**`{role.created_at.strftime('%a, %b %d, %y - %H:%m:%S ')}`**", inline=False)
    emd.add_field(name="ID", value=f"**`{role.id}`**", inline=False)
    emd.add_field(name="Menção", value=f"**`{'Sim' if role.mentionable else 'Não'}`** ~ **`{role.mention}`**", inline=False)
    emd.add_field(name="Posição (De Baixo para Cima)", value=f"**`{role.position}`**", inline=False)

    if role.icon:
      emd.set_thumbnail(url=role.icon.url)

    await interaction.response.send_message(embed=emd)
    
  @app_commands.command(
    name="rcreate",
    description="[Moderação] Cria um cargo."
  )
  @app_commands.choices(color=colors)
  async def role_create(self,
    interaction: discord.Interaction,
    name:        str,
    color:       Optional[app_commands.Choice[int]],
    after:       Optional[discord.Role]  
  ) -> None:
    if not interaction.guild:
      await interaction.response.send_message("Você precisa estar em um servidor.")

      return
    
    usr = interaction.user

    if not usr.guild_permissions.manage_roles:
      await interaction.response.send_message("Você não tem permissão para editar cargos.", ephemeral=True)

      return
    
    optional = {  }

    optional['color'] = color or choice(colors).value
    
    await interaction.response.defer()
    role = await interaction.guild.create_role(reason=f"@{usr.name} criou.", name=name, **optional)

    if after:
      await role.edit(position=after.position + 1)

      await interaction.edit_original_response(content=f"Um novo cargo, chamado: **`@{role.name}`** foi criado depois (De baixo para cima) do cargo: **`@{after.name}`**.")

      return

    await interaction.edit_original_response(content=f"Um novo cargo, chamado: **`@{role.name}`** foi criado.")
  
  @app_commands.command(
    name='rmove',
    description="[Moderação] Move um ou um grupo de cargos para posição de outro cargo já existente."
  )
  async def role_move(self, interaction: discord.Interaction, start: discord.Role, end: Optional[discord.Role], to: discord.Role) -> None:
    if not interaction.guild:
      await interaction.response.send_message("Você precisa estar em um servidor.")

      return
    
    usr = interaction.user

    if not usr.guild_permissions.manage_roles:
      await interaction.response.send_message("Você não tem permissão para criar cargos.", ephemeral=True)

      return
    
    if interaction.guild.self_role.position <= to.position and to.permissions.manage_roles:
      await interaction.response.send_message(f'Como vou colocar o cargos acima do **`@{to.name}`** se eu não estou acima dele?')

      return
    
    await interaction.response.defer()

    roles = [start,]

    if end and not end.id == start.id:
      checker = lambda r: utils.in_range(r.position, (start.position, end.position))

      roles = list(utils.find(interaction.guild.roles, checker))

    content = (
      f'Você está prestes a trocar a posição dos cargos entre: **`@{start.name}` à `@{end.name}`** depois do cargo: **`@{to.name}`**. Tem certeza?'
      if end
      else f'Você está prestes a trocar a posição do cargo: **`@{start.name}` depois do cargo: **`@{to.name}`**. Tem certeza?'
    )

    await interaction.edit_original_response(content=content, view=MoveRoleView(roles, to))
  
  @app_commands.command(
    name='redit',
    description="[Moderação] Edita um cargo."
  )
  @app_commands.choices(color=colors)
  async def role_edit(self,
    interaction: discord.Interaction,
    role:        discord.Role,
    name:        Optional[str],
    color:       Optional[app_commands.Choice[int]],
    after:       Optional[discord.Role]
  ) -> None:
    if not interaction.guild:
      await interaction.response.send_message("Você precisa estar em um servidor.")

      return
    
    usr = interaction.user

    if not usr.guild_permissions.manage_roles:
      await interaction.response.send_message("Você não tem permissão para editar cargos.", silent=True)

      return

    payload = {  }

    if name:
      payload['name'] = name
    
    if color:
      payload['color'] = color

    if after:
      payload['position'] = after.position if after.position != 0 else 1
    
    if not payload:
      await interaction.response.send_message("Tô ficando meio, ou tu não editou nada?")

      return
    
    original_name = role.name

    await interaction.response.defer()
    await role.edit(**payload)

    await interaction.edit_original_response(content=f"O cargo **`@{original_name}`** foi editado.")
    
async def setup(bot: MorkatoBot) -> None:
  await bot.add_cog(AppCommandManagerRoles(bot))
