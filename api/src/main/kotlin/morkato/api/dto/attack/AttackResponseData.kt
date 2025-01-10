package morkato.api.dto.attack

import morkato.api.dto.validation.AttrSchema
import morkato.api.model.attack.Attack
import java.math.BigDecimal

data class AttackResponseData(
  val guild_id: String,
  val id: String,
  val name: String,
  val art_id: String,
  val name_prefix_art: String?,
  val description: String?,
  val banner: String?,
  val wisteria_turn: BigDecimal,
  val poison_turn: BigDecimal,
  val burn_turn: BigDecimal,
  val bleed_turn: BigDecimal,
  val wisteria: BigDecimal,
  val poison: BigDecimal,
  val burn: BigDecimal,
  val bleed: BigDecimal,
  val stun: BigDecimal,
  val damage: BigDecimal,
  val breath: BigDecimal,
  val blood: BigDecimal,
  val flags: Int
) {
  public constructor(attack: Attack) : this(
    attack.guild.id,
    attack.id.toString(),
    attack.name,
    attack.artId.toString(),
    attack.namePrefixArt,
    attack.description,
    attack.banner,
    attack.wisteriaTurn,
    attack.poisonTurn,
    attack.burnTurn,
    attack.bleedTurn,
    attack.wisteria,
    attack.poison,
    attack.burn,
    attack.bleed,
    attack.stun,
    attack.damage,
    attack.breath,
    attack.blood,
    attack.flags
  ) {}
}