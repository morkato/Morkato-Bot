package morkato.api.dto.attack

import morkato.api.dto.validation.NamePrefixArtSchema
import morkato.api.dto.validation.DescriptionSchema
import morkato.api.dto.validation.NameSchema
import morkato.api.dto.validation.BannerSchema
import morkato.api.dto.validation.AttrSchema
import java.math.BigDecimal

data class AttackUpdateData(
  @NameSchema val name: String?,
  @NamePrefixArtSchema val name_prefix_art: String?,
  @DescriptionSchema val description: String?,
  @BannerSchema val banner: String?,
  @AttrSchema val wisteria_turn: BigDecimal?,
  @AttrSchema val poison_turn: BigDecimal?,
  @AttrSchema val burn_turn: BigDecimal?,
  @AttrSchema val bleed_turn: BigDecimal?,
  @AttrSchema val wisteria: BigDecimal?,
  @AttrSchema val poison: BigDecimal?,
  @AttrSchema val burn: BigDecimal?,
  @AttrSchema val bleed: BigDecimal?,
  @AttrSchema val stun: BigDecimal?,
  @AttrSchema val damage: BigDecimal?,
  @AttrSchema val breath: BigDecimal?,
  @AttrSchema val blood: BigDecimal?,
  val flags: Int?
) {}
