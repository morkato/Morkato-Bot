import { makeContext, assert } from './utils'

import Joi from 'joi'

export type Attack = {
  name: string

  roles: string[]
  required_roles: number
  required_exp: number

  damage: number
  stamina: number

  embed_title: string | null
  embed_description: string | null
  embed_url: string | null

  created_at: Date
  updated_at: Date
}

export function attackSchema({ original = {}, required = {} }: {
  original?: Partial<Attack>,
  required?: Partial<Record<keyof Attack, boolean>>
}) {
  return Joi.object({
    name: makeContext(Joi.string().trim().min(1).max(32).regex(/^[^-+>@&$].+[^-+>@&$]$/), required['name'], original['name']),
  
    roles: makeContext(Joi.array().items(Joi.string().trim().regex(/^[0-9]+$/)), required['roles'], original['roles']),
    required_roles: makeContext(Joi.number().integer(), required['required_roles'], original['required_roles']),
    required_exp: makeContext(Joi.number().integer(), required['required_exp'], original['required_exp']),
  
    damage: makeContext(Joi.number().integer(), required['damage'], original['damage']),
    stamina: makeContext(Joi.number().integer(), required['stamina'], original['stamina']),
  
    embed_title: makeContext(Joi.string().allow(null).trim().min(1).max(96), required['embed_title'], original['embed_title']),
    embed_description: makeContext(Joi.string().allow(null).trim().min(1).max(4096), required['embed_description'], original['embed_description']),
    embed_url: makeContext(Joi.string().allow(null).trim(), required['embed_url'], original['embed_url']),
    
    created_at: makeContext(Joi.date().allow(Joi.string()), required['created_at'], original['created_at']),
    updated_at: makeContext(Joi.date().allow(Joi.string()), required['updated_at'], original['updated_at'])
  })
}

export default function validate<T>(obj: Record<string, unknown>, options: Parameters<typeof attackSchema>[0]) {
  return assert(attackSchema(options), obj) as T;
}

export function assertAttack(obj: Record<string, unknown>): Attack {
  return validate(obj, {
    required: {
      name: true,
      roles: true,

      required_roles: true,
      required_exp: true,

      damage: true,
      stamina: true,

      embed_title: true,
      embed_description: true,
      embed_url: true,

      created_at: true,
      updated_at: true
    }
  });
}

export function isValidAttack(obj: Record<string, unknown>): obj is Attack {
  try {
    return !!assertAttack(obj);
  } catch {
    return false;
  }
}