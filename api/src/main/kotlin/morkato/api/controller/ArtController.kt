package morkato.api.controller

import org.springframework.transaction.annotation.Transactional
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.DeleteMapping
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.PutMapping
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.context.annotation.Profile
import jakarta.validation.Valid

import morkato.api.exception.model.ArtNotFoundError
import morkato.api.exception.model.GuildNotFoundError
import morkato.api.dto.validation.IdSchema
import morkato.api.dto.art.ArtAttackResponseData
import morkato.api.dto.art.ArtResponseData
import morkato.api.dto.art.ArtCreateData
import morkato.api.dto.art.ArtUpdateData
import morkato.api.infra.repository.GuildRepository
import morkato.api.model.guild.Guild

@RestController
@RequestMapping("/arts/{guild_id}")
@Profile("api")
class ArtController {
  @GetMapping
  @Transactional
  fun findAllByGuildId(
    @PathVariable("guild_id") @IdSchema guild_id: String
  ) : List<ArtResponseData> {
    return try {
      val guild = Guild(GuildRepository.findById(guild_id))
      val attacks = guild.getAllAttacks().toMutableList()
      guild.getAllArts()
        .map { art ->
          val (valid, invalid) = attacks.partition { art.id == it.artId }
          attacks.clear()
          attacks.addAll(invalid)
          ArtResponseData(art, valid.map(::ArtAttackResponseData))
        }.toList()
    } catch (exc: GuildNotFoundError) {
      listOf()
    }
  }
  @PostMapping
  @Transactional
  fun createArtByGuild(
    @PathVariable("guild_id") @IdSchema guild_id: String,
    @RequestBody @Valid data: ArtCreateData
  ) : ArtResponseData {
    val guild = Guild(GuildRepository.findOrCreate(guild_id))
    val art = guild.createArt(
      name = data.name,
      type = data.type,
      description = data.description,
      banner = data.banner,
      energy = data.energy,
      life = data.life,
      breath = data.breath,
      blood = data.blood
    )
    return ArtResponseData(art, listOf())
  }
  @GetMapping("/{id}")
  @Transactional
  fun getReference(
    @PathVariable("guild_id") @IdSchema guild_id: String,
    @PathVariable("id") @IdSchema id: String
  ) : ArtResponseData {
    return try {
      val guild = Guild(GuildRepository.findById(guild_id))
      val art = guild.getArt(id.toLong())
      val attacks = art.getAllAttacks()
      ArtResponseData(art, attacks.map(::ArtAttackResponseData).toList())
    } catch (exc: GuildNotFoundError) {
      throw ArtNotFoundError(guild_id, id)
    }
  }
  @PutMapping("/{id}")
  @Transactional
  fun updateArtByGuild(
    @PathVariable("guild_id") @IdSchema guild_id: String,
    @PathVariable("id") @IdSchema id: String,
    @RequestBody @Valid data: ArtUpdateData
  ) : ArtResponseData {
    return try {
      val guild = Guild(GuildRepository.findById(guild_id))
      val before = guild.getArt(id.toLong())
      val art = before.update(
        name = data.name,
        type = data.type,
        description = data.description,
        banner = data.banner,
        energy = data.energy,
        life = data.life,
        breath = data.breath,
        blood = data.blood
      )
      val attacks = art.getAllAttacks()
      ArtResponseData(art, attacks.map(::ArtAttackResponseData).toList())
    } catch (exc: GuildNotFoundError) {
      throw ArtNotFoundError(guild_id, id)
    }
  }
  @DeleteMapping("/{id}")
  @Transactional
  fun deleteArtByReference(
    @PathVariable("guild_id") @IdSchema guild_id: String,
    @PathVariable("id") @IdSchema id: String
  ) : ArtResponseData {
    return try {
      val guild = Guild(GuildRepository.findById(guild_id))
      val art = guild.getArt(id.toLong())
      val attacks = art.getAllAttacks()
      ArtResponseData(art.delete(), attacks.map(::ArtAttackResponseData).toList())
    } catch (exc: GuildNotFoundError) {
      throw ArtNotFoundError(guild_id, id)
    }
  }
}
