package morkato.api.model.art

import morkato.api.infra.repository.AttackRepository
import morkato.api.infra.repository.ArtRepository
import morkato.api.model.attack.Attack
import morkato.api.model.guild.Guild

import org.jetbrains.exposed.sql.ResultRow
import java.math.BigDecimal

class Art(
  val guild: Guild,
  val id: Long,
  val name: String,
  val type: ArtType,
  val description: String?,
  val banner: String?,
  val energy: BigDecimal,
  val life: BigDecimal,
  val breath: BigDecimal,
  val blood: BigDecimal
) {
  public constructor(guild: Guild, row: ResultRow) : this(guild, ArtRepository.ArtPayload(row)) {}
  public  constructor(guild: Guild, payload: ArtRepository.ArtPayload) : this(
    guild,
    payload.id,
    payload.name,
    payload.type,
    payload.description,
    payload.banner,
    payload.energy,
    payload.life,
    payload.breath,
    payload.blood
  ) {}
  fun getAllAttacks() : Sequence<Attack> {
    return AttackRepository.findAllByGuildIdAndArtId(this.guild.id, this.id)
      .map { Attack(this@Art.guild, it) }
  }
  fun createAttack(
    name: String,
    namePrefixArt: String?,
    description: String?,
    banner: String?,
    wisteriaTurn: BigDecimal?,
    poisonTurn: BigDecimal?,
    burnTurn: BigDecimal?,
    bleedTurn: BigDecimal?,
    wisteria: BigDecimal?,
    poison: BigDecimal?,
    burn: BigDecimal?,
    bleed: BigDecimal?,
    stun: BigDecimal?,
    damage: BigDecimal?,
    breath: BigDecimal?,
    blood: BigDecimal?,
    flags: Int?
  ) : Attack {
    val payload = AttackRepository.createAttack(
      guildId = this.guild.id,
      artId = this.id,
      name = name,
      namePrefixArt = namePrefixArt,
      description = description,
      banner = banner,
      wisteriaTurn = wisteriaTurn,
      poisonTurn = poisonTurn,
      burnTurn = burnTurn,
      bleedTurn = bleedTurn,
      wisteria = wisteria,
      poison = poison,
      burn = burn,
      bleed = bleed,
      stun = stun,
      damage = damage,
      breath = breath,
      blood = blood,
      flags = flags
    )
    return Attack(this.guild, payload)
  }
  fun update(
    name: String? = null,
    type: ArtType? = null,
    description: String? = null,
    banner: String? = null,
    energy: BigDecimal? = null,
    life: BigDecimal? = null,
    breath: BigDecimal? = null,
    blood: BigDecimal? = null
  ) : Art {
    val payload = ArtRepository.ArtPayload(
      guildId = this.guild.id,
      id = this.id,
      name = name ?: this.name,
      type = type ?: this.type,
      description = description ?: this.description,
      banner = banner ?: this.banner,
      energy = energy ?: this.energy,
      life = life ?: this.life,
      breath = breath ?: this.breath,
      blood = blood ?: this.blood
    )
    ArtRepository.updateArt(
      guildId = this.guild.id,
      id = this.id,
      name = name,
      type = type,
      description = description,
      banner = banner,
      energy = energy,
      life = life,
      breath = breath,
      blood = blood
    )
    return Art(this.guild, payload)
  }
  fun delete() : Art {
    ArtRepository.deleteArt(this.guild.id, this.id)
    return this
  }
}