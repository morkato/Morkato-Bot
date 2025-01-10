package morkato.api.infra.tables

import org.jetbrains.exposed.sql.Table

object attacks : Table("attacks") {
  val guild_id = discordSnowflakeIdType("guild_id")
  val id = idType("id").autoIncrement()

  val name = nameType("name")
  val art_id = idType("art_id")
  val name_prefix_art = namePrefixArt("name_prefix_art").nullable()
  val description = descriptionType("description").nullable()
  val required_exp = attrType("required_exp")
  val wisteria_turn = attrType("wisteria_turn")
  val poison_turn = attrType("poison_turn")
  val burn_turn = attrType("burn_turn")
  val bleed_turn = attrType("bleed_turn")
  val wisteria = attrType("wisteria")
  val poison = attrType("poison")
  val burn = attrType("burn")
  val bleed = attrType("bleed")
  val stun = attrType("stun")
  val damage = attrType("damage")
  val breath = attrType("breath")
  val blood = attrType("blood")
  val banner = text("banner").nullable()
  val flags = integer("flags")

  override val primaryKey = PrimaryKey(guild_id, id)
}