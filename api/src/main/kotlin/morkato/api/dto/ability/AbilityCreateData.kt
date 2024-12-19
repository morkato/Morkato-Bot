package morkato.api.dto.ability

import jakarta.validation.constraints.NotNull
import morkato.api.dto.validation.DescriptionSchema
import morkato.api.dto.validation.BannerSchema
import morkato.api.dto.validation.NameSchema
import java.math.BigDecimal

data class AbilityCreateData(
  @NameSchema @NotNull val name: String,
  val percent: BigDecimal?,
  val user_type: Int?,
  @DescriptionSchema val description: String?,
  @BannerSchema val banner: String?
) {}