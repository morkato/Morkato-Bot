import type { DynamicKeyValue } from 'utils'

import { ValidationError } from 'erros'

import Joi, { AnySchema } from 'joi'

import utils from 'utils'

interface KeyOption {
  option: 0 | 1
  default?: string | number | boolean | null | (string | number | boolean | null)[]
  allow?: any[] | any
}

type ChoiceKeyOption = KeyOption | 0 | 1

export default function validator<T extends any = {}>(obj: any, keys: DynamicKeyValue<ChoiceKeyOption>): T {
  try {
    obj = JSON.parse(JSON.stringify(obj))
  } catch {
    throw new ValidationError({ message: "O body tem que ser um Json.", action: "Tente enviar um Json desssa vez." })
  }
  
  const filtereKeys = utils.object.map(keys, ([key, val]) => val === 0 || val === 1 ? { option: val } : val)
  
  const schema = Joi.object(utils.object.map(filtereKeys, ([key, value]) => validators[key](value))).required().min(1)
  
  const { error, value } = schema.validate(obj)

  if(error)
    throw new ValidationError({
      message: error.details[0].message,
      key: error.details[0].context.key || error.details[0].context.type || 'object',
      errorLocationCode: 'MODEL:VALIDATOR:SCHEMA',
      type: error.details[0].type
    });
  
  return value;
}

function createFlag<T extends any>(schema: AnySchema<T>) {
  return (option: KeyOption) => {
    if(option.allow !== undefined)
      schema = schema.allow(...(option.allow instanceof Array<any> ? option.allow : [option.allow,]));
    if(option.option === 1)
      schema = schema.required();
    else if(option.default !== undefined)
      schema = schema.default(option.default);
    
    return schema;
  }
}

const validators: { [key: string]: (option: KeyOption) => Joi.AnySchema<any> } = {
  name: createFlag(Joi.string()
    .trim()
    .regex(/^[\D0-9].+$/)
    .min(2)
    .max(32)
  ),
  id: createFlag(Joi.string()
    .trim()
    .regex(/^[0-9]+$/)
  ),
  embed_title: createFlag(Joi.string()
    .trim()
    .regex(/^\D.+$/)
    .min(1)
    .max(96)
  ),
  embed_description: createFlag(Joi.string()
    .trim()
    .regex(/^\D.+$/)
    .min(1)
    .max(4096)
  ),
  embed_url: createFlag(Joi.string()
    .trim()
    .regex(/^((https?:\/\/)([\D0-9]+)|(\/[\D0-9]+))$/)
  ),
  type: createFlag(Joi.number()
    .integer()
  ),
  guild_id: (option: KeyOption) => validators.id(option),
  role: (option: KeyOption) => validators.id(option)
}


/*
  * The number 0 means that an element will be optional, while the 1 means Required.
*/

const required = (): 1 => 1
const optional = (): 0 => 0

export { validator, required, optional }